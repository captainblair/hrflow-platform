# HRFlow Platform

Small internal tool for employee records, leave approvals, and monthly payroll.

Most teams I have seen still run this stuff on spreadsheets and WhatsApp. Requests get lost, nobody knows who is actually out, and payroll gets calculated by hand (and sometimes wrong). This project is a tighter version of that workflow with real rules behind it, not just forms that save rows.

## What I prioritized (and why)

The brief said it is better to do one or two modules properly than all three shallowly. I still built all three because they depend on each other, but I put the most effort into:

1. **Leave management** — this is where spreadsheets fall apart. I spent time on notice periods, overlapping requests, team coverage, and stale approvals.
2. **Payroll math** — gross pay that respects unpaid leave and mid-month joiners, plus a simple tax + social security scheme that is easy to verify.
3. **Employee records** — enough to support leave and payroll (including soft deactivate so history stays intact). Not a full HRIS.

If something looks deliberately simple on the employee side, that was intentional. I wanted the leave rules and payslip numbers to be trustworthy first.

## Features

### Employee records
- Create and update employees (name, role, team, manager, start date, salary, employment type)
- Simple org view: who reports to whom
- Deactivate instead of delete (payslips and leave history keep working)

### Leave management
- Employees request time off
- Managers approve or reject
- Leave balances tracked per year
- Unpaid leave feeds into payroll deductions

Rules I built in (problems I kept hitting when thinking through real leave):

| Problem | What I did |
|---|---|
| Last-minute annual leave with no planning time | Minimum 3 calendar days notice for annual leave (sick leave is exempt) |
| Someone booking overlapping dates | Block overlaps against own pending/approved leave |
| Half the team disappearing on the same week | Soft coverage check: for teams with 2+ people, no more than ~50% of active members on leave the same day |
| Requests sitting forever | Pending requests older than 5 business days show up as overdue / escalated on the dashboard |
| Leave not affecting pay | Unpaid leave days reduce gross pay for that month |

Thresholds are documented here on purpose so reviewers know what to expect when clicking through.

### Payroll
- Generate a monthly payslip per active employee
- Gross pay prorated for mid-month joiners and unpaid leave
- Statutory deductions: flat social security + bracketed income tax
- Net pay stored on the payslip

## Architecture

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

**Backend:** Flask app with an app factory. Routes stay thin. Leave rules and payroll calculations live in service modules so they are testable without going through HTTP.

**Frontend:** Plain HTML pages, one CSS file, vanilla JS modules that call the API. No React/Vue — matching the challenge requirement.

**Database:** PostgreSQL. Main tables are employees, leave_requests, leave_balances, payroll_periods, and payslips.

Docker Compose is optional. The app also runs fine with a local venv + local Postgres.

## Business rules

### Leave
- Leave types: annual, sick, unpaid (extendable later)
- Annual leave consumes balance; unpaid does not, but it hits payroll
- Sick leave skips the notice rule
- Only managers (or a designated approver path via manager_id) can approve/reject for their reports
- Rejected / cancelled requests do not affect coverage or balances

### Payroll formula

This is a simplified fictional scheme. It is not meant to match a real country.

Assumptions:
- Pay period = calendar month
- Monthly salary is the base figure stored on the employee
- Working/pay days for proration use calendar days in the month (kept simple and predictable)

**Step 1 — Gross pay**

```
eligible_days = days in month the employee was employed
             - unpaid leave days falling in that month

gross = monthly_salary * (eligible_days / days_in_month)
```

Mid-month joiners only count days from `start_date` onward. Inactive employees are skipped for new runs.

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

Edge cases I specifically handled in code/tests:
- Employee starts mid-month
- Salary sitting right on a bracket boundary
- Month with enough unpaid leave that gross (and therefore tax) collapses toward zero
- Zero-deduction path when taxable income stays in the 0% band

## Installation

### Option A — Manual (recommended for day-to-day work)

Requirements:
- Python 3.11+
- PostgreSQL 14+
- Node is not required

```bash
# 1. Clone
git clone <your-repo-url>
cd hrflow-platform

# 2. Backend env
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# 3. Database
createdb hrflow
# or create it in pgAdmin / psql however you usually do

# 4. Environment
cp .env.example .env
# edit DATABASE_URL if needed

# 5. Migrate + seed
flask db upgrade
flask seed   # or python -m scripts.seed, depending on final setup

# 6. Run
flask run
# app should be on http://127.0.0.1:5000
```

### Option B — Docker

```bash
docker compose up --build
```

This starts Postgres + the app. See `docker-compose.yml` for ports and env defaults.

After first boot you may still need to run migrations inside the container if they are not applied automatically — that will be noted in the compose setup once it is finalized.

## API overview

Base path: `/api`

### Employees
- `GET /api/employees` — list (supports active filter)
- `POST /api/employees` — create
- `GET /api/employees/<id>` — detail
- `PATCH /api/employees/<id>` — update
- `POST /api/employees/<id>/deactivate` — soft deactivate
- `GET /api/employees/org` — reporting tree

### Leave
- `GET /api/leave` — list requests (filters: status, employee, overdue)
- `POST /api/leave` — submit request
- `POST /api/leave/<id>/approve`
- `POST /api/leave/<id>/reject`
- `GET /api/leave/balances/<employee_id>`
- `GET /api/leave/coverage?date=YYYY-MM-DD&team=...` — coverage helper used by rules/UI

### Payroll
- `POST /api/payroll/generate` — body: `{ "year": 2026, "month": 7 }`
- `GET /api/payroll/periods`
- `GET /api/payroll/periods/<id>/payslips`
- `GET /api/payroll/payslips/<id>`

### Dashboard
- `GET /api/dashboard` — pending approvals, people currently out, balances snapshot, recent payslips

Exact request/response shapes live with the route handlers and will stay consistent with what the frontend sends.

## Testing

```bash
pytest
```

Focus is on core logic, not chasing 100% line coverage:
- Leave notice validation
- Overlap detection
- Team coverage rule
- Overdue / escalation helper
- Payroll proration (mid-month join, unpaid leave)
- Tax brackets and social security
- Bracket-boundary and near-zero gross cases

UI and thin route wiring are mostly checked manually.

## Sample data / SQL dump

Submission includes a SQL dump with:
- A few employees across teams with managers set
- Leave requests in different statuses
- At least one generated payroll period with payslips

Path (once generated): `database/hrflow_sample.sql`

## What I would improve with more time

- Proper auth (login, roles). Right now the API is open for demo/local use.
- Email / in-app notifications when a request goes overdue
- More realistic leave accrual (pro-rata by start date, carry-over rules)
- Export payslips to PDF
- Audit log for approve/reject and payroll finalization
- Better calendar UI for team leave

## Stretch ideas (only if core stays solid)

I may add one small quality-of-life thing if time allows (for example a clearer overdue badge on the dashboard, or a one-click "who's out this week" filter). Anything stretch gets called out here so it is obvious what was extra vs core.

---

Built as a practical exercise for an internal HR + payroll workflow. If something in this README drifts from the code, trust the code and open an issue / note — I tried to keep both aligned.
