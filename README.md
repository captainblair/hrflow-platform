# HRFlow Platform

A small internal tool for employee records, leave approvals, and monthly payroll.

Teams often handle this over spreadsheets and chat. Requests get lost, coverage is unclear, and payroll is calculated by hand. HRFlow keeps those workflows in one place with rules that actually matter — notice periods, team coverage, and payslip math you can verify.

## Focus

I am building all three modules because they depend on each other, but the depth goes here first:

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
Browser (HTML, CSS, vanilla JS)
        |
        |  REST / JSON
        v
Flask API (routes + services)
        |
        v
PostgreSQL (SQLAlchemy, Flask-Migrate)
```

Backend keeps route handlers thin and puts leave/payroll logic in services so the important rules are easy to test.

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

Exact commands will be filled in once the project scaffolding is in place. Expected flow:

### Manual
1. Python 3.11+ and PostgreSQL 14+
2. Create a virtualenv and install `requirements.txt`
3. Copy `.env.example` to `.env` and set `DATABASE_URL`
4. Run migrations, seed sample data, start the app with Flask

### Docker
```bash
docker compose up --build
```

## API

Base path: `/api`

**Employees**
- `GET /api/employees`
- `POST /api/employees`
- `GET /api/employees/<id>`
- `PATCH /api/employees/<id>`
- `POST /api/employees/<id>/deactivate`
- `GET /api/employees/org`

**Leave**
- `GET /api/leave`
- `POST /api/leave`
- `POST /api/leave/<id>/approve`
- `POST /api/leave/<id>/reject`
- `GET /api/leave/balances/<employee_id>`
- `GET /api/leave/coverage`

**Payroll**
- `POST /api/payroll/generate`
- `GET /api/payroll/periods`
- `GET /api/payroll/periods/<id>/payslips`
- `GET /api/payroll/payslips/<id>`

**Dashboard**
- `GET /api/dashboard`

## Tests

```bash
pytest
```

Coverage targets the core logic:
- Notice period
- Overlaps
- Team coverage
- Overdue requests
- Payroll proration
- Tax and social security, including edge cases

## Sample data

Final submission will include a SQL dump under `database/hrflow_sample.sql` with a few employees, leave requests in different statuses, and one generated payroll period.

## Later improvements

- Authentication and roles
- Notifications for overdue leave requests
- Proper accrual and carry-over for annual leave
- PDF payslips
- Audit trail for approvals and payroll runs
- Team leave calendar

Stretch work only after the core modules are solid. If I add anything extra (for example clearer overdue indicators), it will be listed here.
