document.addEventListener('DOMContentLoaded', function () {
    const table = document.querySelector('table');
    const headers = table.querySelectorAll('th[data-sort]');

    // Add default sort indicators
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.title = "Click to sort";

        const iconSpan = document.createElement('span');
        iconSpan.className = 'sort-icon';
        iconSpan.style.marginLeft = '5px';
        iconSpan.style.fontSize = '0.7em';
        header.appendChild(iconSpan);

        header.addEventListener('click', () => {
            const currentDir = header.getAttribute('data-dir') || 'none';
            const newDir = currentDir === 'desc' ? 'asc' : 'desc'; // Default to desc on first click usually better for numbers (highest first)

            // Reset other headers
            headers.forEach(h => {
                h.setAttribute('data-dir', 'none');
                h.querySelector('.sort-icon').textContent = '⇅'; // or empty
                h.querySelector('.sort-icon').style.opacity = '0.3';
            });

            // Set current header
            header.setAttribute('data-dir', newDir);
            const icon = header.querySelector('.sort-icon');
            icon.textContent = newDir === 'asc' ? '▲' : '▼';
            icon.style.opacity = '1';

            const columnIndex = Array.from(header.parentElement.children).indexOf(header);
            sortTable(table, columnIndex, newDir === 'asc');
        });

        // Initialize icon
        header.querySelector('.sort-icon').textContent = '⇅';
        header.querySelector('.sort-icon').style.opacity = '0.3';
    });
});

function sortTable(table, columnIndex, asc) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aText = a.children[columnIndex].innerText.trim();
        const bText = b.children[columnIndex].innerText.trim();

        const aVal = parseValue(aText);
        const bVal = parseValue(bText);

        return asc ? aVal - bVal : bVal - aVal;
    });

    // Re-append rows logic
    rows.forEach(row => tbody.appendChild(row));
}

function parseValue(text) {
    // Handle currency and units
    let multiplier = 1;
    const cleanText = text.toUpperCase();

    if (cleanText.includes('B')) multiplier = 1000000000;
    else if (cleanText.includes('M')) multiplier = 1000000;
    else if (cleanText.includes('K')) multiplier = 1000;

    // Remove non-numeric chars except dot and minus
    const clean = text.replace(/[^0-9.-]/g, '');
    const val = parseFloat(clean);

    return isNaN(val) ? -Infinity : val * multiplier;
}
