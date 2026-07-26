let allPeriods = [];
let currentPayslips = [];
let selectedPeriod = null;

function showError(message) {
  const box = document.getElementById("payroll-error");
  document.getElementById("payroll-ok").hidden = true;
  box.hidden = false;
  box.textContent = message;
}

function showOk(message) {
  const box = document.getElementById("payroll-ok");
  document.getElementById("payroll-error").hidden = true;
  box.hidden = false;
  box.textContent = message;
}

function clearMessages() {
  document.getElementById("payroll-error").hidden = true;
  document.getElementById("payroll-ok").hidden = true;
}

function fillMonthOptions() {
  const select = document.getElementById("pay-month");
  const now = new Date();
  select.innerHTML = Array.from({ length: 12 }, (_, index) => {
    const month = index + 1;
    const selected = month === now.getMonth() + 1 ? " selected" : "";
    return `<option value="${month}"${selected}>${month}</option>`;
  }).join("");
  document.getElementById("pay-year").value = now.getFullYear();
}

function filteredPayslips() {
  const q = document.getElementById("payslip-search").value.trim().toLowerCase();
  if (!q) return currentPayslips;
  return currentPayslips.filter((item) =>
    (item.employee_name || "").toLowerCase().includes(q)
  );
}

function renderPayslipTable() {
  const root = document.getElementById("payslip-table");
  const items = filteredPayslips();

  if (!selectedPeriod) {
    root.className = "empty";
    root.innerHTML =
      "<strong>No period selected</strong>Choose a payroll run to inspect payslips.";
    return;
  }

  if (!items.length) {
    root.className = "empty";
    root.innerHTML =
      "<strong>No matching payslips</strong>Try a different name filter.";
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
            <th>Social sec.</th>
            <th>Tax</th>
            <th>Net</th>
            <th>Days</th>
          </tr>
        </thead>
        <tbody>
          ${items
            .map((item) => {
              const details = item.details || {};
              return `
              <tr>
                <td>
                  <strong>${item.employee_name}</strong>
                  <div class="meta muted">
                    unpaid ${details.unpaid_leave_days ?? 0} · employed ${details.employed_days ?? "—"}
                  </div>
                </td>
                <td>${formatMoney(item.gross_pay)}</td>
                <td>${formatMoney(item.social_security)}</td>
                <td>${formatMoney(item.income_tax)}</td>
                <td><strong>${formatMoney(item.net_pay)}</strong></td>
                <td class="muted">${details.eligible_days ?? "—"}/${details.days_in_month ?? "—"}</td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>`;
}

async function loadPayslips(period) {
  selectedPeriod = period;
  const label = `${period.year}-${String(period.month).padStart(2, "0")} · ${period.status}`;
  document.getElementById("payslip-period-label").textContent = label;

  const root = document.getElementById("payslip-table");
  root.className = "loading";
  root.textContent = "Loading payslips…";

  try {
    currentPayslips = await Api.get(`/api/payroll/periods/${period.id}/payslips`);
    renderPayslipTable();
  } catch (error) {
    root.className = "flash error";
    root.textContent = error.message || "Could not load payslips.";
  }
}

function renderPeriods() {
  const root = document.getElementById("period-table");
  if (!allPeriods.length) {
    root.innerHTML =
      '<div class="empty"><strong>No payroll periods</strong>Generate a month to create payslips.</div>';
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
          ${allPeriods
            .map((period) => {
              const label = `${period.year}-${String(period.month).padStart(2, "0")}`;
              const finalizeBtn =
                period.status === "draft"
                  ? `<button class="btn btn-sm" type="button" data-finalize="${period.id}">Finalize</button>`
                  : "";
              return `
              <tr>
                <td><strong>${label}</strong></td>
                <td>${statusBadge(period.status)}</td>
                <td>${period.payslip_count}</td>
                <td>
                  <button class="btn secondary btn-sm" type="button" data-view="${period.id}">
                    View
                  </button>
                  ${finalizeBtn}
                </td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>`;

  root.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      const period = allPeriods.find((item) => String(item.id) === button.dataset.view);
      if (period) loadPayslips(period);
    });
  });

  root.querySelectorAll("[data-finalize]").forEach((button) => {
    button.addEventListener("click", () => finalizePeriod(Number(button.dataset.finalize)));
  });
}

async function loadPayrollPage() {
  clearMessages();
  try {
    allPeriods = await Api.get("/api/payroll/periods");
    renderPeriods();
    if (allPeriods.length) {
      await loadPayslips(allPeriods[0]);
    } else {
      selectedPeriod = null;
      currentPayslips = [];
      document.getElementById("payslip-period-label").textContent = "Select a period";
      renderPayslipTable();
    }
  } catch (error) {
    showError(error.message || "Could not load payroll data.");
  }
}

async function generatePayroll(event) {
  event.preventDefault();
  clearMessages();

  const payload = {
    year: Number(document.getElementById("pay-year").value),
    month: Number(document.getElementById("pay-month").value),
  };

  try {
    const result = await Api.post("/api/payroll/generate", payload);
    showOk(
      `Generated ${result.payslip_count} payslips for ${payload.year}-${String(payload.month).padStart(2, "0")}.`
    );
    await loadPayrollPage();
  } catch (error) {
    showError(error.message || "Could not generate payroll.");
  }
}

async function finalizePeriod(periodId) {
  const period = allPeriods.find((item) => item.id === periodId);
  if (!period) return;
  const label = `${period.year}-${String(period.month).padStart(2, "0")}`;
  if (!window.confirm(`Finalize ${label}? Draft regeneration will be locked.`)) {
    return;
  }

  clearMessages();
  try {
    await Api.post(`/api/payroll/periods/${periodId}/finalize`);
    showOk(`${label} finalized.`);
    await loadPayrollPage();
  } catch (error) {
    showError(error.message || "Could not finalize period.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fillMonthOptions();
  loadPayrollPage();
  document.getElementById("generate-form").addEventListener("submit", generatePayroll);
  document.getElementById("payslip-search").addEventListener("input", renderPayslipTable);
});
