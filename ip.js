function fetchDomainInfo(domain) {
    fetch(`https://ipgeolocation.io/what-is-my-ip/${domain}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const table = doc.querySelector('.table');
            if (table) {
                displayDomainInfo(table);
            } else {
                console.error('Error: Data table not found in HTML.');
            }
        })
        .catch(error => console.error('Error:', error));
}

function displayDomainInfo(table) {
    const rows = table.querySelectorAll('tr');
    console.log('מידע מהדומיין:');
    rows.forEach(row => {
        const columns = row.querySelectorAll('td');
        if (columns.length === 2) {
            const key = columns[0].textContent.trim();
            const value = columns[1].textContent.trim();
            console.log(`${key}: ${value}`);
        }
    });
}

const domain = prompt('אנא הכנס את שם הדומיין שברצונך לבדוק:');
if (domain) {
    fetchDomainInfo(domain);
} else {
    console.log('לא הוזן דומיין, פעולה בוטלה.');
}
