import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# ENUM: Tipos de TDAH
class AdhdTypeChoices(models.TextChoices):
    DESATENTO = "desatento", "Desatento"
    HIPERATIVO_IMPULSIVO = "hiperativo_impulsivo", "Hiperativo/Impulsivo"
    COMBINADO = "combinado", "Combinado"
    NAO_INFORMADO = "nao_informado", "Não Informado"


# ENUM: Ano escolar
class SchoolYearChoices(models.TextChoices):
    ANO_1 = "ano_1", "1º Ano"
    ANO_2 = "ano_2", "2º Ano"
    ANO_3 = "ano_3", "3º Ano"
    ANO_4 = "ano_4", "4º Ano"
    ANO_5 = "ano_5", "5º Ano"
    ANO_6 = "ano_6", "6º Ano"
    ANO_7 = "ano_7", "7º Ano"
    ANO_8 = "ano_8", "8º Ano"
    ANO_9 = "ano_9", "9º Ano"


# Criar um Responsável (Guardian) - tipo usuário
class GuardianManager(BaseUserManager):
    def create_user(self, email, full_name, password, **extra_fields):
        if not email:
            raise ValueError("O Email é obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)  # Isso faz o HASH da senha
        user.save(using=self._db)
        return user

    # Criar um Admin
    def create_superuser(self, email, full_name, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("agreed_to_terms", True)  # Superuser já concorda

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


# Modelo abstrato do 'Guardian' (Responsável) como usuário customizado (AUTH_USER_MODEL)
class Guardian(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,  # Adiciona um índice para buscas rápidas
        help_text="ID público para ser usado em URLs e APIs.",
    )
    email = models.EmailField(
        max_length=200, unique=True, help_text="Email usado para login."
    )
    full_name = models.CharField(
        max_length=300, help_text="Nome completo do responsável."
    )
    agreed_to_terms = models.BooleanField(
        default=False, help_text="Indica se o usuário concordou com os termos de uso."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)  # Permite acesso ao Admin
    is_active = models.BooleanField(default=True)  # Usuário ativo
    objects = GuardianManager()  # Define o Manager que criamos
    USERNAME_FIELD = "email"  # Define 'email' como o campo de login
    REQUIRED_FIELDS = ["full_name"]  # Campos pedidos ao criar superuser

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"

    def __str__(self):
        return self.email


# Modelo do 'Student' (Aluno) como usuário customizado (AUTH_USER_MODEL)
class Student(models.Model):
    id = models.BigAutoField(primary_key=True)  # PK bigserial
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,  # Se deletar o Responsável, deleta o Aluno
        related_name="students",  # Permite fazer guardian.students.all()
        help_text="Responsável vinculado a este aluno.",
    )
    nickname = models.CharField(max_length=300, help_text="Nome ou apelido do aluno.")
    birth_date = models.DateField(
        null=True,
        blank=True,  # Permite que o campo seja nulo
        help_text="Data de Nascimento.",
    )
    school_year = models.CharField(
        max_length=10,
        choices=SchoolYearChoices.choices,
        help_text="Ano escolar do aluno.",
    )
    adhd_type = models.CharField(
        max_length=20,
        choices=AdhdTypeChoices.choices,
        default=AdhdTypeChoices.NAO_INFORMADO,
        help_text="Tipo de TDAH do aluno.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self):
        return f"{self.nickname} (Responsável: {self.guardian.email})"
