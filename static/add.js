/**
 * Collects movie details from the form and submits them to the /add endpoint.
 * This replaces the previous URL-based submission logic.
 */
function submitAdd() {
  // Capture values from the updated form IDs
  const name = document.getElementById("newMovieName").value.trim();
  const type = document.getElementById("newMovieType").value.trim();
  const ott = document.getElementById("newMovieOtt").value.trim();
  const status = document.getElementById("newMovieStatus").value.trim();
  const language = document.getElementById("newMovieLanguage").value.trim();
  const rating = document.getElementById("newMovieRating").value.trim();
  const tags = document.getElementById("newTags").value.trim();

  // Create FormData with keys matching the new backend 'add_movie' route
  const formData = new FormData();
  formData.append("name", name);
  formData.append("type", type);
  formData.append("ott", ott);
  formData.append("status", status);
  formData.append("language", language);
  formData.append("rating", rating);
  formData.append("tags", tags);

  fetch("/add", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      closeAddForm();
      search(1); // refresh movie results
    })
    .catch((error) => console.error("Error:", error));
}

/**
 * Resets all movie-related input fields and displays the modal.
 */
// Change Add Button in HTML or JS
function openAddForm() {
  window.location.href = "/addpage";
}
function closeAddForm() {
  document.getElementById("addModal").style.display = "none";
}
