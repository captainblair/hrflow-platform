let allEmployees = [];

function renderEmployees(employees) {
  const root = document.getElementById("employee-table");
  document.getElementById("employee-count").textContent = `${employees.length} shown`;

  if (!employees.length) {
    root.innerHTML =
      '<div class="empty"><strong>No employees found</strong>Try a different search.</div>';
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
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${employees
            .map(
              (item) => `
            <tr>
              <td>
                <strong>${item.name}</strong>
                <div class="meta muted">${item.employment_type}</div>
              </td>
              <td>${item.role}</td>
              <td>${item.team}</td>
              <td class="muted">${item.manager_name || "—"}</td>
              <td>${item.is_active ? statusBadge("active") : statusBadge("inactive")}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

function renderOrgNodes(nodes, depth = 0) {
  return nodes
    .map((node) => {
      const pad = depth * 16;
      const children = node.reports && node.reports.length
        ? renderOrgNodes(node.reports, depth + 1)
        : "";
      return `
        <div class="list-item" style="padding-left:${pad}px">
          <div>
            <div class="title">${node.name}</div>
            <div class="meta">${node.role} · ${node.team}</div>
          </div>
        </div>
        ${children}`;
    })
    .join("");
}

async function loadEmployeesPage() {
  const errorBox = document.getElementById("employees-error");
  try {
    const [employees, org] = await Promise.all([
      Api.get("/api/employees"),
      Api.get("/api/employees/org"),
    ]);
    allEmployees = employees;
    renderEmployees(employees);

    const orgRoot = document.getElementById("org-tree");
    orgRoot.innerHTML = org.length
      ? renderOrgNodes(org)
      : '<div class="empty"><strong>No org data</strong></div>';
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error.message || "Could not load employees.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadEmployeesPage();
  const search = document.getElementById("employee-search");
  search.addEventListener("input", () => {
    const q = search.value.trim().toLowerCase();
    const filtered = allEmployees.filter(
      (item) =>
        item.name.toLowerCase().includes(q) ||
        item.team.toLowerCase().includes(q) ||
        item.role.toLowerCase().includes(q)
    );
    renderEmployees(filtered);
  });
});
