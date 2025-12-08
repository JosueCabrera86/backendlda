--
-- PostgreSQL database dump
--

-- Dumped from database version 17.7 (178558d)
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO neondb_owner;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    author character varying(100) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.posts OWNER TO neondb_owner;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.posts_id_seq OWNER TO neondb_owner;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    imagen character varying(300),
    subtitulo character varying(200),
    texto text NOT NULL,
    post_id integer NOT NULL
);


ALTER TABLE public.sections OWNER TO neondb_owner;

--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_id_seq OWNER TO neondb_owner;

--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    categoria integer,
    password character varying(300),
    rol character varying(20),
    disciplina character varying(50)
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.alembic_version (version_num) FROM stdin;
d28de085df27
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.posts (id, title, author, created_at) FROM stdin;
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.sections (id, imagen, subtitulo, texto, post_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, name, email, categoria, password, rol, disciplina) FROM stdin;
4	Colectivo Cultural Los de All├í	colectivolosdealla@gmail.com	\N	scrypt:32768:8:1$wjwcDEZrjXLXV4hG$a16ae22cd5e2dfe33603f8863b5461050c157e21da8ebd9ca1b0eb92c8eb6c3a1cf3e6a31b707b8b302f1afa415daa27d96ee60e3d6b4d9832e104aadbcaeb19	admin	\N
56	josu	josue@gmail.com	14	scrypt:32768:8:1$iCJZ20j0Lg1It3tQ$62b2f1c36e6235a721690773f5b89cf1f10ba0ad83d26ad49d36ba6b0615fa260e7afed216a26af624026291a156d5eeebafce92b1369bceda1ebee37aa31466	user	yoga_facial
51	Luc├¡a Mendez	luciamendezterapia@gmail.com	21	scrypt:32768:8:1$mNdYB6Ih8bqn0VRc$688f4a92b00553783f64c1837ed993926e3bdbc17b7e79efeeb7e8e63a243dd7e3514dd1369d031182de4f1535470a9d3ada96b84fdbe5a35857fc2dad487343	user	yoga_facial
58	josu	josu@gmail.com	4	scrypt:32768:8:1$WZs7VbYfrKPY3H2S$8ed3c5c6a7265ec6402e75f551e56ce0388bb8dd74db12d01524281047549dc3e632111425cb14466c64fac660dffe688b832eb1c975489560dd24819ccc4133	user	casino
59	Paula Ducasa	pauladucasa@hotmail.com	9	scrypt:32768:8:1$0XzHhJOgXOj4eJSS$019bd08bed013f71ce09665c8bb81f56f56436a6e9104f64459efb0640f2e9cba8744905fad9972ade815836766b7e2e6a1a3f76282093835f8f979ff46bee21	user	yoga_facial
52	Josue Cabrera	josuegabrielc@gmail.com	\N	scrypt:32768:8:1$IqXOwb50CYiO8ubE$b2677a653ebc6faa47be22e9c054369eb76a477e8c772aa294065d5071eadf775a7d5bc20d76656e4ef327dd3245b103ea5b1c81f51caf99d0cc4ad564d43443	admin	\N
60	Talina Hern├índez	hdztalina@yahoo.com	21	scrypt:32768:8:1$r9G8ShHtEpglnID7$e19d81cea0b2b60165b98b91d10db7c65dfea3330b174b4b4d80193a59728d0c29c0e6fafaf43a64c6e10728391ca2ae489ce0d95d58e4791cbe3f989792855d	user	yoga_facial
50	Sofia	sofiapl@hotmail.com	21	scrypt:32768:8:1$1Xcq8bMmugjcmwKe$b5967a0a2857f87b343471d085f70ea67ddd566f608bb91405ec9ec4a497aa7716c399a3d402c15a881c06519053a612b3a790708d5e32ea346f312e06fb72c9	user	yoga_facial
27	Ana Santos	ana.santos1904@gmail.com	2	scrypt:32768:8:1$ix69F1IhGpdstE9S$373ec2c1df1ccbcccd7eff41a8c0d352ac63bcd9d07a1615c1654583a6e73808c84242b1cf15665e8f087fc8a61287d4d2e927d0fbe2a390edfb762d7b1442a4	user	yoga_facial
2	Eugenia de Combi	decombieugenia@gmail.com	21	scrypt:32768:8:1$9tPvaLqUlBzPc7X1$1934323f898bb01a75db51174021b37ecdda9afd98eb194e8c2ad6c37e1e2558bfe863b1b4d68e17a8eb3386f3307f3adca6c68c6efa27cad040e80406f73213	admin	\N
\.


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.sections_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.users_id_seq', 60, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: sections sections_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

