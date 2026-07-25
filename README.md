# HRFlow Platform

Internal HR + payroll tool for small teams: employee records, leave approvals, and monthly payslips.

Day-to-day this stuff often lives in spreadsheets and WhatsApp. Approvals get lost, nobody has a clear picture of who is out, and payroll is done by hand. This repo is my attempt at a small system with real rules behind it — not just CRUD forms.

> **Status:** early stage. This README describes what I am building and the rules I intend to enforce. I will update it as the code catches up so the docs stay honest.

## What I am prioritizing (and why)

The brief said one or two modules done properly beats three done shallowly. I am still planning all three because leave and payroll need employee data, but effort will go in this order:

1. **Leave management** — this is where spreadsheets usually fail. Notice periods, overlapping requests, team coverage, and stale approvals are the parts I care about most.
2. **Payroll math** — gross pay that respects unpaid leave and mid-month joiners, plus a simple tax + social security scheme that is easy to check by hand.
3. **Employee records** — enough structure to support leave and payroll (including soft deactivate so history can stay). Not trying to build a full HRIS.

If the employee side looks intentionally simple later, that is on purpose. I want leave rules and payslip numbers to be trustworthy first.

## Planned features

### Employee records
- Create and update employees (name, role, team, manager, start date, salary, employment type)
- Simple org view: who reports to whom
- Deactivate instead of delete (so payroll and leave history can remain)

### Leave management
- Request time off
- Manager approve / reject
- Leave balances per year
- Unpaid leave feeding into payroll

Problems I want the leave module to catch (and the rules I plan to use):

| Problem | Planned rule |
|---|---|
| Last-minute annual leave with no planning time | Minimum 3 calendar days notice for annual leave (sick leave exempt) |
| Someone booking overlapping dates | Block overlaps against own pending/approved leave |
| Half the team out the same week | Soft coverage check: for teams with 2+ people, no more than ~50% of active members on leave the same day |
| Requests sitting unanswered | Pending requests older than 5 business days flagged as overdue on the dashboard |
| Leave not affecting pay | Unpaid leave days reduce gross pay for that month |

I am writing the thresholds down now so they are reviewable and testable once the module exists.

### Payroll
- Generate a monthly payslip per active employee
- Gross pay prorated for mid-month joiners and unpaid leave
- Statutory deductions: flat social security + bracketed income tax
- Net pay stored on the payslip

## Architecture (target)

```
Browser (HTML / CSS / vanilla JS)
        |
        |  JSON over REST
        v
Flask API (blueprints + services)
        |
        v
PostgreSQL (SQLAlchemy + Flask-Migrate)
```

**Backend:** Flask with an app factory. Routes stay thin. Leave rules and payroll calculations live in service modules so they can be tested without HTTP.

**Frontend:** Plain HTML, CSS, and vanilla JS calling the API. No React/Vue — matching the challenge requirement.

**Database:** PostgreSQL. Expected main tables: employees, leave_requests, leave_balances, payroll_periods, payslips.

Docker Compose will be optional. The app should also run with a local venv + local Postgres.

## Business rules (design)

### Leave
- Types: annual, sick, unpaid (easy to extend later)
- Annual leave consumes balance; unpaid does not, but it hits payroll
- Sick leave skips the notice rule
- Approvals go through the employee’s manager (`manager_id`)
- Rejected / cancelled requests should not affect coverage or balances

### Payroll formula

Simplified fictional scheme — not meant to match a real country.

Assumptions:
- Pay period = calendar month
- Monthly salary on the employee record is the base figure
- Proration uses calendar days in the month (simple and predictable)

**Step 1 — Gross pay**

```
eligible_days = days in month the employee was employed
             - unpaid leave days falling in that month

gross = monthly_salary * (eligible_days / days_in_month)
```

Mid-month joiners only count from `start_date` onward. Inactive employees should be skipped on new runs.

**Step 2 — Social security**

```
social_security = gross * 0.05
```

**Step 3 — Taxable income**

```
taxable = gross - social_security
```

**Step 4 — Income tax (brackets on taxable)**

| Taxable amount | Rate |
|---|---|
| 0 – 5,000 | 0% |
| 5,001 – 15,000 | 10% on the amount above 5,000 |
| 15,001+ | 10% on 5,001–15,000, then 20% on the rest |

**Step 5 — Net**

```
net = gross - social_security - tax
```

Edge cases I plan to cover in tests:
- Employee starts mid-month
- Salary sitting on a bracket boundary
- Enough unpaid leave that gross (and tax) drop near zero
- Zero-deduction path when taxable income stays in the 0% band

## Installation

Setup instructions will land with the project scaffolding. Expected paths:

### Manual
- Python 3.11+
- PostgreSQL 14+
- venv + `pip install -r requirements.txt`
- `.env` from `.env.example`
- `flask db upgrade`, seed data, then `flask run`

### Docker
- `docker compose up --build` once compose files exist

I will fill exact commands here when the app is runnable so this section does not promise steps that are not in the repo yet.

## API overview (planned)

Base path: `/api`

### Employees
- `GET /api/employees`
- `POST /api/employees`
- `GET /api/employees/<id>`
- `PATCH /api/employees/<id>`
- `POST /api/employees/<id>/deactivate`
- `GET /api/employees/org`

### Leave
- `GET /api/leave`
- `POST /api/leave`
- `POST /api/leave/<id>/approve`
- `POST /api/leave/<id>/reject`
- `GET /api/leave/balances/<employee_id>`
- `GET /api/leave/coverage`

### Payroll
- `POST /api/payroll/generate`
- `GET /api/payroll/periods`
- `GET /api/payroll/periods/<id>/payslips`
- `GET /api/payroll/payslips/<id>`

### Dashboard
- `GET /api/dashboard`

Shapes will match whatever the frontend ends up sending. I will keep this list in sync as routes are added.

## Testing

Plan: `pytest`, focused on core logic rather than chasing full line coverage.

- Leave notice validation
- Overlap detection
- Team coverage rule
- Overdue / escalation helper
- Payroll proration (mid-month join, unpaid leave)
- Tax brackets and social security
- Bracket-boundary and near-zero gross cases

## Sample data / SQL dump

For the final submission I will include a SQL dump with a few employees/teams, leave requests in different statuses, and at least one generated payroll period.

Expected path once ready: `database/hrflow_sample.sql`

## What I would improve with more time

- Auth (login / roles) — API will start open for local demo use
- Notifications when a request goes overdue
- More realistic leave accrual and carry-over
- PDF payslip export
- Audit log for approvals and payroll runs
- Better team leave calendar UI

## Stretch goals

Only after the core modules work. Possible extras: clearer overdue indicators on the dashboard, or a quick “who’s out this week” filter. Anything stretch will be called out here so it is obvious what was extra.
