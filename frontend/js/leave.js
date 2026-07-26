let allLeave = [];
let allEmployees = [];
let currentFilter = "all";
let pendingDecide = null;

function showError(message) {
  const box = document.getElementById("leave-error");
  document.getElementById("leave-ok").hidden = true;
  box.hidden = false;
  box.textContent = message;
}

function showOk(message) {
  const box = document.getElementById("leave-ok");
  document.getElementById("leave-error").hidden = true;
  box.hidden = false;
  box.textContent = message;
}

function clearMessages() {
  document.getElementById("leave-error").hidden = true;
  document.getElementById("leave-ok").hidden = true;
}

function applyLeaveFilter() {
  let items = allLeave;
  if (currentFilter === "pending") {
    items = items.filter((item) => item.status === "pending");
  } else if (currentFilter === "overdue") {
    items = items.filter((item) => item.is_overdue);
  }

  const search = document.getElementById("leave-search").value.trim().toLowerCase();
  if (search) {
    items = items.filter((item) =>
      (item.employee_name || "").toLowerCase().includes(search)
    );
  }
  renderLeaveTable(items);
}

function setFilterButtons() {
  document.querySelectorAll("[data-filter]").forEach((button) => {
    const active = button.getAttribute("data-filter") === currentFilter;
    button.className = active ? "btn secondary btn-sm" : "btn ghost btn-sm";
  });
}

function renderLeaveTable(items) {
  const root = document.getElementById("leave-table");
  if (!items.length) {
    root.innerHTML =
      '<div class="empty"><strong>No matching requests</strong>Adjust filters to see more.</div>';
    return;
  }

  root.innerHTML = `
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Type</th>
            <th>Dates</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${items
            .map((item) => {
              const actions =
                item.status === "pending"
                  ? `
                    <button class="btn secondary btn-sm" type="button" data-approve="${item.id}">Approve</button>
                    <button class="btn danger btn-sm" type="button" data-reject="${item.id}">Reject</button>
                  `
                  : `<span class="muted">${item.decided_by_name || "—"}</span>`;
              return `
            <tr>
              <td>
                <strong>${item.employee_name}</strong>
                <div class="meta muted">${item.reason || "No reason given"}</div>
              </td>
              <td>${item.leave_type}</td>
              <td class="muted">${formatDate(item.start_date)} → ${formatDate(item.end_date)} (${item.days}d)</td>
              <td>
                ${leaveStatusBadges(item)}
              </td>
              <td>${actions}</td>
            </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>`;

  root.querySelectorAll("[data-approve]").forEach((button) => {
    button.addEventListener("click", () =>
      openDecideModal(Number(button.dataset.approve), "approve")
    );
  });
  root.querySelectorAll("[data-reject]").forEach((button) => {
    button.addEventListener("click", () =>
      openDecideModal(Number(button.dataset.reject), "reject")
    );
  });
}

function fillEmployeeSelect() {
  const select = document.getElementById("leave-employee");
  const active = allEmployees.filter((item) => item.is_active);
  select.innerHTML =
    '<option value="">Select employee</option>' +
    active
      .map(
        (item) =>
          `<option value="${item.id}">${item.name} · ${item.team}</option>`
      )
      .join("");
}

async function refreshBalance() {
  const badge = document.getElementById("balance-badge");
  const employeeId = document.getElementById("leave-employee").value;
  if (!employeeId) {
    badge.textContent = "Balance —";
    return;
  }

  try {
    const balance = await Api.get(`/api/leave/balances/${employeeId}`);
    badge.textContent = `Annual left: ${balance.annual_remaining}`;
  } catch (error) {
    badge.textContent = "Balance unavailable";
  }
}

function openDecideModal(leaveId, action) {
  const leave = allLeave.find((item) => item.id === leaveId);
  if (!leave) return;

  pendingDecide = { leave, action };
  document.getElementById("decide-leave-id").value = leaveId;
  document.getElementById("decide-action").value = action;
  document.getElementById("decide-title").textContent =
    action === "approve" ? "Approve leave request" : "Reject leave request";
  document.getElementById("decide-summary").textContent =
    `${leave.employee_name} · ${leave.leave_type} · ${formatDate(leave.start_date)} → ${formatDate(leave.end_date)}. Choose their manager as approver.`;
  document.getElementById("decide-confirm").textContent =
    action === "approve" ? "Approve" : "Reject";
  document.getElementById("decide-confirm").className =
    action === "approve" ? "btn" : "btn danger";

  const employee = allEmployees.find((item) => item.id === leave.employee_id);
  const managerId = employee && employee.manager_id;
  const select = document.getElementById("decide-approver");
  const managers = allEmployees.filter((item) => item.is_active);
  select.innerHTML =
    '<option value="">Select manager</option>' +
    managers
      .map((item) => {
        const selected = item.id === managerId ? " selected" : "";
        return `<option value="${item.id}"${selected}>${item.name}</option>`;
      })
      .join("");

  const modal = document.getElementById("decide-modal");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
}

function closeDecideModal() {
  pendingDecide = null;
  const modal = document.getElementById("decide-modal");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
}

async function loadLeavePage() {
  clearMessages();
  try {
    const [leave, employees] = await Promise.all([
      Api.get("/api/leave"),
      Api.get("/api/employees"),
    ]);
    allLeave = leave;
    allEmployees = employees;
    fillEmployeeSelect();
    setFilterButtons();
    applyLeaveFilter();
    await refreshBalance();
  } catch (error) {
    showError(error.message || "Could not load leave data.");
  }
}

async function submitLeave(event) {
  event.preventDefault();
  clearMessages();

  const payload = {
    employee_id: Number(document.getElementById("leave-employee").value),
    leave_type: document.getElementById("leave-type").value,
    start_date: document.getElementById("leave-start").value,
    end_date: document.getElementById("leave-end").value,
    reason: document.getElementById("leave-reason").value.trim() || null,
  };

  try {
    await Api.post("/api/leave", payload);
    event.target.reset();
    showOk("Leave request submitted.");
    await loadLeavePage();
  } catch (error) {
    showError(error.message || "Could not submit leave request.");
  }
}

async function confirmDecision(event) {
  event.preventDefault();
  clearMessages();

  const leaveId = Number(document.getElementById("decide-leave-id").value);
  const action = document.getElementById("decide-action").value;
  const approverId = Number(document.getElementById("decide-approver").value);
  if (!approverId) {
    showError("Approver is required.");
    return;
  }

  try {
    await Api.post(`/api/leave/${leaveId}/${action}`, {
      approver_id: approverId,
    });
    closeDecideModal();
    showOk(action === "approve" ? "Leave approved." : "Leave rejected.");
    await loadLeavePage();
  } catch (error) {
    showError(error.message || `Could not ${action} leave request.`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadLeavePage();

  document.getElementById("leave-form").addEventListener("submit", submitLeave);
  document.getElementById("leave-employee").addEventListener("change", refreshBalance);
  document.getElementById("leave-search").addEventListener("input", applyLeaveFilter);
  document.getElementById("decide-form").addEventListener("submit", confirmDecision);
  document.getElementById("decide-cancel").addEventListener("click", closeDecideModal);
  document.getElementById("decide-modal").addEventListener("click", (event) => {
    if (event.target.id === "decide-modal") closeDecideModal();
  });

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      currentFilter = button.getAttribute("data-filter");
      setFilterButtons();
      applyLeaveFilter();
    });
  });
});
