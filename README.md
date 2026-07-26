# HRFlow Platform

An internal HR and Payroll management platform for employee records, leave approvals, and monthly payslips.

Teams often handle this over spreadsheets and chat. Requests get lost, coverage is unclear, and payroll is calculated by hand. HRFlow keeps those workflows in one place with enforceable rules — notice periods, team coverage, and payslip math that can be verified.

## Project Status

Currently under active development as part of a Software Engineering practical assessment.

**Implemented**
- Flask application factory
- Environment-based configuration
- Database models (employees, leave, payroll)
- Initial Alembic migration
- Seed command with sample data
- API health endpoint
- Employee records API (CRUD, deactivate, org tree)
- Leave management API (request, approve/reject, balances)
- Leave business rules (notice, overlaps, coverage, overdue)
- Payroll calculation engine (proration, tax, social security)
- Payslip generation and payroll periods
- Backend tests for core leave and payroll logic
- Frontend shell (pages, shared styles, API client)

**Defined**
- Project architecture
- Core business workflows

**Upcoming**
- Dashboard, employee, leave, and payroll UI
- Docker setup

## Tech Stack

**Backend**
- Flask
- SQLAlchemy
- Flask-Migrate

**Database**
- PostgreSQL

**Frontend**
- HTML
- CSS
- Vanilla JavaScript

**Testing**
- Pytest

**DevOps**
- Docker (optional local deployment)

## Focus

HRFlow implements all three modules because they depend on each other operationally. Development prioritizes business-critical workflows first:

1. **Leave** — approvals, balances, and safeguards (short notice, overlaps, under-covered teams, stalled requests)
2. **Payroll** — monthly payslips with proration, unpaid leave deductions, and a simple tax + social security scheme
3. **Employees** — records and reporting lines solid enough to support leave and payroll, including soft deactivation so history stays intact

Employee management stays lean on purpose. Leave rules and payroll correctness are the parts worth getting right.

## Features

### Employees
- Create and update records (name, role, team, manager, start date, salary, employment type)
- Org view showing who reports to whom
- Deactivate instead of delete

### Leave
- Request time off
- Manager approve or reject
- Annual balances tracked per year
- Unpaid leave reduces that month’s gross pay

Rules:

| Situation | Rule |
|---|---|
| Annual leave booked too late | At least 3 calendar days notice (sick leave exempt) |
| Overlapping dates for the same person | Blocked against pending or approved leave |
| Too many people out on the same team | Teams of 2+ capped at about 50% of active members off on the same day |
| Requests left unanswered | Pending longer than 5 business days marked overdue on the dashboard |
| Unpaid time off | Days fall out of eligible pay days for the month |

### Payroll
- Generate a payslip per active employee for a given month
- Gross pay prorated for mid-month starters and unpaid leave
- Flat social security plus bracketed income tax
- Net pay stored with the calculation breakdown

## Architecture

```
Browser (HTML, CSS, Vanilla JS)
              |
              | REST / JSON
              v
Flask API
(routes/controllers)
              |
              v
Business Services
(leave rules + payroll calculations)
              |
              v
PostgreSQL
(SQLAlchemy + Flask-Migrate)
```

Route handlers stay thin. Leave rules and payroll calculations live in a service layer so the important logic is easy to test.

Frontend is plain HTML/CSS/JS — no React or Vue.

Docker is optional. Local run with a virtualenv and PostgreSQL is the default path.

## Leave rules

- Types: annual, sick, unpaid
- Annual leave uses balance; unpaid does not, but it affects payroll
- Sick leave skips the notice check
- Approvals go through the employee’s manager
- Rejected or cancelled requests do not change coverage or balances

## Payroll formula

Simplified scheme for this project — not tied to a real country’s tax code.

Assumptions:
- Pay period is a calendar month
- Base figure is the employee’s monthly salary
- Proration uses calendar days in the month

**Gross**

```
eligible_days = days employed in the month
              - unpaid leave days in that month

gross = monthly_salary * (eligible_days / days_in_month)
```

Mid-month joiners count from `start_date`. Inactive employees are skipped on new runs.

**Social security**

```
social_security = gross * 0.05
```

**Taxable income**

```
taxable = gross - social_security
```

**Income tax**

| Taxable amount | Rate |
|---|---|
| 0 – 5,000 | 0% |
| 5,001 – 15,000 | 10% on the amount above 5,000 |
| 15,001+ | 10% on 5,001–15,000, then 20% on the rest |

**Net**

```
net = gross - social_security - tax
```

Cases covered in tests:
- Mid-month start date
- Salary on a bracket boundary
- Heavy unpaid leave bringing gross near zero
- Taxable income that stays in the 0% band

## Setup

### Manual
Requirements: Python 3.11+ and PostgreSQL 14+.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and create the local environment file:

```bash
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

Update `DATABASE_URL` in `.env` with local PostgreSQL credentials. If the password contains special characters such as `@`, URL-encode them (for example `@` becomes `%40`).

Create the database once:

```sql
CREATE DATABASE hrflow;
```

Apply migrations and load sample data:

```bash
flask db upgrade
flask seed
```

Start the development server:

```bash
python run.py
```

The app UI is available at `http://127.0.0.1:5000/`.

The API health check is available at `http://127.0.0.1:5000/api/health`.

### Docker
Docker support is planned for a later phase.

## Planned API Structure

Base path: `/api`

**Employees**
- `GET /api/employees`
- `POST /api/employees`
- `GET /api/employees/<id>`
- `PATCH /api/employees/<id>`
- `POST /api/employees/<id>/deactivate`
- `GET /api/employees/org`

**Leave**
- `GET /api/leave` (filters: `status`, `employee_id`, `overdue`)
- `POST /api/leave`
- `POST /api/leave/<id>/approve`
- `POST /api/leave/<id>/reject`
- `GET /api/leave/balances/<employee_id>`
- `GET /api/leave/coverage?date=YYYY-MM-DD&team=...`

**Payroll**
- `POST /api/payroll/preview` — calculate without saving
- `POST /api/payroll/generate` — create/regenerate draft period + payslips
- `GET /api/payroll/periods`
- `GET /api/payroll/periods/<id>/payslips`
- `POST /api/payroll/periods/<id>/finalize`
- `GET /api/payroll/payslips/<id>`

**Dashboard**
- `GET /api/dashboard`

## Tests

Install development dependencies, then run the suite:

```bash
pip install -r requirements-dev.txt
pytest
```

The current suite contains 25 tests covering:
- Notice period
- Overlaps
- Team coverage
- Overdue requests
- Manager approval and annual balance deductions
- Payroll proration
- Tax and social security, including edge cases
- Payroll generation, draft regeneration, and finalization

## Sample data

The final submission includes a SQL dump under `database/hrflow_sample.sql` with a few employees, leave requests in different statuses, and one generated payroll period.

## Screenshots

Screenshots of the dashboard, leave workflow, and payroll views will be added here once the frontend is in place.

## Later improvements

- Authentication and roles
- Notifications for overdue leave requests
- Proper accrual and carry-over for annual leave
- PDF payslips
- Audit trail for approvals and payroll runs
- Team leave calendar
- CI/CD pipeline integration
- Cloud deployment configuration

Stretch work only after the core modules are solid. Extra quality-of-life features (for example clearer overdue indicators) will be listed here if added.
