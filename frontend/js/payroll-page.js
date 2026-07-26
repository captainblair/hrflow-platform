async function loadPayslips(periodId, label) {
  const root = document.getElementById("payslip-table");
  const badge = document.getElementById("payslip-period-label");
  badge.textContent = label;
  root.className = "loading";
  root.textContent = "Loading payslips…";

  try {
    const payslips = await Api.get(`/api/payroll/periods/${periodId}/payslips`);
    if (!payslips.length) {
      root.className = "empty";
      root.innerHTML =
        "<strong>No payslips</strong>This period has no payslip rows.";
      return;
    }

    root.className = "";
    root.innerHTML = `
      <div class="table-wrap">
        <table class="data">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Gross</th>
              <th>Tax</th>
              <th>Net</th>
              <th>Eligible days</th>
            </tr>
          </thead>
          <tbody>
            ${payslips
              .map(
                (item) => `
              <tr>
                <td><strong>${item.employee_name}</strong></td>
                <td>${formatMoney(item.gross_pay)}</td>
                <td>${formatMoney(item.income_tax)}</td>
                <td><strong>${formatMoney(item.net_pay)}</strong></td>
                <td class="muted">${(item.details && item.details.eligible_days) || "—"}</td>
              </tr>`
              )
              .join("")}
          </tbody>
        </table>
      </div>`;
  } catch (error) {
    root.className = "flash error";
    root.textContent = error.message || "Could not load payslips.";
  }
}

function renderPeriods(periods) {
  const root = document.getElementById("period-table");
  if (!periods.length) {
    root.innerHTML =
      '<div class="empty"><strong>No payroll periods</strong>Generate one when controls are enabled.</div>';
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
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${periods
            .map((period) => {
              const label = `${period.year}-${String(period.month).padStart(2, "0")}`;
              return `
              <tr>
                <td><strong>${label}</strong></td>
                <td>${statusBadge(period.status)}</td>
                <td>${period.payslip_count}</td>
                <td>
                  <button class="btn secondary btn-sm" type="button"
                    data-period-id="${period.id}" data-period-label="${label}">
                    View payslips
                  </button>
                </td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>`;

  root.querySelectorAll("[data-period-id]").forEach((button) => {
    button.addEventListener("click", () => {
      loadPayslips(
        button.getAttribute("data-period-id"),
        button.getAttribute("data-period-label")
      );
    });
  });
}

async function loadPayrollPage() {
  const errorBox = document.getElementById("payroll-error");
  try {
    const periods = await Api.get("/api/payroll/periods");
    renderPeriods(periods);
    if (periods.length) {
      const latest = periods[0];
      const label = `${latest.year}-${String(latest.month).padStart(2, "0")}`;
      loadPayslips(latest.id, label);
    }
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error.message || "Could not load payroll data.";
  }
}

document.addEventListener("DOMContentLoaded", loadPayrollPage);
