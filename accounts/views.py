from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
import uuid
from accounts.models import User, Student, SchoolYearChoices, AdhdTypeChoices, RoleChoices
from learning.models import Enrollment
from accounts.models import PasswordResetToken

def home(request):
    return render(request, "accounts/home.html")

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "")
        # Controle de tentativas: não bloquear antes de tentar autenticar
        lock_key = f"lock:{email}"
        fail_key = f"fail:{email}"
        user = authenticate(request, username=email, password=senha)
        if user is None:
            manual = User.objects.filter(email__iexact=email).first()
            if manual and manual.check_password(senha):
                user = manual
        if user is not None:
            login(request, user)
            # Manter-me conectado
            keep = request.POST.get("manter-conectado") == "on"
            if keep:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dias
            else:
                request.session.set_expiry(60 * 60 * 6)  # 6 horas
            cache.delete(fail_key)
            cache.delete(lock_key)
            return redirect("dashboard_responsavel")
        # falha: incrementa contador
        fails = cache.get(fail_key, 0) + 1
        cache.set(fail_key, fails, 60 * 60)  # contador expira em 1h
        if fails >= 5:
            cache.set(lock_key, True, 60 * 30)  # bloqueia por 30 min
        return render(request, "accounts/login.html", {"error_type": "error", "error_message": "E-mail ou senha inválidos. Por favor, tente novamente ou faça o cadastro", "show_error_modal": True})
    return render(request, "accounts/login.html")

@require_http_methods(["GET", "POST"])
def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("responsavel_nome", "").strip()
        email = request.POST.get("responsavel_email", "").strip()
        senha = request.POST.get("responsavel_senha", "")
        confirma = request.POST.get("responsavel_confirma_senha", "")
        termos = request.POST.get("termos") == "on"

        errors = {}
        if len(nome) < 3:
            errors["responsavel_nome"] = "O nome deve conter pelo menos 3 caracteres."
        if not _valid_email(email):
            errors["responsavel_email"] = "Insira um e-mail válido."
        if not _valid_password(senha):
            errors["responsavel_senha"] = "A senha não atende aos requisitos de segurança."
        if senha != confirma:
            errors["responsavel_confirma_senha"] = "As senhas não conferem."
        if not termos:
            errors["termos"] = "É necessário aceitar os Termos e a Política de Privacidade."
        if errors:
            return render(request, "accounts/cadastro_responsavel.html", {"errors": errors, "values": {"responsavel_nome": nome, "responsavel_email": email}})

        try:
            with transaction.atomic():
                user = User.objects.create_user(email=email, full_name=nome, password=senha, role=RoleChoices.GUARDIAN, agreed_to_terms=True)
            login(request, user)
            return redirect("cadastro_aluno")
        except IntegrityError:
            errors = {"responsavel_email": "E-mail já cadastrado no sistema, use a página de login para acessar."}
            return render(request, "accounts/cadastro_responsavel.html", {"errors": errors, "values": {"responsavel_nome": nome, "responsavel_email": email}})
    return render(request, "accounts/cadastro_responsavel.html")

@login_required
@require_http_methods(["GET", "POST"])
def cadastro_aluno_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        nickname = request.POST.get("nome_aluno", "").strip()
        ano = request.POST.get("ano_escolar")
        tipo_tdah = request.POST.get("tipo_tdah", AdhdTypeChoices.NAO_INFORMADO)
        birth_date_str = request.POST.get("data_nascimento") or None
        from datetime import date
        birth_date = None
        if birth_date_str:
            try:
                birth_date = date.fromisoformat(birth_date_str)
            except Exception:
                birth_date = None

        initial = {"nome_aluno": nickname, "ano_escolar": ano, "tipo_tdah": tipo_tdah, "data_nascimento": birth_date_str or ""}
        errors = {}
        if len(nickname) < 3:
            errors["nome_aluno"] = "O nome ou apelido do aluno deve ter ao menos 3 caracteres."
        if ano not in dict(SchoolYearChoices.choices):
            errors["ano_escolar"] = "Selecione o ano escolar."
        if tipo_tdah not in dict(AdhdTypeChoices.choices):
            errors["tipo_tdah"] = "Selecione o tipo de TDAH."
        if errors:
            return render(request, "accounts/cadastrar_aluno.html", {"errors": errors, "initial": initial})

        try:
            with transaction.atomic():
                student = Student.objects.create(
                    user=request.user,
                    nickname=nickname,
                    school_year=ano,
                    adhd_type=tipo_tdah,
                    birth_date=birth_date,
                )
        except Exception:
            return render(request, "accounts/cadastrar_aluno.html", {"error_message": "Não foi possível cadastrar o aluno.", "initial": initial})

        if action == "adicionar_outro":
            return render(request, "accounts/cadastrar_aluno.html", {"success_message": f"Aluno(a) '{student.nickname}' adicionado com sucesso!", "initial": {}})
        return redirect("dashboard_responsavel")
    return render(request, "accounts/cadastrar_aluno.html")

@login_required
def dashboard_responsavel_view(request):
    students = request.user.students.all()
    return render(request, "accounts/dashboard_responsavel.html", {"students": students})

@login_required
@require_http_methods(["GET", "POST"])
def meus_dados_view(request):
    context = {}
    if request.method == "POST":
        # handled via separate endpoints
        pass
    students = request.user.students.all()
    context["students"] = students
    return render(request, "accounts/meus_dados.html", context)

@login_required
@require_http_methods(["POST"])
def atualizar_perfil_view(request):
    full_name = request.POST.get("full_name", "").strip()
    email = request.POST.get("email", "").strip()
    field_errors = {}
    if len(full_name) < 3:
        field_errors["profile_error_full_name"] = "O nome deve conter pelo menos 3 caracteres."
    if not _valid_email(email):
        field_errors["profile_error_email"] = "Insira um e-mail válido."
    if field_errors:
        return _render_meus_dados(request, **field_errors)
    try:
        request.user.full_name = full_name
        request.user.email = email
        request.user.save()
    except IntegrityError:
        return _render_meus_dados(request, profile_error_email="Este e-mail já está em uso. Por favor, utilize outro.")
    return _render_meus_dados(request, profile_message="Dados atualizados com sucesso.")

@login_required
@require_http_methods(["POST"])
def atualizar_senha_view(request):
    current = request.POST.get("current_password", "")
    new = request.POST.get("new_password", "")
    confirm = request.POST.get("confirm_password", "")
    if not request.user.check_password(current):
        return _render_meus_dados(request, password_error_current="A senha atual está incorreta. Tente novamente")
    if not _valid_password(new):
        return _render_meus_dados(request, password_error_password="A senha deve conter ao menos 8 caracteres, com maiúscula, minúscula, número e símbolo (@#$%&*).")
    if new != confirm:
        return _render_meus_dados(request, password_error_confirm="As senhas não conferem.")
    request.user.set_password(new)
    request.user.save()
    return _render_meus_dados(request, password_message="Senha atualizada com sucesso.")

@login_required
@require_http_methods(["POST"])
def remover_aluno_view(request, public_id):
    student = Student.objects.filter(public_id=public_id, user=request.user).first()
    total = request.user.students.count()
    if total <= 1:
        return _render_meus_dados(request, students_error="Não é possível remover este perfil. Sua conta deve ter pelo menos um Aluno cadastrado")
    if student:
        student.delete()
    return redirect("meus_dados")

@login_required
@require_http_methods(["GET", "POST"])
def editar_aluno_view(request, public_id):
    student = Student.objects.filter(public_id=public_id, user=request.user).first()
    if not student:
        return redirect("meus_dados")
    if request.method == "POST":
        nickname = request.POST.get("nome_aluno", "").strip()
        ano = request.POST.get("ano_escolar")
        tipo_tdah = request.POST.get("tipo_tdah", AdhdTypeChoices.NAO_INFORMADO)
        birth_date_str = request.POST.get("data_nascimento") or None
        from datetime import date
        birth_date = None
        if birth_date_str:
            try:
                birth_date = date.fromisoformat(birth_date_str)
            except Exception:
                birth_date = None
        if len(nickname) < 3:
            return render(request, "accounts/cadastrar_aluno.html", {"error_message": "O nome ou apelido do aluno deve ter ao menos 3 caracteres.", "initial": {"nome_aluno": nickname, "ano_escolar": ano, "tipo_tdah": tipo_tdah, "data_nascimento": birth_date}})
        if ano not in dict(SchoolYearChoices.choices):
            return render(request, "accounts/cadastrar_aluno.html", {"error_message": "O ano escolar do aluno é obrigatório.", "initial": {"nome_aluno": nickname, "ano_escolar": ano, "tipo_tdah": tipo_tdah, "data_nascimento": birth_date}})
        if tipo_tdah not in dict(AdhdTypeChoices.choices):
            return render(request, "accounts/cadastrar_aluno.html", {"error_message": "A seleção do tipo de TDAH é obrigatória.", "initial": {"nome_aluno": nickname, "ano_escolar": ano, "tipo_tdah": tipo_tdah, "data_nascimento": birth_date}})
        student.nickname = nickname
        student.school_year = ano
        student.adhd_type = tipo_tdah
        student.birth_date = birth_date
        student.save()
        return redirect("meus_dados")
    initial = {"nome_aluno": student.nickname, "ano_escolar": student.school_year, "tipo_tdah": student.adhd_type, "data_nascimento": student.birth_date and student.birth_date.isoformat() or ""}
    return render(request, "accounts/cadastrar_aluno.html", {"initial": initial, "form_action": f"/aluno/editar/{public_id}/", "is_edit": True})

def _render_meus_dados(request, **messages_ctx):
    students = request.user.students.all()
    ctx = {"students": students}
    ctx.update(messages_ctx)
    return render(request, "accounts/meus_dados.html", ctx)

@login_required
@require_http_methods(["POST"])
def excluir_conta_view(request):
    from django.contrib.auth import logout
    password = request.POST.get("current_password", "")
    if not request.user.check_password(password):
        return _render_meus_dados(request, account_delete_error="A senha está incorreta. A exclusão não foi realizada.")
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "Sua conta e todos os seus dados foram excluídos com sucesso.")
    return redirect("home")

@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return redirect("home")

def _valid_email(email: str) -> bool:
    import re
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email))

def _valid_password(pw: str) -> bool:
    import re
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", pw))

@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not _valid_email(email):
            return render(request, "accounts/recuperar_senha_solicitar.html", {"error_message": "Insira um e-mail válido.", "value_email": email})
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return render(request, "accounts/recuperar_senha_solicitar.html", {"error_message": "E-mail não cadastrado no sistema. Por favor, verifique ou faça o cadastro.", "value_email": email})
        token = PasswordResetToken.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=15))
        reset_link = request.build_absolute_uri(f"/redefinir-senha/{token.token}/")
        send_mail(
            subject="Redefinição de Senha - HiperSaber",
            message=f"Olá,\n\nPara redefinir sua senha, acesse: {reset_link}\n\nEste link expira em 15 minutos.",
            from_email=None,
            recipient_list=[user.email],
        )
        return render(request, "accounts/recuperar_senha_solicitar.html", {"success_message": True, "value_email": email})
    return render(request, "accounts/recuperar_senha_solicitar.html")

@require_http_methods(["GET", "POST"])
def reset_password_view(request, token):
    prt = PasswordResetToken.objects.filter(token=token).first()
    if not prt or prt.used_at or prt.expires_at < timezone.now():
        return render(request, "accounts/recuperar_senha_redefinir.html", {"invalid_token": True})
    user = prt.user
    if request.method == "POST":
        new = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")
        if new != confirm:
            return render(request, "accounts/recuperar_senha_redefinir.html", {"error_confirm": "As senhas não conferem."})
        if not _valid_password(new):
            return render(request, "accounts/recuperar_senha_redefinir.html", {"error_password": "A senha deve atender aos requisitos de segurança."})
        if user.check_password(new):
            return render(request, "accounts/recuperar_senha_redefinir.html", {"error_password": "A nova senha não pode ser idêntica à anterior."})
        user.set_password(new)
        user.save()
        prt.used_at = timezone.now()
        prt.save()
        return redirect("login")
    return render(request, "accounts/recuperar_senha_redefinir.html")
