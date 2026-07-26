let allLeave = [];
let currentFilter = "all";

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
          </tr>
        </thead>
        <tbody>
          ${items
            .map(
              (item) => `
            <tr>
              <td>
                <strong>${item.employee_name}</strong>
                <div class="meta muted">${item.reason || "No reason given"}</div>
              </td>
              <td>${item.leave_type}</td>
              <td class="muted">${formatDate(item.start_date)} → ${formatDate(item.end_date)}</td>
              <td>
                ${statusBadge(item.status)}
                ${item.is_overdue ? '<span class="badge warning">Overdue</span>' : ""}
              </td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

async function loadLeavePage() {
  const errorBox = document.getElementById("leave-error");
  try {
    allLeave = await Api.get("/api/leave");
    applyLeaveFilter();
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error.message || "Could not load leave requests.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadLeavePage();
  document.getElementById("leave-search").addEventListener("input", applyLeaveFilter);
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      currentFilter = button.getAttribute("data-filter");
      applyLeaveFilter();
    });
  });
});
