import requests
import socket

API_KEY = 'ה-API_KEY_שלך_כאן'

def fetch_domain_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        url = f'https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}'
        response = requests.get(url)
        data = response.json()

        if 'error' in data:
            print(f'Error: {data["error"]["message"]}')
        else:
            display_domain_info(data)
    except socket.gaierror:
        print('Error: Failed to resolve domain.')

def display_domain_info(data):
    print('מידע מהדוח:')
    for key, value in data.items():
        if isinstance(value, dict):
            print(f'{key}:')
            for inner_key, inner_value in value.items():
                print(f'  {inner_key}: {inner_value}')
        else:
            print(f'{key}: {value}')

domain = input('אנא הכנס את שם הדומיין שברצונך לבדוק: ')
if domain:
    fetch_domain_info(domain)
else:
    print('לא הוזן דומיין, פעולה בוטלה.')
