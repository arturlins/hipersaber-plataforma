from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, Student, RoleChoices, AdhdTypeChoices, SchoolYearChoices
from learning.models import Course, Module, Lesson, Material, Enrollment, LessonTypeChoices
import random

class Command(BaseCommand):
    def handle(self, *args, **options):
        courses = []
        for i in range(1, 11):
            title = f"Matemática Divertida {i}"
            course, _ = Course.objects.get_or_create(title=title, defaults={"description": f"Curso de matemática inclusivo com foco em TDAH (edição {i}).", "thumbnail_url": f"https://placehold.co/600x400/564adc/white?text=Matematica+{i}"})
            courses.append(course)
        for course in courses:
            for order, mod_title in [(1, "Operações"), (2, "Formas"), (3, "Desafios")]:
                module, _ = Module.objects.get_or_create(course=course, module_order=order, defaults={"title": f"Módulo {order} - {mod_title}"})
                Lesson.objects.get_or_create(module=module, lesson_order=1, defaults={"title": f"Vídeo: {mod_title} Básico", "lesson_type": LessonTypeChoices.VIDEO, "video_url": f"https://videos.example.com/{course.title.replace(' ', '_').lower()}_m{order}.mp4", "duration_in_seconds": 600 + order * 60})
                Lesson.objects.get_or_create(module=module, lesson_order=2, defaults={"title": f"Texto: {mod_title} Explicado", "lesson_type": LessonTypeChoices.TEXT, "content": f"Conteúdo textual de apoio para {mod_title.lower()} básico."})
                Lesson.objects.get_or_create(module=module, lesson_order=3, defaults={"title": f"Quiz: {mod_title}", "lesson_type": LessonTypeChoices.QUIZ, "content": f"Perguntas de múltipla escolha sobre {mod_title.lower()} básico."})
        for lesson in Lesson.objects.all():
            Material.objects.get_or_create(lesson=lesson, title="Mapa Mental - Tópico", defaults={"file_url": f"https://files.example.com/{lesson.title.replace(' ', '_').lower()}_mapa.pdf"})
            Material.objects.get_or_create(lesson=lesson, title="Podcast - Tópico", defaults={"file_url": f"https://files.example.com/{lesson.title.replace(' ', '_').lower()}_podcast.mp3"})
        guardians = []
        for i in range(1, 11):
            email = f"responsavel{i}@example.com"
            full_name = f"Responsável {i}"
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                user = User.objects.create_user(email=email, full_name=full_name, password="Teste123@A!", role=RoleChoices.GUARDIAN, agreed_to_terms=True)
            guardians.append(user)
        school_years = [k for k, _ in SchoolYearChoices.choices]
        adhd_types = [k for k, _ in AdhdTypeChoices.choices]
        for user in guardians:
            count = random.randint(1, 5)
            for j in range(count):
                nickname = f"Aluno {chr(65+j)} de {user.full_name}"
                birth_year = random.randint(2010, 2017)
                birth_date = timezone.datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date()
                school_year = random.choice(school_years)
                adhd_type = random.choice(adhd_types)
                Student.objects.get_or_create(user=user, nickname=nickname, defaults={"birth_date": birth_date, "school_year": school_year, "adhd_type": adhd_type})
        all_courses = list(Course.objects.all())
        for student in Student.objects.all():
            enroll_in = random.sample(all_courses, k=min(random.randint(2, 4), len(all_courses)))
            for course in enroll_in:
                Enrollment.objects.get_or_create(student=student, course=course)
        self.stdout.write("Seed concluído com sucesso.")