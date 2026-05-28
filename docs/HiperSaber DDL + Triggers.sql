-- ENUMS 
CREATE TYPE adhd_type_enum AS ENUM (
  'desatento',
  'hiperativo_impulsivo',
  'combinado',
  'nao_informado'
);

CREATE TYPE school_year_enum AS ENUM (
  'ano_1',
  'ano_2',
  'ano_3',
  'ano_4',
  'ano_5',
  'ano_6',
  'ano_7',
  'ano_8',
  'ano_9'
);

CREATE TYPE lesson_type_enum AS ENUM (
  'video',
  'text',
  'quiz'
);

CREATE TYPE role_enum AS ENUM (
  'guardian',
  'admin',
  'superuser'
);

CREATE TYPE ticket_status_enum AS ENUM (
  'novo',
  'em_andamento',
  'resolvido'
);

-- Tabela "User"
CREATE TABLE "User" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "email" varchar(200) NOT NULL UNIQUE,
  "password_hash" varchar(255) NOT NULL,
  "full_name" varchar(300) NOT NULL,
  "agreed_to_terms" boolean NOT NULL DEFAULT false,
  "last_login" timestamp,
  "is_staff" boolean NOT NULL DEFAULT false,
  "is_superuser" boolean NOT NULL DEFAULT false,
  "role" role_enum NOT NULL DEFAULT 'guardian',
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

-- Tabela "Student"
CREATE TABLE "Student" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "user_id" bigint NOT NULL REFERENCES "User"("id") ON DELETE RESTRICT,
  "nickname" varchar(300) NOT NULL,
  "birth_date" date,
  "school_year" school_year_enum NOT NULL,
  "adhd_type" adhd_type_enum NOT NULL DEFAULT 'nao_informado',
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

-- Tabela "Course"
CREATE TABLE "Course" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "title" varchar(255) NOT NULL,
  "description" text,
  "thumbnail_url" varchar(255),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

-- Tabela "Module"
CREATE TABLE "Module" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "course_id" bigint NOT NULL REFERENCES "Course"("id") ON DELETE CASCADE,
  "title" varchar(255) NOT NULL,
  "module_order" int NOT NULL,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now()),
  UNIQUE ("course_id", "module_order")
);

-- Tabela "Lesson"
CREATE TABLE "Lesson" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "module_id" bigint NOT NULL REFERENCES "Module"("id") ON DELETE CASCADE,
  "title" varchar(255) NOT NULL,
  "lesson_type" lesson_type_enum NOT NULL,
  "content" text,
  "video_url" varchar(255),
  "duration_in_seconds" int,
  "lesson_order" int NOT NULL,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now()),
  UNIQUE ("module_id", "lesson_order")
);

-- Tabela "Material"
CREATE TABLE "Material" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "lesson_id" bigint NOT NULL REFERENCES "Lesson"("id") ON DELETE CASCADE,
  "title" varchar(255) NOT NULL,
  "file_url" varchar(255) NOT NULL,
  "file_type" varchar(50),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

-- Tabela "Subtitle"
CREATE TABLE "Subtitle" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "lesson_id" bigint NOT NULL REFERENCES "Lesson"("id") ON DELETE CASCADE,
  "language_code" varchar(10) NOT NULL,
  "file_url" varchar(255) NOT NULL,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

-- Tabela "Enrollment"
CREATE TABLE "Enrollment" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "student_id" bigint NOT NULL REFERENCES "Student"("id") ON DELETE CASCADE,
  "course_id" bigint NOT NULL REFERENCES "Course"("id") ON DELETE CASCADE,
  "enrolled_at" timestamp DEFAULT (now()),
  "completed_at" timestamp,
  UNIQUE ("student_id", "course_id")
);

-- Tabela "LessonProgress"
CREATE TABLE "LessonProgress" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "student_id" bigint NOT NULL REFERENCES "Student"("id") ON DELETE CASCADE,
  "lesson_id" bigint NOT NULL REFERENCES "Lesson"("id") ON DELETE CASCADE,
  "completed_at" timestamp DEFAULT (now()),
  UNIQUE ("student_id", "lesson_id")
);

-- Tabela "SupportTicket"
CREATE TABLE "SupportTicket" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "user_id" bigint NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "subject" varchar(255) NOT NULL,
  "message" text NOT NULL,
  "status" ticket_status_enum NOT NULL DEFAULT 'novo',
  "created_at" timestamp DEFAULT (now()),
  "resolved_at" timestamp
);

-- Tabela "AdminLogs"
CREATE TABLE "AdminLogs" (
  "id" bigserial PRIMARY KEY,
  "public_id" uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  "admin_internal_id" bigint, 
  "admin_public_id" uuid,
  "admin_name" varchar(300) NOT NULL,  
  "admin_email" varchar(200) NOT NULL, 
  "action" varchar(255) NOT NULL,
  "target_entity" varchar(100),
  "target_internal_id" bigint,
  "target_public_id" uuid,
  "details_old" jsonb,
  "details_new" jsonb,
  "date" timestamp DEFAULT (now())
);

-- -----------------------------------------------------------------------------------------

-- TRIGGER


-- Função do Trigger
CREATE OR REPLACE FUNCTION fn_log_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_id bigint;
    v_public_id uuid;
    v_dados_antigos jsonb;
    v_dados_novos jsonb;
BEGIN

    -- 1. Prepara as variáveis (Define ID e JSON)
    IF (TG_OP = 'INSERT') THEN
        v_id            := NEW.id;
        v_public_id     := NEW.public_id;
        v_dados_antigos := NULL;
        v_dados_novos   := to_jsonb(NEW);

    ELSIF (TG_OP = 'UPDATE') THEN
        v_id            := NEW.id;
        v_public_id     := NEW.public_id;
        v_dados_antigos := to_jsonb(OLD);
        v_dados_novos   := to_jsonb(NEW);

    ELSIF (TG_OP = 'DELETE') THEN
        v_id            := OLD.id;
        v_public_id     := OLD.public_id;
        v_dados_antigos := to_jsonb(OLD);
        v_dados_novos   := NULL;
    END IF;

    -- 2. Insere na auditoria (AGORA COM OS CAMPOS OBRIGATÓRIOS)
    INSERT INTO "AdminLogs" (
        admin_name,
        admin_email,
        action,
        target_entity,
        target_internal_id,
        target_public_id,
        details_old,
        details_new,
        date
    )
    VALUES (
        current_user,
        current_user || '@email.com',
        TG_OP,
        TG_TABLE_NAME,
        v_id,
        v_public_id,
        v_dados_antigos,
        v_dados_novos,
        now()
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


-- --------------------------------------------------------------------------------------------


-- Um trigger para cada tabela do banco de dados
CREATE TRIGGER trg_log_user_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "User" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_student_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Student" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_course_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Course" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_module_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Module" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_lesson_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Lesson" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_material_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Material" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_subtitle_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Subtitle" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_enrollment_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "Enrollment" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_lessonprogress_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "LessonProgress" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();

CREATE TRIGGER trg_log_supportticket_changes 
AFTER INSERT OR UPDATE OR DELETE 
ON "SupportTicket" FOR EACH ROW 
EXECUTE FUNCTION fn_log_changes();


-- -----------------------------------------------------------------------------------------

-- Testes do trigger

-- 1.1 Criar um Usuário Responsável
INSERT INTO "User" (email, password_hash, full_name, role) 
VALUES ('teste.pai@email.com', 'senha_falsa_123', 'Carlos Silva', 'guardian');

-- 1.2 Criar um Aluno vinculado a esse pai (Usando subselect para pegar o ID automático)
INSERT INTO "Student" (user_id, nickname, school_year, adhd_type) 
VALUES (
    (SELECT id FROM "User" WHERE email = 'teste.pai@email.com'), 
    'Juninho', 
    'ano_5', 
    'combinado'
);

-- 1.3 Criar um Curso
INSERT INTO "Course" (title, description) 
VALUES ('Matemática Divertida', 'Aprendendo tabuada com jogos');

-- 2.1 O Pai mudou de nome
UPDATE "User" 
SET full_name = 'Carlos Silva Souza' 
WHERE email = 'teste.pai@email.com';

-- 2.2 O Juninho passou de ano
UPDATE "Student" 
SET school_year = 'ano_6' 
WHERE nickname = 'Juninho';

-- 3.1 Apagar o Curso
DELETE FROM "Course" WHERE title = 'Matemática Divertida';

-- 3.2 Apagar o Aluno
DELETE FROM "Student" WHERE nickname = 'Juninho';

-- 3.3 Apagar o Usuário
DELETE FROM "User" WHERE email = 'teste.pai@email.com';



-- --------------------------------------------------------------------------------------------

-- SELECT do trigger

SELECT 
    id, 
    admin_name AS "Nome",
    admin_email AS "E-mail",
    action AS "Ação", 
    target_entity AS "Tabela alterada", 
    target_internal_id AS "ID Alvo",
    details_old AS "Antes", 
    details_new AS "Depois",
    date
FROM "AdminLogs"
ORDER BY id DESC;