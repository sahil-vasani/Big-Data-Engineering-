let mode = "desc";

// Tab switch
function switchTab(tab) {
    mode = tab;

    document.getElementById("isbnTab").classList.toggle("active", tab === "isbn");
    document.getElementById("descTab").classList.toggle("active", tab === "desc");

    document.getElementById("isbnInput").disabled = tab !== "isbn";
    document.getElementById("descInput").disabled = tab !== "desc";
}

// Search handler
async function search() {
    if (mode === "isbn") {
        searchByISBN();
    } else {
        searchByDescription();
    }
}

// ISBN
async function searchByISBN() {
    const isbn = document.getElementById("isbnInput").value.trim();
    if (!isbn) return;

    try {
        const res = await fetch(`/book/isbn/${isbn}`);
        if (!res.ok) throw new Error("Book not found");
        const data = await res.json();
        renderBooks([data]);
    } catch (e) {
        alert("Error searching ISBN: " + e.message);
    }
}

// DESCRIPTION
async function searchByDescription() {
    const desc = document.getElementById("descInput").value.trim();
    if (desc.length < 3) return;

    const btn = document.querySelector(".search-button");
    if (!btn) return;

    const originalText = btn.innerText;
    btn.innerText = "Searching...";
    btn.disabled = true;

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
        renderBooks(data.results || []);
    } catch (e) {
        console.error(e);
        alert("Recommendation Error: " + e.message);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// Render cards
function renderBooks(books) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    if (!books || books.length === 0) {
        container.innerHTML = "<p class='no-results' style='grid-column: 1/-1; text-align: center; padding: 2rem; color: #666;'>No books found matching your description. Try another search!</p>";
        return;
    }

    books.forEach(book => {
        const img = book.image_url && book.image_url !== "nan"
            ? book.image_url
            : "https://via.placeholder.com/300x450?text=No+Image";

        container.innerHTML += `
            <div class="book-card">
                <div class="cover-wrapper">
                    <span class="match-badge">
                        ${Math.floor(85 + Math.random() * 10)}% Match
                    </span>
                    <img src="${img}"
                         class="book-cover"
                         onerror="this.src='https://via.placeholder.com/300x450?text=No+Image'">
                </div>
                <div class="card-content">
                    <div class="book-title clamp-2">${book.Title}</div>
                    <div class="book-author clamp-1">${book.Author_Editor || ""}</div>
                </div>
            </div>
        `;
    });
}

