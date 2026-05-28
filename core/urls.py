"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views
from learning import views as learning_views
from support import views as support_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", accounts_views.home, name="home"),
    path("login/", accounts_views.login_view, name="login"),
    path("esqueci-minha-senha/", accounts_views.forgot_password_view, name="forgot_password"),
    path("redefinir-senha/<uuid:token>/", accounts_views.reset_password_view, name="reset_password"),
    path("cadastro/", accounts_views.cadastro_view, name="cadastro"),
    path("cadastro-aluno/", accounts_views.cadastro_aluno_view, name="cadastro_aluno"),
    path("dashboard/", accounts_views.dashboard_responsavel_view, name="dashboard_responsavel"),
    path("meus-dados/", accounts_views.meus_dados_view, name="meus_dados"),
    path("meus-dados/atualizar/", accounts_views.atualizar_perfil_view, name="atualizar_perfil"),
    path("meus-dados/senha/", accounts_views.atualizar_senha_view, name="atualizar_senha"),
    path("excluir-conta/", accounts_views.excluir_conta_view, name="excluir_conta"),
    path("aluno/remover/<uuid:public_id>/", accounts_views.remover_aluno_view, name="remover_aluno"),
    path("aluno/editar/<uuid:public_id>/", accounts_views.editar_aluno_view, name="editar_aluno"),
    path("dashboard-aluno/<uuid:student_public_id>/", learning_views.dashboard_aluno_view, name="dashboard_aluno"),
    path("curso/<uuid:course_public_id>/continuar/<uuid:student_public_id>/", learning_views.continuar_curso_view, name="continuar_curso"),
    path("curso/<uuid:course_public_id>/detalhes/<uuid:student_public_id>/", learning_views.course_detail_view, name="course_detail"),
    path("curso/<uuid:course_public_id>/matricular/<uuid:student_public_id>/", learning_views.enroll_course_view, name="enroll_course"),
    path("curso/<uuid:course_public_id>/concluir/<uuid:student_public_id>/", learning_views.concluir_curso_view, name="concluir_curso"),
    path("pausa/<uuid:next_lesson_public_id>/<uuid:student_public_id>/", learning_views.pausa_view, name="pausa"),
    path("licao/<uuid:lesson_public_id>/<uuid:student_public_id>/", learning_views.lesson_detail_view, name="lesson_detail"),
    path("licao/<uuid:lesson_public_id>/<uuid:student_public_id>/concluir/", learning_views.concluir_licao_view, name="concluir_licao"),
    path("suporte/", support_views.suporte_view, name="suporte"),
    path("logout/", accounts_views.logout_view, name="logout"),
]
