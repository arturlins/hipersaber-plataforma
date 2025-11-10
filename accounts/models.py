import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings  # <-- IMPORT ADICIONADO


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


# ENUM: Tipos de Usuário
class RoleChoices(models.TextChoices):
    GUARDIAN = 'guardian', 'Responsável'
    ADMIN = 'admin', 'Administrador'
    SUPERUSER = 'superuser', 'Superusuário'


# Criar um Usuário (User) - baseado no role
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password, **extra_fields):
        if not email:
            raise ValueError("O Email é obrigatório")

        role = extra_fields.get('role', RoleChoices.GUARDIAN)
        # Criar um Usuário tipo Responsável (Guardian)
        if role == RoleChoices.GUARDIAN:
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
        # Criar um Usuário tipo Administrador (Admin)
        elif role == RoleChoices.ADMIN:
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', False)
        # Criar um Usuário tipo Superusuário (Superuser)  
        elif role == RoleChoices.SUPERUSER:
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)  # HASH da senha
        user.save(using=self._db)

        return user

    # Criar um Superusuário
    def create_superuser(self, email, full_name, password, **extra_fields):
        extra_fields.setdefault('role', RoleChoices.SUPERUSER)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('agreed_to_terms', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(email, full_name, password, **extra_fields)


# Modelo abstrato do 'User' (antigo Guardian) como usuário customizado (AUTH_USER_MODEL)
class User(AbstractBaseUser, PermissionsMixin): # <-- CLASSE RENOMEADA
    id = models.BigAutoField(primary_key=True) # PK bigserial
    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs."
    )
    email = models.EmailField(
        max_length=200, 
        unique=True, 
        help_text="Email usado para login."
    )
    full_name = models.CharField(
        max_length=300, 
        help_text="Nome completo do usuário."
    )
    agreed_to_terms = models.BooleanField(
        default=False,
        help_text="Indica se o usuário concordou com os termos de uso."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.GUARDIAN,
        help_text="Papel do usuário no sistema."
    )
    objects = UserManager() # Usa o novo Manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Usuário' # Nome amigável
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


# Modelo do 'Student' (Aluno)
class Student(models.Model):
    id = models.BigAutoField(primary_key=True)  # PK bigserial
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Boa prática: usar settings.AUTH_USER_MODEL
        on_delete=models.CASCADE, 
        related_name='students',  
        help_text="Responsável (Usuário) vinculado a este aluno."
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
        # <-- REFERÊNCIA CORRIGIDA de 'guardian' para 'user'
        return f"{self.nickname} (Responsável: {self.user.email})"


# --- PROXY MODELS PARA O ADMIN ---
# Estas classes NÃO criam novas tabelas.
# Elas apenas criam "visualizações" do modelo 'User' para o painel admin.

# Proxy Model para filtrar e mostrar apenas Usuários com 'role' de GUARDIAN.
class GuardianUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'


# Proxy Model para filtrar e mostrar apenas Usuários com 'role' de ADMIN.
class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'


# Proxy Model para filtrar e mostrar apenas Usuários com 'role' de SUPERUSER.
class SuperuserUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Superusuário'
        verbose_name_plural = 'Superusuários'