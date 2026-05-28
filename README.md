**Visão Geral**
- Plataforma educacional para crianças com TDAH, construída com `Django 5.2`. Organiza cursos, módulos e lições, com acompanhamento por responsáveis, suporte e recursos de acessibilidade (vídeo com velocidade, TTS, materiais, quizzes e pausas pedagógicas).
- A arquitetura segue orientação a objetos: entidades de domínio modeladas como classes (`User`, `Student`, `Course`, etc.), relações e regras via ORM; controladores como funções de view, e personalizações administrativas via classes de admin.

**Estrutura Django**
- `manage.py`: ponto de entrada de comandos (`runserver`, `migrate`, `createsuperuser`).
- `core/settings.py`: configuração do projeto (apps, banco, templates, static, email). Customiza `AUTH_USER_MODEL` para `accounts.User` e inclui `EMAIL_BACKEND` console.
- `core/urls.py`: roteamento central, agregando todas as URLs para contas, aprendizagem e suporte.
- `core/wsgi.py` e `core/asgi.py`: inicialização para servidores WSGI/ASGI.
- `apps.py` de cada app: registro e metadados (`AppConfig`).
- `migrations/`: arquivos de migração por app gerados pelo ORM (criação/alteração de tabelas). 
- `templates/`: HTML por app, renderizado pelas views.
- `admin.py`: configurações do Django Admin para manutenção das entidades.
- `tests.py`: ponto inicial para testes unitários por app.

**App Accounts (Contas)**
- Propósito: autenticação, gestão do responsável e perfis de alunos, fluxo de cadastro, recuperação de senha e dados da conta.
- Modelos (orientação a objetos):
  - `User` (`accounts/models.py:82`): usuário principal, com `email` como identificador, `full_name`, campo de papel (`role`), e `public_id`. Estende `AbstractBaseUser` e `PermissionsMixin`. O `UserManager` define fábricas (`create_user`, `create_superuser`).
  - `Student` (`accounts/models.py:127`): perfil de aluno associado a um `User` via `ForeignKey`. Atributos: `nickname`, `birth_date`, `school_year`, `adhd_type` e `public_id`.
  - `PasswordResetToken` (`accounts/models.py:198`): token UUID de uso único para redefinição de senha, com `expires_at` e `used_at`.
  - Enums: `AdhdTypeChoices` (`accounts/models.py:12`), `SchoolYearChoices` (`accounts/models.py:20`), `RoleChoices` (`accounts/models.py:33`).
  - Proxy models: `GuardianUser`, `AdminUser`, `SuperuserUser` (não criam tabelas; filtram por papel para o admin).
- Views (controladores):
  - `home` (`accounts/views.py:15`): landing page pública.
  - `login_view` (`accounts/views.py:18`): autenticação com bloqueio após 5 falhas, sessão com expiração condicional e mensagem genérica em caso de erro.
  - `cadastro_view` (`accounts/views.py:50`): valida dados do responsável, cria `User` e autentica.
  - `cadastro_aluno_view` (`accounts/views.py:85`): valida e cria `Student`; suporta “Adicionar outro aluno” e “Concluir”.
  - `dashboard_responsavel_view` (`accounts/views.py:128`): lista perfis de alunos do responsável.
  - `meus_dados_view` (`accounts/views.py:135`), `atualizar_perfil_view` (`accounts/views.py:146`), `atualizar_senha_view` (`accounts/views.py:166`): gestão de perfil e senha com validações por campo.
  - `remover_aluno_view` (`accounts/views.py:182`): remove aluno preservando regra de mínimo 1 perfil.
  - `editar_aluno_view` (`accounts/views.py:193`): atualização de um perfil existente.
  - `excluir_conta_view` (`accounts/views.py:232`): exclusão da conta com confirmação de senha.
  - `forgot_password_view` (`accounts/views.py:256`): solicita e envia token de recuperação.
  - `reset_password_view` (`accounts/views.py:276`): valida token, exige senha forte, proíbe reutilização e salva nova senha.
  - `logout_view` (`accounts/views.py:243`): encerra sessão e redireciona para a home.
- Admin:
  - `accounts/admin.py`: `StudentAdmin` e uma hierarquia `UserAdminBase` que reforça o papel (`role`) e registra `GuardianUser`, `AdminUser`, `SuperuserUser` com listas filtradas.
- Templates principais:
  - `accounts/templates/accounts/home.html`: landing.
  - `login.html`, `cadastro_responsavel.html`, `cadastrar_aluno.html`, `dashboard_responsavel.html`, `meus_dados.html`.
  - Recuperação de senha: `recuperar_senha_solicitar.html`, `recuperar_senha_redefinir.html`.
- Tests:
  - `accounts/tests.py`: base de testes (ponto de partida para cenários de autenticação e validações).

**App Learning (Aprendizagem)**
- Propósito: estrutura de cursos, módulos e lições; navegação de aluno, progresso, materiais, pausa pedagógica e conclusão.
- Modelos (orientação a objetos):
  - `Course` (`learning/models.py:15`): curso com metadados e `public_id`.
  - `Module` (`learning/models.py:46`): módulo ordenado por `module_order`, ligado a `Course`.
  - `Lesson` (`learning/models.py:82`): lição ordenada por `lesson_order`, ligada a `Module`. Suporta tipos (`LessonTypeChoices`), conteúdo de texto e `video_url`.
  - `Enrollment` (`learning/models.py:139`): matrícula de `Student` em `Course` com `enrolled_at` e `completed_at`.
  - `LessonProgress` (`learning/models.py:178`): marca uma lição concluída por um aluno (único por par aluno–lição).
  - `Material` (`learning/models.py:214`): materiais de apoio vinculados à lição.
  - `Subtitle` (`learning/models.py:254`): legendas por língua para vídeos.
- Views (controladores):
  - `dashboard_aluno_view` (`learning/views.py:11`): lista cursos matriculados, calcula progresso e exibe catálogo de disponíveis.
  - `continuar_curso_view` (`learning/views.py:28`): direciona para a próxima lição não concluída.
  - `lesson_detail_view` (`learning/views.py:45`): resolve prev/next e renderiza por tipo: vídeo (`lesson_video.html`), texto+TTS (`lesson_text_tts.html`), quiz (`lesson_quiz.html`).
  - `concluir_licao_view` (`learning/views.py:112`): grava `LessonProgress` e redireciona para pausa ou conclusão de curso.
  - `pausa_view` (`learning/views.py:39`): tela de pausa/reflexão com timer e avanço.
  - `course_detail_view` (`learning/views.py:127`): detalhes do curso com lições e ações.
  - `enroll_course_view` (`learning/views.py:134`): cria `Enrollment` e volta ao dashboard do aluno.
  - `concluir_curso_view` (`learning/views.py:142`): marca todas as lições como concluídas e define `completed_at`.
- Admin:
  - `learning/admin.py`: inlines para editar lições dentro de módulos e módulos dentro de cursos; configurações para listas e filtros de `Enrollment` e `LessonProgress`.
- Templates principais:
  - `dashboard_aluno.html`, `course_detail.html`, `lesson_video.html` (controle de velocidade), `lesson_text_tts.html` (TTS), `lesson_quiz.html` (atividade), `pausa.html`.
- Seeds:
  - `learning/management/commands/seed_demo.py`: comando ORM que cria cursos, módulos, lições, materiais, responsáveis, alunos e matrículas para testes.
- Tests:
  - `learning/tests.py`: base para validar navegação e progresso.

**App Support (Suporte)**
- Propósito: registro de tickets de suporte e notificação por email.
- Modelos (orientação a objetos):
  - `SupportTicket` (`support/models.py:13`): ticket com `subject`, `message`, `status` (enum `TicketStatusChoices`), `user` (opcional) e carimbos de data.
- Views:
  - `suporte_view` (`support/views.py:7`): valida campos, cria `SupportTicket` e envia email a `settings.SUPPORT_EMAIL`.
- Admin:
  - `support/admin.py`: lista tickets com filtros por status e data.
- Template:
  - `support/templates/support/suporte.html`: formulário com feedback e botão cancelar.
- Tests:
  - `support/tests.py`: base para validação de criação e fluxo de suporte.

**URLs e Rotas**
- `core/urls.py`: define rotas para home, login, cadastro de responsável/aluno, dashboards, fluxo de lições (pausa, concluir), suporte, recuperação de senha e logout.
- Exemplos de rotas: `"/dashboard-aluno/<uuid:student_public_id>/"`, `"/curso/<uuid:course_public_id>/detalhes/<uuid:student_public_id>/"`, `"/licao/<uuid:lesson_public_id>/<uuid:student_public_id>/concluir/"`.

**Templates e Camada de Apresentação**
- Cada view renderiza um template com dados do contexto; componentes visuais seguem estilo coerente e acessível.
- Vídeo: player responsivo 16:9 com controle de velocidade e navegação prev/next.
- Texto: TTS via Web Speech API com destaque do trecho lido e controles simples.
- Quiz: múltipla escolha com feedback e registro de conclusão.
- Materiais: seção colapsável, exibida quando existem itens.

**Orientação a Objetos no Design**
- Entidades e agregados do domínio representados por classes: `User`–`Student`, `Course`–`Module`–`Lesson`, `Enrollment`, `LessonProgress` e `SupportTicket`.
- Encapsulamento de regras: enums (`TextChoices`) restringem estados válidos; `unique_together` define invariantes de domínio; managers e views concentram fluxo e validação.
- Polimorfismo e extensão: proxy models para separar visualizações administrativas por papel sem novas tabelas; views escolhem template com base em `lesson_type`.
- Composição: relações `ForeignKey` estruturam vínculos entre entidades para consultas eficientes e integridade referencial.

**Admin e Operação**
- Admins por app expõem listas, filtros e inlines para edição hierárquica (Curso→Módulo→Lição), mantendo `public_id` imutável e facilitando manutenção.
- `StudentAdmin` e variantes de `UserAdmin` reforçam papéis e restrições de segurança conforme o papel do usuário.

**Configurações Relevantes**
- Banco: PostgreSQL via `DATABASES`.
- Autenticação: `AUTH_USER_MODEL = "accounts.User"`.
- Templates: `APP_DIRS=True` e diretório adicional `prototype_templates`.
- Estáticos: `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`.
- Email: `EMAIL_BACKEND` console e `SUPPORT_EMAIL`.

**Como Navegar o Código**
- Inicie por `core/urls.py` para ver o mapa de rotas; siga para as views nos apps (`accounts/views.py`, `learning/views.py`, `support/views.py`) e revisite os modelos para entender o domínio e relações.
- Use os templates correspondentes para entender o fluxo de UI e os nomes de variáveis esperadas no contexto.