function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function addDaysISO(days) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function coversDate(leave, day) {
  return leave.start_date <= day && leave.end_date >= day;
}

function renderRecentLeave(items) {
  const root = document.getElementById("recent-leave");
  if (!items.length) {
    root.innerHTML =
      '<div class="empty"><strong>No leave requests yet</strong>New requests will show up here.</div>';
    return;
  }

  root.innerHTML = items
    .slice(0, 6)
    .map(
      (item) => `
      <div class="list-item">
        <div>
          <div class="title">${item.employee_name}</div>
          <div class="meta">${item.leave_type} · ${formatDate(item.start_date)} → ${formatDate(item.end_date)}</div>
        </div>
        ${statusBadge(item.status)}${item.is_overdue ? ' <span class="badge warning">Overdue</span>' : ""}
      </div>`
    )
    .join("");
}

function renderUpcoming(items) {
  const root = document.getElementById("upcoming-leave");
  const start = todayISO();
  const end = addDaysISO(14);
  const upcoming = items
    .filter(
      (item) =>
        item.status === "approved" &&
        item.end_date >= start &&
        item.start_date <= end
    )
    .sort((a, b) => a.start_date.localeCompare(b.start_date));

  if (!upcoming.length) {
    root.innerHTML =
      '<div class="empty"><strong>No upcoming leave</strong>Approved leave in the next two weeks will appear here.</div>';
    return;
  }

  root.className = "calendar-list";
  root.innerHTML = upcoming
    .slice(0, 6)
    .map((item) => {
      const label = formatDate(item.start_date).slice(5).replace("-", "/");
      return `
        <div class="day">
          <div class="date-chip">${label}</div>
          <div>
            <div class="title">${item.employee_name}</div>
            <div class="meta">${item.leave_type} · until ${formatDate(item.end_date)}</div>
          </div>
        </div>`;
    })
    .join("");
}

function renderPayrollRuns(periods) {
  const root = document.getElementById("payroll-runs");
  if (!periods.length) {
    root.innerHTML =
      '<div class="empty"><strong>No payroll runs yet</strong>Generate a period from the Payroll page.</div>';
    return;
  }

  root.innerHTML = `
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th>Period</th>
            <th>Status</th>
            <th>Payslips</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          ${periods
            .slice(0, 5)
            .map(
              (period) => `
            <tr>
              <td>${period.year}-${String(period.month).padStart(2, "0")}</td>
              <td>${statusBadge(period.status)}</td>
              <td>${period.payslip_count}</td>
              <td class="muted">${formatDate(period.created_at)}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

async function loadDashboard() {
  const errorBox = document.getElementById("dashboard-error");

  try {
    const [employees, leave, periods] = await Promise.all([
      Api.get("/api/employees"),
      Api.get("/api/leave"),
      Api.get("/api/payroll/periods"),
    ]);

    const active = employees.filter((item) => item.is_active);
    const pending = leave.filter((item) => item.status === "pending");
    const overdue = pending.filter((item) => item.is_overdue);
    const today = todayISO();
    const outToday = new Set(
      leave
        .filter((item) => item.status === "approved" && coversDate(item, today))
        .map((item) => item.employee_id)
    );

    document.getElementById("kpi-employees").textContent = String(employees.length);
    document.getElementById("kpi-employees-meta").textContent =
      `${active.length} active · ${employees.length - active.length} inactive`;

    document.getElementById("kpi-out").textContent = String(outToday.size);

    document.getElementById("kpi-pending").textContent = String(pending.length);
    document.getElementById("kpi-pending-meta").textContent =
      overdue.length ? `${overdue.length} overdue` : "No overdue requests";

    document.getElementById("kpi-payroll").textContent = String(periods.length);
    const latest = periods[0];
    document.getElementById("kpi-payroll-meta").textContent = latest
      ? `Latest ${latest.year}-${String(latest.month).padStart(2, "0")} · ${latest.payslip_count} slips`
      : "No periods generated";

    renderRecentLeave(leave);
    renderUpcoming(leave);
    renderPayrollRuns(periods);
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error.message || "Could not load dashboard data.";
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);
