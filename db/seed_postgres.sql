INSERT INTO learning_course (title, description, thumbnail_url)
VALUES
('Matemática Divertida 1', 'Curso de matemática inclusivo com foco em TDAH (edição 1).', 'https://placehold.co/600x400/564adc/white?text=Matematica+1'),
('Matemática Divertida 2', 'Curso de matemática inclusivo com foco em TDAH (edição 2).', 'https://placehold.co/600x400/564adc/white?text=Matematica+2'),
('Matemática Divertida 3', 'Curso de matemática inclusivo com foco em TDAH (edição 3).', 'https://placehold.co/600x400/564adc/white?text=Matematica+3'),
('Matemática Divertida 4', 'Curso de matemática inclusivo com foco em TDAH (edição 4).', 'https://placehold.co/600x400/564adc/white?text=Matematica+4'),
('Matemática Divertida 5', 'Curso de matemática inclusivo com foco em TDAH (edição 5).', 'https://placehold.co/600x400/564adc/white?text=Matematica+5'),
('Matemática Divertida 6', 'Curso de matemática inclusivo com foco em TDAH (edição 6).', 'https://placehold.co/600x400/564adc/white?text=Matematica+6'),
('Matemática Divertida 7', 'Curso de matemática inclusivo com foco em TDAH (edição 7).', 'https://placehold.co/600x400/564adc/white?text=Matematica+7'),
('Matemática Divertida 8', 'Curso de matemática inclusivo com foco em TDAH (edição 8).', 'https://placehold.co/600x400/564adc/white?text=Matematica+8'),
('Matemática Divertida 9', 'Curso de matemática inclusivo com foco em TDAH (edição 9).', 'https://placehold.co/600x400/564adc/white?text=Matematica+9'),
('Matemática Divertida 10', 'Curso de matemática inclusivo com foco em TDAH (edição 10).', 'https://placehold.co/600x400/564adc/white?text=Matematica+10');

INSERT INTO learning_module (course_id, title, module_order)
SELECT c.id, CONCAT('Módulo 1 - Operações (', c.title, ')'), 1 FROM learning_course c;
INSERT INTO learning_module (course_id, title, module_order)
SELECT c.id, CONCAT('Módulo 2 - Formas (', c.title, ')'), 2 FROM learning_course c;
INSERT INTO learning_module (course_id, title, module_order)
SELECT c.id, CONCAT('Módulo 3 - Desafios (', c.title, ')'), 3 FROM learning_course c;

INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Vídeo: Adição Básica (', m.title, ')'), 1, 'video', '', CONCAT('https://videos.example.com/', replace(lower(m.title), ' ', '_'), '_video1.mp4'), 600
FROM learning_module m WHERE m.module_order = 1;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Texto: Adição Explicada (', m.title, ')'), 2, 'text', 'Conteúdo textual de apoio para adição básica. Explica conceitos com exemplos simples.', NULL, NULL
FROM learning_module m WHERE m.module_order = 1;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Quiz: Adição (', m.title, ')'), 3, 'quiz', 'Perguntas de múltipla escolha sobre adição básica.', NULL, NULL
FROM learning_module m WHERE m.module_order = 1;

INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Vídeo: Formas Geométricas (', m.title, ')'), 1, 'video', '', CONCAT('https://videos.example.com/', replace(lower(m.title), ' ', '_'), '_video2.mp4'), 540
FROM learning_module m WHERE m.module_order = 2;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Texto: Reconhecendo Formas (', m.title, ')'), 2, 'text', 'Conteúdo textual de apoio para reconhecimento de formas geométricas.', NULL, NULL
FROM learning_module m WHERE m.module_order = 2;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Quiz: Formas (', m.title, ')'), 3, 'quiz', 'Perguntas de múltipla escolha sobre formas geométricas.', NULL, NULL
FROM learning_module m WHERE m.module_order = 2;

INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Vídeo: Problemas Divertidos (', m.title, ')'), 1, 'video', '', CONCAT('https://videos.example.com/', replace(lower(m.title), ' ', '_'), '_video3.mp4'), 720
FROM learning_module m WHERE m.module_order = 3;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Texto: Estratégias de Resolução (', m.title, ')'), 2, 'text', 'Conteúdo textual sobre estratégias para resolver problemas matemáticos.', NULL, NULL
FROM learning_module m WHERE m.module_order = 3;
INSERT INTO learning_lesson (module_id, title, lesson_order, lesson_type, content, video_url, duration_in_seconds)
SELECT m.id, CONCAT('Quiz: Desafios (', m.title, ')'), 3, 'quiz', 'Perguntas de múltipla escolha sobre desafios matemáticos.', NULL, NULL
FROM learning_module m WHERE m.module_order = 3;

INSERT INTO learning_material (lesson_id, title, file_url)
SELECT l.id, 'Mapa Mental - Tópico', CONCAT('https://files.example.com/', replace(lower(l.title), ' ', '_'), '_mapa.pdf')
FROM learning_lesson l;
INSERT INTO learning_material (lesson_id, title, file_url)
SELECT l.id, 'Podcast - Tópico', CONCAT('https://files.example.com/', replace(lower(l.title), ' ', '_'), '_podcast.mp3')
FROM learning_lesson l;

INSERT INTO accounts_user (email, full_name, password, role, agreed_to_terms, is_staff, is_superuser)
VALUES
('responsavel1@example.com', 'Responsável 1', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel2@example.com', 'Responsável 2', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel3@example.com', 'Responsável 3', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel4@example.com', 'Responsável 4', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel5@example.com', 'Responsável 5', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel6@example.com', 'Responsável 6', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel7@example.com', 'Responsável 7', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel8@example.com', 'Responsável 8', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel9@example.com', 'Responsável 9', '!', 'guardian', TRUE, FALSE, FALSE),
('responsavel10@example.com', 'Responsável 10', '!', 'guardian', TRUE, FALSE, FALSE);

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2015-01-10', 'ano_3', 'desatento' FROM accounts_user u WHERE u.email='responsavel1@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2014-05-12', 'ano_4', 'hiperativo_impulsivo' FROM accounts_user u WHERE u.email='responsavel1@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2016-03-12', 'ano_2', 'combinado' FROM accounts_user u WHERE u.email='responsavel2@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2013-09-20', 'ano_5', 'nao_informado' FROM accounts_user u WHERE u.email='responsavel3@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2012-08-11', 'ano_6', 'desatento' FROM accounts_user u WHERE u.email='responsavel3@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno C de ' || u.full_name, DATE '2014-02-05', 'ano_4', 'hiperativo_impulsivo' FROM accounts_user u WHERE u.email='responsavel3@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2015-04-02', 'ano_3', 'desatento' FROM accounts_user u WHERE u.email='responsavel4@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2017-07-18', 'ano_1', 'combinado' FROM accounts_user u WHERE u.email='responsavel4@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2011-11-11', 'ano_6', 'desatento' FROM accounts_user u WHERE u.email='responsavel5@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2010-10-10', 'ano_7', 'hiperativo_impulsivo' FROM accounts_user u WHERE u.email='responsavel5@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno C de ' || u.full_name, DATE '2013-01-01', 'ano_5', 'combinado' FROM accounts_user u WHERE u.email='responsavel5@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno D de ' || u.full_name, DATE '2016-06-06', 'ano_2', 'nao_informado' FROM accounts_user u WHERE u.email='responsavel5@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno E de ' || u.full_name, DATE '2017-07-07', 'ano_1', 'desatento' FROM accounts_user u WHERE u.email='responsavel5@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2012-12-12', 'ano_6', 'combinado' FROM accounts_user u WHERE u.email='responsavel6@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2014-04-14', 'ano_4', 'nao_informado' FROM accounts_user u WHERE u.email='responsavel7@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2015-05-15', 'ano_3', 'hiperativo_impulsivo' FROM accounts_user u WHERE u.email='responsavel7@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2013-03-13', 'ano_5', 'desatento' FROM accounts_user u WHERE u.email='responsavel8@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2016-09-09', 'ano_2', 'combinado' FROM accounts_user u WHERE u.email='responsavel8@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno C de ' || u.full_name, DATE '2017-02-02', 'ano_1', 'nao_informado' FROM accounts_user u WHERE u.email='responsavel8@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2011-01-20', 'ano_7', 'desatento' FROM accounts_user u WHERE u.email='responsavel9@example.com';

INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno A de ' || u.full_name, DATE '2012-02-21', 'ano_6', 'hiperativo_impulsivo' FROM accounts_user u WHERE u.email='responsavel10@example.com';
INSERT INTO accounts_student (user_id, nickname, birth_date, school_year, adhd_type)
SELECT u.id, 'Aluno B de ' || u.full_name, DATE '2013-03-22', 'ano_5', 'combinado' FROM accounts_user u WHERE u.email='responsavel10@example.com';

INSERT INTO learning_enrollment (student_id, course_id)
SELECT s.id, c.id FROM accounts_student s JOIN learning_course c ON c.title IN ('Matemática Divertida 1', 'Matemática Divertida 2');
INSERT INTO learning_enrollment (student_id, course_id)
SELECT s.id, c.id FROM accounts_student s JOIN learning_course c ON c.title IN ('Matemática Divertida 3', 'Matemática Divertida 4') WHERE s.id % 2 = 0;