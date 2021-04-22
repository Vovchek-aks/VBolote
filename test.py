import requests

ret = requests.post(
    'http://127.0.0.1:5000/api/add_zhaba',
    json={
        'name1': 'sfeef',
        'name2': 'ffffff',
        'name3': 'ewfewgfbgreg',
        'pw': 6,
        'u_id': 0
    }
).json()

print(ret)


