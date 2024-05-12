const fetch = require('node-fetch');
const dns = require('dns');

const API_KEY = 'ה-API_KEY_שלך_כאן';

async function fetchDomainInfo(domain) {
    try {
        const ip = await resolveDomain(domain);
        const url = `https://api.ipgeolocation.io/ipgeo?apiKey=${API_KEY}&ip=${ip}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            console.log(`Error: ${data.error.message}`);
        } else {
            displayDomainInfo(data);
        }
    } catch (error) {
        console.log('Error:', error.message);
    }
}

function resolveDomain(domain) {
    return new Promise((resolve, reject) => {
        dns.resolve(domain, (error, addresses) => {
            if (error) {
                reject(error);
            } else {
                resolve(addresses[0]);
            }
        });
    });
}

function displayDomainInfo(data) {
    console.log('מידע מהדוח:');
    for (const key in data) {
        if (typeof data[key] === 'object') {
            console.log(`${key}:`);
            for (const innerKey in data[key]) {
                console.log(`  ${innerKey}: ${data[key][innerKey]}`);
            }
        } else {
            console.log(`${key}: ${data[key]}`);
        }
    }
}

const domain = prompt('אנא הכנס את שם הדומיין שברצונך לבדוק:');
if (domain) {
    fetchDomainInfo(domain);
} else {
    console.log('לא הוזן דומיין, פעולה בוטלה.');
}
