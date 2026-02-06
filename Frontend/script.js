let mode = "desc";

document.addEventListener("DOMContentLoaded", () => {
    fetchInitialSuggestions();
    setupISBNToggle();
});

function setupISBNToggle() {
    const btn = document.getElementById("isbnToggle");
    const field = document.getElementById("isbnField");
    btn.addEventListener("click", () => {
        field.classList.toggle("active");
        mode = field.classList.contains("active") ? "isbn" : "desc";
    });
}

async function fetchInitialSuggestions() {
    try {
        const res = await fetch("/random");
        const data = await res.json();
        renderRecommendations(data.results || []);
    } catch (e) {
        console.error("Failed suggestions:", e);
    }
}

async function search() {
    const desc = document.getElementById("descInput").value.trim();
    const isbn = document.getElementById("isbnInput").value.trim();

    if (mode === "isbn" && isbn) {
        searchByISBN(isbn);
    } else if (desc) {
        searchByDescription(desc);
    }
}

async function searchByISBN(isbn) {
    setLoading(true);
    try {
        const res = await fetch(`/book/isbn/${isbn}`);
        if (!res.ok) throw new Error("No book found");
        const data = await res.json();
        renderMainResults([data], "Search Results");
    } catch (e) {
        alert(e.message);
    } finally {
        setLoading(false);
    }
}

async function searchByDescription(desc) {
    setLoading(true);
    try {
        const res = await fetch(`/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: desc })
        });
        const data = await res.json();
        renderMainResults(data.results || [], `Results for "${desc}"`);
    } catch (e) {
        console.error(e);
        alert("Error: " + e.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    const btn = document.querySelector(".primary-search-btn");
    btn.innerText = isLoading ? "Searching..." : "Search";
    btn.disabled = isLoading;
}

function renderMainResults(books, label) {
    document.getElementById("resultsLabel").innerText = label;
    const heroContainer = document.getElementById("heroCard");
    const gridContainer = document.getElementById("results");

    heroContainer.innerHTML = "";
    gridContainer.innerHTML = "";

    if (!books || books.length === 0) {
        heroContainer.innerHTML = "<p>No matches found.</p>";
        return;
    }

    // First book is Hero
    const hero = books[0];
    const heroImg = hero.image_url && hero.image_url !== "nan" ? hero.image_url : "https://via.placeholder.com/200x300";
    const heroLink = hero.book_url && hero.book_url !== "nan" ? hero.book_url : "#";

    heroContainer.innerHTML = `
        <img src="${heroImg}" class="book-img" alt="${hero.Title}" onerror="this.src='https://via.placeholder.com/200x300'">
        <div class="details">
            <h3>${hero.Title}</h3>
            <p>${hero.Author_Editor || "Unknown Author"}</p>
            <a href="${heroLink}" target="_blank" class="hero-details-btn">View Details</a>
        </div>
    `;

    // Remaining are grid
    books.slice(1, 7).forEach(book => {
        const img = book.image_url && book.image_url !== "nan" ? book.image_url : "https://via.placeholder.com/150x225";
        const link = book.book_url && book.book_url !== "nan" ? book.book_url : "#";

        const card = document.createElement("a");
        card.href = link;
        card.target = "_blank";
        card.style.textDecoration = "none";
        card.className = "book-card-mini";
        card.innerHTML = `
            <img src="${img}" class="mini-cover" onerror="this.src='https://via.placeholder.com/150x225'">
            <div class="mini-info">
                <div class="mini-title">${book.Title}</div>
            </div>
        `;
        gridContainer.appendChild(card);
    });

    document.querySelector(".dashboard-grid").scrollIntoView({ behavior: 'smooth' });
}

function renderRecommendations(books) {
    const container = document.getElementById("recommendations");
    container.innerHTML = "";

    books.forEach(book => {
        const img = book.image_url && book.image_url !== "nan" ? book.image_url : "https://via.placeholder.com/150x225";
        const link = book.book_url && book.book_url !== "nan" ? book.book_url : "#";

        const card = document.createElement("a");
        card.href = link;
        card.target = "_blank";
        card.className = "scroll-card";
        card.innerHTML = `<img src="${img}" class="scroll-img" alt="${book.Title}" onerror="this.src='https://via.placeholder.com/150x225'">`;
        container.appendChild(card);
    });
}
