function renderLeaveList(items, emptyTitle, emptyBody) {
  if (!items.length) {
    return `<div class="empty"><strong>${emptyTitle}</strong>${emptyBody}</div>`;
  }

  return items
    .map(
      (item) => `
      <div class="list-item">
        <div>
          <div class="title">${item.employee_name}</div>
          <div class="meta">${item.leave_type} · ${formatDate(item.start_date)} → ${formatDate(item.end_date)}</div>
        </div>
        <div>
          ${leaveStatusBadges(item)}
        </div>
      </div>`
    )
    .join("");
}

function renderUpcoming(items) {
  const root = document.getElementById("upcoming-leave");
  if (!items.length) {
    root.className = "";
    root.innerHTML =
      '<div class="empty"><strong>No upcoming leave</strong>Approved leave in the next two weeks will appear here.</div>';
    return;
  }

  root.className = "calendar-list";
  root.innerHTML = items
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

function renderBalances(items, year) {
  const root = document.getElementById("leave-balances");
  document.getElementById("balance-year").textContent = String(year);

  if (!items.length) {
    root.innerHTML =
      '<div class="empty"><strong>No balances</strong>Balances appear once employees are seeded.</div>';
    return;
  }

  root.innerHTML = `
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Used</th>
            <th>Remaining</th>
          </tr>
        </thead>
        <tbody>
          ${items
            .map(
              (item) => `
            <tr>
              <td>${item.employee_name || "Employee #" + item.employee_id}</td>
              <td>${item.annual_used}/${item.annual_allocated}</td>
              <td><strong>${item.annual_remaining}</strong></td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
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
          </tr>
        </thead>
        <tbody>
          ${periods
            .map(
              (period) => `
            <tr>
              <td>${period.year}-${String(period.month).padStart(2, "0")}</td>
              <td>${statusBadge(period.status)}</td>
              <td>${period.payslip_count}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

function renderPayslips(payslips, latestPeriod) {
  const root = document.getElementById("recent-payslips");
  const badge = document.getElementById("payslip-period-badge");
  badge.textContent = latestPeriod || "No period";

  if (!payslips.length) {
    root.innerHTML =
      '<div class="empty"><strong>No payslips</strong>Generate payroll to see slips here.</div>';
    return;
  }

  root.innerHTML = `
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Gross</th>
            <th>Net</th>
          </tr>
        </thead>
        <tbody>
          ${payslips
            .map(
              (item) => `
            <tr>
              <td>${item.employee_name}</td>
              <td>${formatMoney(item.gross_pay)}</td>
              <td><strong>${formatMoney(item.net_pay)}</strong></td>
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
    const data = await Api.get("/api/dashboard");
    const summary = data.summary;

    document.getElementById("kpi-employees").textContent = String(
      summary.total_employees
    );
    document.getElementById("kpi-employees-meta").textContent =
      `${summary.active_employees} active · ${summary.inactive_employees} inactive`;

    document.getElementById("kpi-out").textContent = String(
      summary.employees_on_leave_today
    );

    document.getElementById("kpi-pending").textContent = String(
      summary.pending_leave_requests
    );
    document.getElementById("kpi-pending-meta").textContent =
      summary.overdue_leave_requests
        ? `${summary.overdue_leave_requests} overdue`
        : "No overdue requests";

    document.getElementById("kpi-payroll").textContent = String(
      summary.payroll_periods
    );
    document.getElementById("kpi-payroll-meta").textContent = summary.latest_period
      ? `Latest ${summary.latest_period} · ${summary.latest_payslip_count} slips`
      : "No periods generated";

    document.getElementById("out-today-badge").textContent = data.as_of;

    document.getElementById("pending-approvals").innerHTML = renderLeaveList(
      data.pending_approvals,
      "No pending approvals",
      "New leave requests waiting on managers will show here."
    );
    document.getElementById("out-today").innerHTML = renderLeaveList(
      data.out_today,
      "Nobody out today",
      "Approved leave covering today will list here."
    );

    renderBalances(data.leave_balances, data.as_of.slice(0, 4));
    renderUpcoming(data.upcoming_leave);
    renderPayrollRuns(data.payroll_periods);
    renderPayslips(data.recent_payslips, summary.latest_period);
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error.message || "Could not load dashboard data.";
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);
