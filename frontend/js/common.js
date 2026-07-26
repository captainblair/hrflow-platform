function markActiveNav() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll(".nav a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    const isActive = href === path;
    link.classList.toggle("active", isActive);
    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
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

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function leaveStatusBadges(item) {
  const parts = [statusBadge(item.status)];
  if (item.is_overdue) {
    parts.push('<span class="badge warning">Overdue</span>');
  }
  // Keep approved history, but mark finished ranges so they don't look current.
  if (item.end_date && item.end_date < todayISO()) {
    parts.push('<span class="badge inactive">Past</span>');
  }
  return `<span class="badge-group">${parts.join("")}</span>`;
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

function emptyState(title, body) {
  return `<div class="empty"><strong>${title}</strong>${body || ""}</div>`;
}

function loadingState(message) {
  return `<div class="loading"><span class="spinner" aria-hidden="true"></span>${message || "Loading…"}</div>`;
}

function setBusy(button, busy, busyLabel) {
  if (!button) return;
  if (busy) {
    button.dataset.label = button.textContent;
    button.disabled = true;
    button.classList.add("is-busy");
    button.textContent = busyLabel || "Working…";
  } else {
    button.disabled = false;
    button.classList.remove("is-busy");
    if (button.dataset.label) {
      button.textContent = button.dataset.label;
      delete button.dataset.label;
    }
  }
}

function createFlash(errorId, okId) {
  const errorBox = document.getElementById(errorId);
  const okBox = document.getElementById(okId);

  function clear() {
    if (errorBox) errorBox.hidden = true;
    if (okBox) okBox.hidden = true;
  }

  function show(box, message) {
    clear();
    if (!box) return;
    box.hidden = false;
    box.textContent = message;
    box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  return {
    clear,
    error(message) {
      show(errorBox, message);
    },
    ok(message) {
      show(okBox, message);
    },
  };
}

document.addEventListener("DOMContentLoaded", markActiveNav);
