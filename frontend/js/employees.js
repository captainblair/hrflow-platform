let allEmployees = [];
let statusFilter = "active";
const flash = createFlash("employees-error", "employees-ok");

function filteredEmployees() {
  let items = allEmployees;
  if (statusFilter === "active") {
    items = items.filter((item) => item.is_active);
  } else if (statusFilter === "inactive") {
    items = items.filter((item) => !item.is_active);
  }

  const q = document.getElementById("employee-search").value.trim().toLowerCase();
  if (q) {
    items = items.filter(
      (item) =>
        item.name.toLowerCase().includes(q) ||
        item.team.toLowerCase().includes(q) ||
        item.role.toLowerCase().includes(q)
    );
  }
  return items;
}

function fillManagerOptions(selectEl, selectedId, excludeId) {
  const current = selectedId == null ? "" : String(selectedId);
  const options = ['<option value="">No manager</option>'];
  allEmployees
    .filter((item) => item.is_active && item.id !== excludeId)
    .forEach((item) => {
      const selected = String(item.id) === current ? " selected" : "";
      options.push(
        `<option value="${item.id}"${selected}>${item.name} (${item.role})</option>`
      );
    });
  selectEl.innerHTML = options.join("");
}

function renderEmployees() {
  const employees = filteredEmployees();
  const root = document.getElementById("employee-table");
  document.getElementById("employee-count").textContent = `${employees.length} shown`;

  if (!employees.length) {
    root.innerHTML = emptyState(
      "No employees found",
      "Try a different filter or search."
    );
    return;
  }

  root.innerHTML = `
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th>Name</th>
            <th>Role</th>
            <th>Team</th>
            <th>Manager</th>
            <th>Salary</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${employees
            .map(
              (item) => `
            <tr>
              <td data-label="Name">
                <strong>${item.name}</strong>
                <div class="meta muted">${item.employment_type} · started ${formatDate(item.start_date)}</div>
              </td>
              <td data-label="Role">${item.role}</td>
              <td data-label="Team">${item.team}</td>
              <td data-label="Manager" class="muted">${item.manager_name || "—"}</td>
              <td data-label="Salary">${formatMoney(item.salary)}</td>
              <td data-label="Status">${item.is_active ? statusBadge("active") : statusBadge("inactive")}</td>
              <td data-label="Actions">
                <button class="btn secondary btn-sm" type="button" data-edit="${item.id}">Edit</button>
                ${
                  item.is_active
                    ? `<button class="btn danger btn-sm" type="button" data-deactivate="${item.id}">Deactivate</button>`
                    : ""
                }
              </td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;

  root.querySelectorAll("[data-edit]").forEach((button) => {
    button.addEventListener("click", () => openEditModal(Number(button.dataset.edit)));
  });
  root.querySelectorAll("[data-deactivate]").forEach((button) => {
    button.addEventListener("click", () => deactivateEmployee(Number(button.dataset.deactivate)));
  });
}

function renderOrgNodes(nodes, depth = 0, managerName = null) {
  return nodes
    .map((node) => {
      const children =
        node.reports && node.reports.length
          ? renderOrgNodes(node.reports, depth + 1, node.name)
          : "";
      const reportsLine = managerName
        ? `<div class="org-reports">Reports to ${managerName}</div>`
        : `<div class="org-reports org-reports-root">Top of team</div>`;
      return `
        <div class="org-node" data-depth="${depth}">
          <div class="org-name">${node.name}</div>
          <div class="org-role">${node.role}</div>
          <div class="org-team">${node.team}</div>
          ${reportsLine}
        </div>
        ${children}`;
    })
    .join("");
}

async function loadEmployeesPage() {
  flash.clear();
  const table = document.getElementById("employee-table");
  const orgRoot = document.getElementById("org-tree");
  table.innerHTML = loadingState("Loading employees…");
  orgRoot.innerHTML = loadingState("Loading org tree…");

  try {
    const [employees, org] = await Promise.all([
      Api.get("/api/employees"),
      Api.get("/api/employees/org"),
    ]);
    allEmployees = employees;
    fillManagerOptions(document.getElementById("emp-manager"));
    renderEmployees();
    orgRoot.innerHTML = org.length
      ? `<div class="org-tree">${renderOrgNodes(org)}</div>`
      : emptyState("No org data", "Add employees with managers to build the tree.");
  } catch (error) {
    table.innerHTML = emptyState("Could not load directory", error.message);
    orgRoot.innerHTML = emptyState("Could not load org tree", error.message);
    flash.error(error.message || "Could not load employees.");
  }
}

async function createEmployee(event) {
  event.preventDefault();
  flash.clear();
  const button = event.target.querySelector('button[type="submit"]');
  setBusy(button, true, "Creating…");

  const managerValue = document.getElementById("emp-manager").value;
  const payload = {
    name: document.getElementById("emp-name").value.trim(),
    role: document.getElementById("emp-role").value.trim(),
    team: document.getElementById("emp-team").value.trim(),
    start_date: document.getElementById("emp-start").value,
    salary: Number(document.getElementById("emp-salary").value),
    employment_type: document.getElementById("emp-type").value,
    manager_id: managerValue ? Number(managerValue) : null,
  };

  try {
    await Api.post("/api/employees", payload);
    event.target.reset();
    flash.ok("Employee created.");
    await loadEmployeesPage();
  } catch (error) {
    flash.error(error.message || "Could not create employee.");
  } finally {
    setBusy(button, false);
  }
}

function openEditModal(employeeId) {
  const employee = allEmployees.find((item) => item.id === employeeId);
  if (!employee) return;

  document.getElementById("edit-id").value = employee.id;
  document.getElementById("edit-name").value = employee.name;
  document.getElementById("edit-role").value = employee.role;
  document.getElementById("edit-team").value = employee.team;
  document.getElementById("edit-start").value = employee.start_date;
  document.getElementById("edit-salary").value = employee.salary;
  document.getElementById("edit-type").value = employee.employment_type;
  fillManagerOptions(
    document.getElementById("edit-manager"),
    employee.manager_id,
    employee.id
  );

  const modal = document.getElementById("edit-modal");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
}

function closeEditModal() {
  const modal = document.getElementById("edit-modal");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
}

async function saveEmployee(event) {
  event.preventDefault();
  flash.clear();
  const button = event.target.querySelector('button[type="submit"]');
  setBusy(button, true, "Saving…");

  const id = Number(document.getElementById("edit-id").value);
  const managerValue = document.getElementById("edit-manager").value;
  const payload = {
    name: document.getElementById("edit-name").value.trim(),
    role: document.getElementById("edit-role").value.trim(),
    team: document.getElementById("edit-team").value.trim(),
    start_date: document.getElementById("edit-start").value,
    salary: Number(document.getElementById("edit-salary").value),
    employment_type: document.getElementById("edit-type").value,
    manager_id: managerValue ? Number(managerValue) : null,
  };

  try {
    await Api.patch(`/api/employees/${id}`, payload);
    closeEditModal();
    flash.ok("Employee updated.");
    await loadEmployeesPage();
  } catch (error) {
    flash.error(error.message || "Could not update employee.");
  } finally {
    setBusy(button, false);
  }
}

async function deactivateEmployee(employeeId) {
  const employee = allEmployees.find((item) => item.id === employeeId);
  if (!employee) return;
  if (!window.confirm(`Deactivate ${employee.name}? Their history will be kept.`)) {
    return;
  }

  flash.clear();
  try {
    await Api.post(`/api/employees/${employeeId}/deactivate`);
    flash.ok(`${employee.name} deactivated.`);
    await loadEmployeesPage();
  } catch (error) {
    flash.error(error.message || "Could not deactivate employee.");
  }
}

function setFilter(next, activeBtn) {
  statusFilter = next;
  ["filter-active", "filter-all", "filter-inactive"].forEach((id) => {
    const btn = document.getElementById(id);
    btn.className = btn === activeBtn ? "btn secondary" : "btn ghost";
  });
  renderEmployees();
}

document.addEventListener("DOMContentLoaded", () => {
  loadEmployeesPage();

  document.getElementById("employee-form").addEventListener("submit", createEmployee);
  document.getElementById("edit-form").addEventListener("submit", saveEmployee);
  document.getElementById("edit-cancel").addEventListener("click", closeEditModal);
  document.getElementById("edit-modal").addEventListener("click", (event) => {
    if (event.target.id === "edit-modal") closeEditModal();
  });

  document.getElementById("employee-search").addEventListener("input", renderEmployees);
  document
    .getElementById("filter-active")
    .addEventListener("click", (e) => setFilter("active", e.currentTarget));
  document
    .getElementById("filter-all")
    .addEventListener("click", (e) => setFilter("all", e.currentTarget));
  document
    .getElementById("filter-inactive")
    .addEventListener("click", (e) => setFilter("inactive", e.currentTarget));
});
