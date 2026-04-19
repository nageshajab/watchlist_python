let showDetails = false;

/**
 * Main search function to fetch movies from the backend.
 * Renders Bootstrap cards into the #results grid.
 */
function hideCancelledAndCompleted(page = 1) {
  console.log("Hiding Cancelled and Completed movies...");
  const defaultStatuses = ["watching", "to watch"];

  document.querySelectorAll(".status-checkbox").forEach((cb) => {
    if (defaultStatuses.includes(cb.value)) {
      cb.checked = true;
    } else {
      cb.checked = false;
    }
  });
  search(page);
}

function search(page = 1) {
  const query = document.getElementById("searchBox").value.trim();

  const statuses = getSelectedStatuses(); // 👈 array

  const limit = 12; // Adjusted for a better grid look (multiple of 1, 2, 3, 4)

  const params = new URLSearchParams();
  params.append("page", page);
  params.append("limit", limit);

  if (query) params.append("q", query);

  if (statuses.length) {
    params.append("status", statuses.join(","));
  }

  fetch(`/search?${params.toString()}`)
    .then((response) => response.json())
    .then((data) => {
      const resultsDiv = document.getElementById("results");
      resultsDiv.innerHTML = "";

      if (data.results.length === 0) {
        resultsDiv.innerHTML = `<div class="col-12 text-center py-5 text-muted">No movies found in your watchlist.</div>`;
        return;
      }

      data.results.forEach((item) => {
        const col = document.createElement("div");
        col.className = "col";

        // Create the card structure using Bootstrap classes
        col.innerHTML = `
                    <div class="card movie-card h-100 p-3">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="fw-bold mb-0 text-truncate" style="max-width: 80%;">${item.name}</h6>
                            <span class="badge rounded-pill rating-badge text-dark">⭐ ${item.rating}/10</span>
                        </div>
                        
                        <div class="movie-info-section mb-3">
                            <span class="badge badge-ott mb-1">${item.ott || "Unknown OTT"}</span>
                            <div class="small text-muted mt-1 ${showDetails ? "" : "d-none"}">
                                <div><strong>Type:</strong> ${item.type || "N/A"}</div>
                                <div><strong>Lang:</strong> ${item.language || "N/A"}</div>
                                <div><strong>Status:</strong> ${item.status || "N/A"}</div>
                            </div>
                        </div>

                        ${
                          item.tags && item.tags.length > 0
                            ? `
                            <div class="mb-3">
                                <small class="text-primary d-block text-truncate">#${item.tags.join(" #")}</small>
                            </div>
                        `
                            : ""
                        }

                        <div class="mt-auto d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary w-50" 
                                    onclick="location.href='/editpage/${item.id}'">Edit</button>
                            <button class="btn btn-sm btn-outline-danger w-50" 
                                    onclick="deleteMovie(${item.id})">Delete</button>
                        </div>
                    </div>
                `;
        resultsDiv.appendChild(col);
      });

      renderPagination(data);
    })
    .catch((error) => console.error("Error fetching movies:", error));
}

/**
 * Handles movie deletion with a confirmation prompt.
 */
function deleteMovie(id) {
  if (
    confirm("Are you sure you want to remove this movie from your watchlist?")
  ) {
    fetch(`/delete/${id}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message);
        search(1); // Refresh the current view
      })
      .catch((error) => console.error("Error deleting movie:", error));
  }
}

/**
 * Renders Bootstrap-styled pagination buttons.
 */
function renderPagination(data) {
  const paginationDiv = document.getElementById("pagination");
  paginationDiv.innerHTML = "";

  const totalPages = Math.ceil(data.total / data.per_page);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = `btn btn-outline-primary mx-1 ${i === data.page ? "active-page" : ""}`;
    btn.onclick = () => {
      search(i);
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
    paginationDiv.appendChild(btn);
  }
}

function getSelectedStatuses() {
  return Array.from(document.querySelectorAll(".status-checkbox:checked")).map(
    (cb) => cb.value,
  );
}

function updateStatusDropdownText() {
  const selected = getSelectedStatuses();
  const btn = document.getElementById("statusDropdownBtn");

  if (selected.length === 0) {
    btn.innerText = "All Status";
  } else {
    btn.innerText = selected.join(", ");
  }
}

document.querySelectorAll(".status-checkbox").forEach((cb) => {
  cb.addEventListener("change", updateStatusDropdownText);
});
/**
 * Clears search results and resets the search box.
 */
function clearSearch() {
  document.getElementById("searchBox").value = "";
  document.getElementById("results").innerHTML = "";
  document.getElementById("pagination").innerHTML = "";
  document.querySelectorAll(".status-checkbox").forEach((cb) => {
    cb.checked = true;
  });
}

/**
 * Initialization and Event Listeners
 */
document.addEventListener("DOMContentLoaded", () => {
  // Initial search to populate the page
  search(1);

  // Listen for Enter key on search box
  const searchBox = document.getElementById("searchBox");
  if (searchBox) {
    searchBox.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        search(1);
      }
    });
  }

  // Toggle extended details listener
  const toggleCheckbox = document.getElementById("toggleDetailsCheckbox");
  if (toggleCheckbox) {
    toggleCheckbox.addEventListener("change", () => {
      showDetails = toggleCheckbox.checked;
      search(1); // Re-render to show/hide details
    });
  }
});
