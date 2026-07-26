function markActiveNav() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll(".nav a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === path) {
      link.classList.add("active");
    }
  });
}

function statusBadge(status) {
  const value = (status || "").toLowerCase();
  const map = {
    approved: "approved",
    pending: "pending",
    rejected: "rejected",
    cancelled: "inactive",
    active: "active",
    inactive: "inactive",
    draft: "pending",
    finalized: "approved",
  };
  const cls = map[value] || "inactive";
  return `<span class="badge ${cls}">${status || "—"}</span>`;
}

function formatMoney(value) {
  const amount = Number(value || 0);
  return amount.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatDate(value) {
  if (!value) return "—";
  return value.slice(0, 10);
}

document.addEventListener("DOMContentLoaded", markActiveNav);
