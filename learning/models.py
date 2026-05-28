import uuid
from django.db import models
from django.conf import settings  # Boa prática para referenciar o AUTH_USER_MODEL
from accounts.models import Student


# ENUM tipo de aula
class LessonTypeChoices(models.TextChoices):
    VIDEO = "video", "Vídeo"
    TEXT = "text", "Texto"
    QUIZ = "quiz", "Quiz"


# Modelo: Cursos da plataforma
class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    title = models.CharField(max_length=255, help_text="Título do curso.")
    description = models.TextField(
        null=True, blank=True, help_text="Descrição detalhada do curso."
    )
    thumbnail_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        help_text="URL para a imagem de capa (thumbnail).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.title


# Modelo: módulos do curso
class Module(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,  # Se deletar o Curso, deleta o Módulo
        related_name="modules",  # Permite fazer course.modules.all()
        help_text="Curso ao qual este módulo pertence.",
    )
    title = models.CharField(max_length=255, help_text="Título do módulo.")
    module_order = models.IntegerField(
        help_text="Ordem do módulo dentro do curso (1, 2, 3...)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        unique_together = (
            "course",
            "module_order",
        )  # Garante que a ordem (module_order) seja única PARA CADA curso
        ordering = ["course", "module_order"]

    def __str__(self):
        return f"{self.course.title} - Módulo {self.module_order}: {self.title}"


# Modelo: lições do módulo
class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,  # Se deletar o Módulo, deleta a Lição
        related_name="lessons",  # Permite fazer module.lessons.all()
        help_text="Módulo ao qual esta lição pertence.",
    )
    title = models.CharField(max_length=255, help_text="Título da lição.")
    lesson_order = models.IntegerField(
        help_text="Ordem da lição dentro do módulo (1, 2, 3...)."
    )
    lesson_type = models.CharField(
        max_length=10,
        choices=LessonTypeChoices.choices,
        default=LessonTypeChoices.VIDEO,
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Conteúdo (usado se o tipo for 'Texto' ou 'Quiz').",
    )
    video_url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        help_text="URL do vídeo (usado se o tipo for 'Vídeo').",
    )
    duration_in_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duração (em segundos) do vídeo ou tempo de leitura.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lição"
        verbose_name_plural = "Lições"
        unique_together = (
            "module",
            "lesson_order",
        )  # Garante que a ordem (lesson_order) seja única PARA CADA módulo
        ordering = ["module", "lesson_order"]  # Ordena as lições por padrão

    def __str__(self):
        return f"{self.module.title} - Aula {self.lesson_order}: {self.title}"


# Modelo: matrículas de alunos nos cursos
class Enrollment(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",  # Permite fazer student.enrollments.all()
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",  # Permite fazer course.enrollments.all()
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True, help_text="Data em que o aluno se matriculou."
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Data em que o aluno completou o curso."
    )

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = (
            "student",
            "course",
        )  # Garante que um aluno só possa se matricular UMA VEZ em cada curso

    def __str__(self):
        return f"Aluno {self.student.nickname} matriculado em {self.course.title}"


# Modelo: progresso das lições
class LessonProgress(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="lesson_progress",  # Permite fazer student.lesson_progress.all()
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_records",  # Permite fazer lesson.progress_records.all()
    )
    completed_at = models.DateTimeField(
        auto_now_add=True, help_text="Data em que o aluno completou a lição."
    )

    class Meta:
        verbose_name = "Progresso de Lição"
        verbose_name_plural = "Progressos de Lições"
        unique_together = (
            "student",
            "lesson",
        )  # Garante que um aluno só possa completar cada lição UMA VEZ

    def __str__(self):
        return f"Progresso: {self.student.nickname} completou {self.lesson.title}"


# Modelo: material de apoio
class Material(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="materials",  # Permite fazer lesson.materials.all()
        help_text="Lição à qual este material pertence.",
    )
    title = models.CharField(
        max_length=255,
        help_text="Título do material (ex: 'Slides da Aula', 'Código Fonte').",
    )
    file_url = models.URLField(
        max_length=255, help_text="URL para o arquivo (PDF, ZIP, etc)."
    )
    file_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Tipo do arquivo (ex: 'pdf', 'zip').",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Material de Apoio"
        verbose_name_plural = "Materiais de Apoio"
        ordering = ["created_at"]  # Ordena os materiais pelo mais antigo

    def __str__(self):
        return f"{self.title} (Lição: {self.lesson.title})"


# Modelo: legenda
class Subtitle(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="ID público para ser usado em URLs e APIs.",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="subtitles",  # Permite fazer lesson.subtitles.all()
        help_text="Lição de vídeo à qual esta legenda pertence.",
    )
    language_code = models.CharField(
        max_length=10, help_text="Código da língua (ex: 'pt-BR', 'en-US')."
    )
    file_url = models.URLField(
        max_length=255, help_text="URL para o arquivo .vtt ou .srt."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Legenda"
        verbose_name_plural = "Legendas"
        # Garante que só exista uma legenda por língua para cada lição
        unique_together = ("lesson", "language_code")
        ordering = ["language_code"]

    def __str__(self):
        return f"Legenda {self.language_code} para {self.lesson.title}"
