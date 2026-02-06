let mode = "desc";

// Initialize on load
document.addEventListener("DOMContentLoaded", () => {
    fetchInitialSuggestions();
});

async function fetchInitialSuggestions() {
    try {
        const res = await fetch("/random");
        const data = await res.json();
        renderBooks(data.results || [], "Suggested For You");
    } catch (e) {
        console.error("Failed to load initial suggestions:", e);
    }
}

// Tab switch
function switchTab(tab) {
    mode = tab;

    document.getElementById("isbnTab").classList.toggle("active", tab === "isbn");
    document.getElementById("descTab").classList.toggle("active", tab === "desc");

    const descInput = document.getElementById("descInput");
    const isbnInput = document.getElementById("isbnInput");

    if (tab === "isbn") {
        descInput.style.display = "none";
        isbnInput.style.display = "block";
    } else {
        descInput.style.display = "block";
        isbnInput.style.display = "none";
    }
}

// Search handler
async function search() {
    if (mode === "isbn") {
        searchByISBN();
    } else {
        searchByDescription();
    }
}

// ISBN Search
async function searchByISBN() {
    const isbn = document.getElementById("isbnInput").value.trim();
    if (!isbn) return;

    setLoading(true);
    try {
        const res = await fetch(`/book/isbn/${isbn}`);
        if (!res.ok) throw new Error("No book found with this ISBN");
        const data = await res.json();
        renderBooks([data], `Result for ${isbn}`);
    } catch (e) {
        alert(e.message);
    } finally {
        setLoading(false);
    }
}

// Semantic Search
async function searchByDescription() {
    const desc = document.getElementById("descInput").value.trim();
    if (desc.length < 2) return;

    setLoading(true);
    try {
        const res = await fetch(`/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: desc })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Search failed");
        }

        const data = await res.json();
        renderBooks(data.results || [], `Top Matches for "${desc}"`);
    } catch (e) {
        console.error(e);
        alert("Error: " + e.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    const btn = document.querySelector(".search-button");
    btn.innerText = isLoading ? "Scanning Library..." : "Find Matches";
    btn.disabled = isLoading;
}

// Render cards
function renderBooks(books, title) {
    if (title) {
        document.getElementById("sectionTitle").innerText = title;
    }

    const container = document.getElementById("results");
    container.innerHTML = "";

    if (!books || books.length === 0) {
        container.innerHTML = "<div class='no-results'>We couldn't find any books that match your query. Try different words or a different genre.</div>";
        return;
    }

    books.forEach((book, index) => {
        const img = book.image_url && book.image_url !== "nan"
            ? book.image_url
            : "https://via.placeholder.com/400x600?text=No+Cover+Available";

        const bookUrl = book.book_url && book.book_url !== "nan"
            ? book.book_url
            : `https://www.google.com/search?q=${encodeURIComponent(book.Title + ' book')}`;

        const card = document.createElement("div");
        card.className = "book-card";
        card.style.animationDelay = `${index * 0.08}s`;

        card.innerHTML = `
            <a href="${bookUrl}" target="_blank" style="text-decoration: none; color: inherit;">
                <div class="cover-wrapper">
                    <img src="${img}" 
                         class="book-cover" 
                         alt="${book.Title}"
                         onerror="this.src='https://via.placeholder.com/400x600?text=No+Cover+Available'">
                </div>
            </a>
            <div class="card-content">
                <div class="book-title clamp-2" title="${book.Title}">${book.Title}</div>
                <div class="book-author clamp-1">${book.Author_Editor || "Unknown Author"}</div>
            </div>
        `;
        container.appendChild(card);
    });

    if (title !== "Suggested For You") {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
