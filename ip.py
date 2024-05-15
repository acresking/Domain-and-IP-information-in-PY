from bs4 import BeautifulSoup
import requests
import socket

def fetch_domain_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        url = f'https://ipgeolocation.io/what-is-my-ip/{ip}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            data_table = soup.find('table', {'class': 'table'})
            if data_table:
                display_domain_info(data_table)
            else:
                print('Error: Data table not found in HTML.')

        else:
            print(f'Error: Non-200 status code ({response.status_code})')

    except socket.gaierror:
        print('Error: Failed to resolve domain.')
    except Exception as e:
        print(f'Error: {e}')

def display_domain_info(data_table):
    print('מידע מהדומיין:')
    rows = data_table.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 2:
            key = columns[0].text.strip()
            value = columns[1].text.strip()
            print(f'{key}: {value}')

domain = input('אנא הכנס את שם הדומיין שברצונך לבדוק: ')
if domain:
    fetch_domain_info(domain)
else:
    print('לא הוזן דומיין, פעולה בוטלה.')
