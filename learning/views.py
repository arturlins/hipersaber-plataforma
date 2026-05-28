from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from accounts.models import Student
from learning.models import Course, Module, Lesson, Enrollment, LessonTypeChoices
from learning.models import LessonProgress, Material

def _course_lessons_ordered(course):
    return list(Lesson.objects.filter(module__course=course).select_related("module").order_by("module__module_order", "lesson_order"))

@login_required
def dashboard_aluno_view(request, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    request.session["active_student"] = str(student.public_id)
    enrollments = Enrollment.objects.select_related("course").filter(student=student)
    # calcular progresso por curso
    progress_list = []
    for e in enrollments:
        course = e.course
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed = LessonProgress.objects.filter(student=student, lesson__module__course=course).count()
        percent = int((completed / total_lessons) * 100) if total_lessons else 0
        progress_list.append({"enrollment": e, "percent": percent, "total": total_lessons, "completed": completed})
    enrolled_ids = [e.course_id for e in enrollments]
    available_courses = Course.objects.exclude(id__in=enrolled_ids)
    return render(request, "learning/dashboard_aluno.html", {"student": student, "enrollments": enrollments, "available_courses": available_courses, "progress": progress_list})

@login_required
def continuar_curso_view(request, course_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    course = get_object_or_404(Course, public_id=course_public_id)
    lessons = _course_lessons_ordered(course)
    if not lessons:
        return redirect("dashboard_aluno", student_public_id=student.public_id)
    unfinished = [l for l in lessons if not LessonProgress.objects.filter(student=student, lesson=l).exists()]
    target = unfinished[0] if unfinished else lessons[0]
    return redirect("lesson_detail", lesson_public_id=target.public_id, student_public_id=student.public_id)

@login_required
def pausa_view(request, next_lesson_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    return render(request, "learning/pausa.html", {"student": student, "next_lesson_public_id": next_lesson_public_id})

@login_required
def lesson_detail_view(request, lesson_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    lesson = get_object_or_404(Lesson, public_id=lesson_public_id)
    ordered = _course_lessons_ordered(lesson.module.course)
    idx = ordered.index(lesson)
    prev_lesson = ordered[idx - 1] if idx > 0 else None
    next_lesson = ordered[idx + 1] if idx < len(ordered) - 1 else None
    is_last = next_lesson is None
    is_first = prev_lesson is None
    course = lesson.module.course
    conclude_url = None
    if is_last:
        conclude_url = f"/curso/{course.public_id}/concluir/{student.public_id}/"
    # materiais de apoio
    materials = list(Material.objects.filter(lesson=lesson))
    if lesson.lesson_type == LessonTypeChoices.VIDEO:
        is_html5_video = bool(lesson.video_url and lesson.video_url.lower().endswith(".mp4"))
        return render(
            request,
            "learning/lesson_video.html",
            {
                "student": student,
                "lesson": lesson,
                "next_lesson": next_lesson,
                "prev_lesson": prev_lesson,
                "is_last": is_last,
                "is_first": is_first,
                "conclude_url": conclude_url,
                "materials": materials,
                "is_html5_video": is_html5_video,
            },
        )
    if lesson.lesson_type == LessonTypeChoices.TEXT:
        content_lines = [line.strip() for line in (lesson.content or "").split("\n") if line.strip()]
        return render(
            request,
            "learning/lesson_text_tts.html",
            {
                "student": student,
                "lesson": lesson,
                "content_lines": content_lines,
                "next_lesson": next_lesson,
                "prev_lesson": prev_lesson,
                "is_last": is_last,
                "is_first": is_first,
                "conclude_url": conclude_url,
                "materials": materials,
            },
        )
    # QUIZ
    quiz_choices = []
    return render(
        request,
        "learning/lesson_quiz.html",
        {
            "student": student,
            "lesson": lesson,
            "quiz_choices": quiz_choices,
            "next_lesson": next_lesson,
            "prev_lesson": prev_lesson,
            "is_last": is_last,
            "is_first": is_first,
            "conclude_url": conclude_url,
            "materials": materials,
        },
    )

@login_required
@require_http_methods(["POST"])
def concluir_licao_view(request, lesson_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    lesson = get_object_or_404(Lesson, public_id=lesson_public_id)
    # cria progresso (MVP, independente de pontuação)
    LessonProgress.objects.get_or_create(student=student, lesson=lesson)
    ordered = _course_lessons_ordered(lesson.module.course)
    idx = ordered.index(lesson)
    next_lesson = ordered[idx + 1] if idx < len(ordered) - 1 else None
    if next_lesson is None:
        # última lição: concluir curso
        return redirect("concluir_curso", course_public_id=lesson.module.course.public_id, student_public_id=student.public_id)
    return redirect("pausa", next_lesson_public_id=next_lesson.public_id, student_public_id=student.public_id)

@login_required
def course_detail_view(request, course_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    course = get_object_or_404(Course, public_id=course_public_id)
    modules = course.modules.prefetch_related("lessons").order_by("module_order")
    return render(request, "learning/course_detail.html", {"student": student, "course": course, "modules": modules})

@login_required
@require_http_methods(["POST"]) 
def enroll_course_view(request, course_public_id, student_public_id):
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    course = get_object_or_404(Course, public_id=course_public_id)
    Enrollment.objects.get_or_create(student=student, course=course)
    return redirect("dashboard_aluno", student_public_id=student.public_id)

@login_required
@require_http_methods(["POST"]) 
def concluir_curso_view(request, course_public_id, student_public_id):
    from django.utils import timezone
    student = get_object_or_404(Student, public_id=student_public_id, user=request.user)
    course = get_object_or_404(Course, public_id=course_public_id)
    enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
    # garantir 100%: cria progresso para todas as lições do curso
    for lesson in Lesson.objects.filter(module__course=course):
        LessonProgress.objects.get_or_create(student=student, lesson=lesson)
    enrollment.completed_at = timezone.now()
    enrollment.save()
    return redirect("dashboard_aluno", student_public_id=student.public_id)

# Create your views here.
