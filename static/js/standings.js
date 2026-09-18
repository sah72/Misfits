document.addEventListener("DOMContentLoaded", () => {

    const tableContainer = document.querySelector(".table-scroll");

    if (!tableContainer) {
        return;
    }

    tableContainer.addEventListener("click", async (event) => {

        const sortLink = event.target.closest(
            "#standings_table thead a"
        );

        if (!sortLink) {
            return;
        }

        // Stop the browser from refreshing the whole page
        event.preventDefault();

        try {

            const response = await fetch(sortLink.href);

            if (!response.ok) {
                throw new Error("Could not sort standings");
            }

            const html = await response.text();

            // Convert the returned HTML string into a document
            const parser = new DOMParser();
            const newDocument = parser.parseFromString(
                html,
                "text/html"
            );

            // Find the newly sorted table
            const newTable =
                newDocument.querySelector("#standings_table");

            const currentTable =
                document.querySelector("#standings_table");

            // Replace only the table
            currentTable.replaceWith(newTable);

        } catch (error) {

            console.error(
                "Could not update standings:",
                error
            );

        }

    });

});

// Prevent refresh on sort buttons

// Sort standings without refreshing the page
let sorting = false;

document.addEventListener("click", async (event) => {

    // Check whether a sortable header was clicked
    const link = event.target.closest(
        "#standings_table thead a"
    );

    if (!link) return;

    // Allow Ctrl+Click, middle-click, etc.
    if (
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey ||
        event.altKey ||
        event.button !== 0
    ) return;

    // Prevent the page from refreshing
    event.preventDefault();

    if (sorting) return;

    sorting = true;

    const url = link.href;
    const currentTable = document.querySelector(
        "#standings_table"
    );

    currentTable.setAttribute("aria-busy", "true");

    try {

        // Request sorted standings from Flask
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Failed to fetch standings");
        }

        const html = await response.text();

        // Convert returned HTML into a document
        const parser = new DOMParser();

        const doc = parser.parseFromString(
            html,
            "text/html"
        );

        // Find the updated standings table
        const newTable = doc.querySelector(
            "#standings_table"
        );

        if (!newTable) {
            throw new Error("Standings table not found");
        }

        // Replace ONLY the table
        currentTable.replaceWith(newTable);

    } catch (error) {

        console.error("Sorting error:", error);

        // Fall back to regular navigation
        window.location.href = url;

    } finally {

        sorting = false;

    }

});