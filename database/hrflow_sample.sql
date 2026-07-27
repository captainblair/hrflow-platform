--
-- PostgreSQL database dump
--

\restrict KTwNG3nnFvgeI8JUfL7Hg33EDnJwtcbwiQidmHeGS1PBMyxAOvD70imW5BAU6U3

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    role character varying(80) NOT NULL,
    team character varying(80) NOT NULL,
    manager_id integer,
    start_date date NOT NULL,
    salary numeric(10,2) NOT NULL,
    employment_type character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: leave_balances; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.leave_balances (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    year integer NOT NULL,
    annual_allocated integer NOT NULL,
    annual_used integer NOT NULL
);


--
-- Name: leave_balances_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.leave_balances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: leave_balances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.leave_balances_id_seq OWNED BY public.leave_balances.id;


--
-- Name: leave_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.leave_requests (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status character varying(20) NOT NULL,
    reason text,
    decided_at timestamp without time zone,
    decided_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: leave_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.leave_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: leave_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.leave_requests_id_seq OWNED BY public.leave_requests.id;


--
-- Name: payroll_periods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_periods (
    id integer NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: payroll_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payroll_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payroll_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payroll_periods_id_seq OWNED BY public.payroll_periods.id;


--
-- Name: payslips; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payslips (
    id integer NOT NULL,
    period_id integer NOT NULL,
    employee_id integer NOT NULL,
    gross_pay numeric(10,2) NOT NULL,
    social_security numeric(10,2) NOT NULL,
    income_tax numeric(10,2) NOT NULL,
    net_pay numeric(10,2) NOT NULL,
    details json,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: payslips_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payslips_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payslips_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payslips_id_seq OWNED BY public.payslips.id;


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: leave_balances id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_balances ALTER COLUMN id SET DEFAULT nextval('public.leave_balances_id_seq'::regclass);


--
-- Name: leave_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_requests ALTER COLUMN id SET DEFAULT nextval('public.leave_requests_id_seq'::regclass);


--
-- Name: payroll_periods id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_periods ALTER COLUMN id SET DEFAULT nextval('public.payroll_periods_id_seq'::regclass);


--
-- Name: payslips id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payslips ALTER COLUMN id SET DEFAULT nextval('public.payslips_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
302cfe719711
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employees (id, name, role, team, manager_id, start_date, salary, employment_type, is_active, created_at) FROM stdin;
1	Grace Wanjiru	General Manager	Management	\N	2023-02-01	95000.00	full_time	t	2026-07-27 11:25:18.540119
2	Brian Otieno	Engineering Lead	Engineering	1	2023-09-18	75000.00	full_time	t	2026-07-27 11:25:18.540119
3	Alice Achieng	HR Officer	Operations	1	2024-05-06	48000.00	full_time	t	2026-07-27 11:25:18.540119
4	Faith Njeri	Backend Engineer	Engineering	2	2024-11-04	55000.00	full_time	t	2026-07-27 11:25:18.540119
5	Kevin Mutua	Frontend Engineer	Engineering	2	2025-03-10	52000.00	full_time	t	2026-07-27 11:25:18.540119
6	Daniel Kiprop	Accountant	Operations	1	2026-07-15	38000.00	part_time	t	2026-07-27 11:25:18.540119
7	Wycliffe Barasa	Support Assistant	Operations	3	2024-08-12	30000.00	contract	t	2026-07-27 11:25:18.540119
\.


--
-- Data for Name: leave_balances; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.leave_balances (id, employee_id, year, annual_allocated, annual_used) FROM stdin;
1	1	2026	21	0
2	2	2026	21	0
3	3	2026	21	0
4	4	2026	21	0
5	5	2026	21	0
6	6	2026	21	0
7	7	2026	21	0
\.


--
-- Data for Name: leave_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.leave_requests (id, employee_id, leave_type, start_date, end_date, status, reason, decided_at, decided_by, created_at) FROM stdin;
1	4	annual	2026-08-06	2026-08-10	pending	Family visit upcountry	\N	\N	2026-07-27 11:25:18.540119
2	5	annual	2026-08-16	2026-08-18	pending	Long weekend away	\N	\N	2026-07-13 11:25:18.55256
3	3	sick	2026-07-21	2026-07-22	approved	Flu	2026-07-21 11:25:18.552579	1	2026-07-27 11:25:18.540119
4	5	unpaid	2026-07-24	2026-07-26	approved	Personal matters	2026-07-23 11:25:18.552602	2	2026-07-27 11:25:18.540119
\.


--
-- Data for Name: payroll_periods; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payroll_periods (id, year, month, status, created_at) FROM stdin;
1	2026	7	draft	2026-07-27 11:25:50.45441
2	2026	2	finalized	2026-07-27 11:26:18.192918
\.


--
-- Data for Name: payslips; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payslips (id, period_id, employee_id, gross_pay, social_security, income_tax, net_pay, details, created_at) FROM stdin;
8	2	3	48000.00	2400.00	7120.00	38480.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 48000.0, "gross_pay": 48000.0, "social_security": 2400.0, "taxable_income": 45600.0, "income_tax": 7120.0, "net_pay": 38480.0}	2026-07-27 11:26:18.192918
9	2	2	75000.00	3750.00	12250.00	59000.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 75000.0, "gross_pay": 75000.0, "social_security": 3750.0, "taxable_income": 71250.0, "income_tax": 12250.0, "net_pay": 59000.0}	2026-07-27 11:26:18.192918
10	2	4	55000.00	2750.00	8450.00	43800.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 55000.0, "gross_pay": 55000.0, "social_security": 2750.0, "taxable_income": 52250.0, "income_tax": 8450.0, "net_pay": 43800.0}	2026-07-27 11:26:18.192918
11	2	1	95000.00	4750.00	16050.00	74200.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 95000.0, "gross_pay": 95000.0, "social_security": 4750.0, "taxable_income": 90250.0, "income_tax": 16050.0, "net_pay": 74200.0}	2026-07-27 11:26:18.192918
12	2	5	52000.00	2600.00	7880.00	41520.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 52000.0, "gross_pay": 52000.0, "social_security": 2600.0, "taxable_income": 49400.0, "income_tax": 7880.0, "net_pay": 41520.0}	2026-07-27 11:26:18.192918
13	2	7	30000.00	1500.00	3700.00	24800.00	{"year": 2026, "month": 2, "days_in_month": 28, "employed_days": 28, "unpaid_leave_days": 0, "eligible_days": 28, "monthly_salary": 30000.0, "gross_pay": 30000.0, "social_security": 1500.0, "taxable_income": 28500.0, "income_tax": 3700.0, "net_pay": 24800.0}	2026-07-27 11:26:18.192918
14	1	3	48000.00	2400.00	7120.00	38480.00	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 0, "eligible_days": 31, "monthly_salary": 48000.0, "gross_pay": 48000.0, "social_security": 2400.0, "taxable_income": 45600.0, "income_tax": 7120.0, "net_pay": 38480.0}	2026-07-27 11:40:25.304163
15	1	2	75000.00	3750.00	12250.00	59000.00	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 0, "eligible_days": 31, "monthly_salary": 75000.0, "gross_pay": 75000.0, "social_security": 3750.0, "taxable_income": 71250.0, "income_tax": 12250.0, "net_pay": 59000.0}	2026-07-27 11:40:25.304163
16	1	6	20838.71	1041.94	1959.35	17837.42	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 17, "unpaid_leave_days": 0, "eligible_days": 17, "monthly_salary": 38000.0, "gross_pay": 20838.71, "social_security": 1041.94, "taxable_income": 19796.77, "income_tax": 1959.35, "net_pay": 17837.42}	2026-07-27 11:40:25.304163
17	1	4	55000.00	2750.00	8450.00	43800.00	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 0, "eligible_days": 31, "monthly_salary": 55000.0, "gross_pay": 55000.0, "social_security": 2750.0, "taxable_income": 52250.0, "income_tax": 8450.0, "net_pay": 43800.0}	2026-07-27 11:40:25.304163
18	1	1	95000.00	4750.00	16050.00	74200.00	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 0, "eligible_days": 31, "monthly_salary": 95000.0, "gross_pay": 95000.0, "social_security": 4750.0, "taxable_income": 90250.0, "income_tax": 16050.0, "net_pay": 74200.0}	2026-07-27 11:40:25.304163
19	1	5	46967.74	2348.39	6923.87	37695.48	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 3, "eligible_days": 28, "monthly_salary": 52000.0, "gross_pay": 46967.74, "social_security": 2348.39, "taxable_income": 44619.35, "income_tax": 6923.87, "net_pay": 37695.48}	2026-07-27 11:40:25.304163
20	1	7	30000.00	1500.00	3700.00	24800.00	{"year": 2026, "month": 7, "days_in_month": 31, "employed_days": 31, "unpaid_leave_days": 0, "eligible_days": 31, "monthly_salary": 30000.0, "gross_pay": 30000.0, "social_security": 1500.0, "taxable_income": 28500.0, "income_tax": 3700.0, "net_pay": 24800.0}	2026-07-27 11:40:25.304163
\.


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employees_id_seq', 7, true);


--
-- Name: leave_balances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.leave_balances_id_seq', 7, true);


--
-- Name: leave_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.leave_requests_id_seq', 4, true);


--
-- Name: payroll_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payroll_periods_id_seq', 2, true);


--
-- Name: payslips_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payslips_id_seq', 20, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: leave_balances leave_balances_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT leave_balances_pkey PRIMARY KEY (id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (id);


--
-- Name: payroll_periods payroll_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_periods
    ADD CONSTRAINT payroll_periods_pkey PRIMARY KEY (id);


--
-- Name: payslips payslips_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payslips
    ADD CONSTRAINT payslips_pkey PRIMARY KEY (id);


--
-- Name: leave_balances uq_balance_employee_year; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT uq_balance_employee_year UNIQUE (employee_id, year);


--
-- Name: payslips uq_payslip_period_employee; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payslips
    ADD CONSTRAINT uq_payslip_period_employee UNIQUE (period_id, employee_id);


--
-- Name: payroll_periods uq_period_year_month; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_periods
    ADD CONSTRAINT uq_period_year_month UNIQUE (year, month);


--
-- Name: employees employees_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id);


--
-- Name: leave_balances leave_balances_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT leave_balances_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: leave_requests leave_requests_decided_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_decided_by_fkey FOREIGN KEY (decided_by) REFERENCES public.employees(id);


--
-- Name: leave_requests leave_requests_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: payslips payslips_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payslips
    ADD CONSTRAINT payslips_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: payslips payslips_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payslips
    ADD CONSTRAINT payslips_period_id_fkey FOREIGN KEY (period_id) REFERENCES public.payroll_periods(id);


--
-- PostgreSQL database dump complete
--

\unrestrict KTwNG3nnFvgeI8JUfL7Hg33EDnJwtcbwiQidmHeGS1PBMyxAOvD70imW5BAU6U3

