/**
 * Collects updated movie details from the edit form and submits them
 * to the /edit/<id> endpoint using the POST method.
 */
function submitEdit() {
  const id = document.getElementById("editId").value;
  const name = document.getElementById("editMovieName").value.trim();
  const type = document.getElementById("editMovieType").value.trim();
  const ott = document.getElementById("editMovieOtt").value.trim();
  const status = document.getElementById("editMovieStatus").value.trim();
  const language = document.getElementById("editMovieLanguage").value.trim();
  const rating = document.getElementById("editMovieRating").value.trim();
  const tags = document.getElementById("editTags").value.trim();

  const formData = new FormData();
  formData.append("name", name);
  formData.append("type", type);
  formData.append("ott", ott);
  formData.append("status", status);
  formData.append("language", language);
  formData.append("rating", rating);
  formData.append("tags", tags);

  fetch(`/edit/${id}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      closeEditForm();
      search(1); // refresh the movie results list
    })
    .catch((error) => console.error("Error updating movie:", error));
}

/**
 * Fetches existing movie details from the server to populate the edit modal.
 * @param {number} id - The unique ID of the movie to be edited.
 */
function openEditForm(id) {
  fetch(`/edit/${id}`)
    .then((response) => response.json())
    .then((data) => {
      // Map the retrieved movie data to the form input fields
      document.getElementById("editId").value = data.id;
      document.getElementById("editMovieName").value = data.name;
      document.getElementById("editMovieType").value = data.type || "";
      document.getElementById("editMovieOtt").value = data.ott || "Netflix";
      document.getElementById("editMovieStatus").value = data.status || "";
      document.getElementById("editMovieLanguage").value = data.language || "";
      document.getElementById("editMovieRating").value = data.rating || 0;
      document.getElementById("editTags").value = data.tags
        ? data.tags.join(", ")
        : "";

      document.getElementById("editModal").style.display = "block";
    })
    .catch((error) => console.error("Error fetching movie details:", error));
}

function closeEditForm() {
  document.getElementById("editModal").style.display = "none";
}
