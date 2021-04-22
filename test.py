import requests

ret1 = requests.post(
    'http://127.0.0.1:5000/api/add_zhaba',
    json={
        'name1': 'sfeef',
        'name2': 'ffffff',
        'name3': 'ewfewgfbgreg',
        'pw': 6,
        'u_id': 0
    }
).json()

ret2 = requests.get('http://127.0.0.1:5000/api/all_users').json()

print(ret1)
print(ret2)


