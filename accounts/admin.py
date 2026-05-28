# Em /accounts/admin.py

from django.contrib import admin
from .models import User, Student, RoleChoices, GuardianUser, AdminUser, SuperuserUser

# -----------------
# ADMIN DO ALUNO
# -----------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'user', 'school_year')
    search_fields = ('nickname', 'user__email')

# -----------------
# ADMINS DOS USUÁRIOS (POR PAPEL)
# -----------------

# Esta classe base será usada por todos os admins de usuário
class UserAdminBase(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_superuser')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    
    # Esconde os campos de permissão que estamos controlando via 'role'
    # para evitar que um admin mude um 'guardian' para 'staff' manualmente.
    exclude = ('is_staff', 'is_superuser')

    # Sobrescreve o 'save_model' para forçar o 'role' correto
    # com base no admin que está sendo usado.
    def save_model(self, request, obj, form, change):
        if obj.role == RoleChoices.GUARDIAN:
            obj.is_staff = False
            obj.is_superuser = False
        elif obj.role == RoleChoices.ADMIN:
            obj.is_staff = True
            obj.is_superuser = False
        elif obj.role == RoleChoices.SUPERUSER:
            obj.is_staff = True
            obj.is_superuser = True
        super().save_model(request, obj, form, change)

@admin.register(GuardianUser)
class GuardianUserAdmin(UserAdminBase):
    def get_queryset(self, request):
        # Filtra a lista para mostrar APENAS 'guardian'
        return User.objects.filter(role=RoleChoices.GUARDIAN)

    def get_changeform_initial_data(self, request):
        # Define 'guardian' como padrão ao criar um novo
        return {'role': RoleChoices.GUARDIAN}

@admin.register(AdminUser)
class AdminUserAdmin(UserAdminBase):
    def get_queryset(self, request):
        # Filtra a lista para mostrar APENAS 'admin'
        return User.objects.filter(role=RoleChoices.ADMIN)

    def get_changeform_initial_data(self, request):
        # Define 'admin' como padrão ao criar um novo
        return {'role': RoleChoices.ADMIN}

@admin.register(SuperuserUser)
class SuperuserUserAdmin(UserAdminBase):
    def get_queryset(self, request):
        # Filtra a lista para mostrar APENAS 'superuser'
        return User.objects.filter(role=RoleChoices.SUPERUSER)

    def get_changeform_initial_data(self, request):
        # Define 'superuser' como padrão ao criar um novo
        return {'role': RoleChoices.SUPERUSER}