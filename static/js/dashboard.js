// Live filter: hide the student cards that do not match the name typed
// or the language selected. Runs in the browser, no page reload.

const search = document.getElementById("search");
const languageFilter = document.getElementById("language-filter");
const cards = document.querySelectorAll(".student-card");
const count = document.getElementById("student-count");
const noResults = document.getElementById("no-results");

function applyFilters() {
  const query = search.value.trim().toLowerCase();
  const language = languageFilter.value; // "" means all languages
  let visible = 0;

  cards.forEach((card) => {
    // data-name and data-language are set in lower case by the template.
    const nameOk = card.dataset.name.includes(query);
    const languageOk = language === "" || card.dataset.language === language;
    const match = nameOk && languageOk;
    card.hidden = !match;
    if (match) visible++;
  });

  count.textContent = visible;
  noResults.hidden = visible > 0;
}

// The filters only exist when the tutor has at least one student.
if (search && languageFilter) {
  search.addEventListener("input", applyFilters);
  languageFilter.addEventListener("change", applyFilters);
}
