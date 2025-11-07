from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, LessonProgress, Material, Subtitle

# --- Configuração Avançada para Cursos, Módulos e Lições ---


# Permite editar Lições (Lessons) diretamente de dentro do admin do Módulo (Module)
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1  # Quantos formulários de lição em branco mostrar


# Permite editar Módulos (Modules) diretamente de dentro do admin do Curso (Course)
class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1  # Quantos formulários de módulo em branco mostrar
    inlines = [LessonInline]  # Aninhamento: Lições dentro de Módulos


# Configuração personalizada para o modelo Curso no admin.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "published_at", "created_at")
    list_filter = ("audience", "published_at")
    search_fields = ("title", "description")
    inlines = [
        ModuleInline
    ]  # Permite criar Módulos (e Lições) dentro da página do Curso
    readonly_fields = (
        "public_id",
    )  # Preenche o 'public_id' automaticamente (não editável)


# Configuração personalizada para o modelo Módulo no admin (Usado se você clicar em um Módulo separadamente)
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "module_order")
    list_filter = ("course",)
    search_fields = ("title",)
    inlines = [LessonInline]
    readonly_fields = ("public_id",)


# Configuração personalizada para o modelo Material no admin
class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1 # Mostra 1 slot de upload em branco


# Configuração personalizada para o modelo Legenda no admin
class SubtitleInline(admin.TabularInline):
    model = Subtitle
    extra = 1 # Mostra 1 slot de upload em branco


# Configuração personalizada para o modelo Lição no admin
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "lesson_type", "lesson_order")
    list_filter = ("module__course", "lesson_type")  # Filtra por curso ou tipo
    search_fields = ("title", "content")
    readonly_fields = ("public_id",)
    inlines = [MaterialInline, SubtitleInline]


# --- Configuração Simples para Matrículas e Progresso ---


# Configuração personalizada para o modelo Matrícula no admin
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "completed_at")
    list_filter = ("course",)
    search_fields = (
        "student__nickname",
        "course__title",
    )  # Busca por nome do aluno ou curso
    readonly_fields = ("public_id", "enrolled_at")


# Configuração personalizada para o modelo Progresso de Lição no admin
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "completed_at")
    list_filter = ("lesson__module__course",)  # Filtra pelo curso
    search_fields = ("student__nickname", "lesson__title")
    readonly_fields = ("public_id", "completed_at")

