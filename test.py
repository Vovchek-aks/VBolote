import requests
from pprint import pprint
from random import randint
import time

# ret1 = requests.post(
#     'http://127.0.0.1:5000/api/add_zhaba',
#     json={
#         'name1': 'sfeef',
#         'name2': 'ffffff',
#         'name3': 'ewfewgfbgreg',
#         'pw': randint(0, 9),
#         'u_id': 0
#     }
# ).json()
#
# ret2 = requests.get('http://127.0.0.1:5000/api/all_users').json()
# pprint(ret1)
# pprint(ret2)

# while True:
#     pprint(requests.post(
#         'http://127.0.0.1:5000/api/add_zhaba',
#         json={
#             'name1': 'sfeef',
#             'name2': 'ffffff',
#             'name3': 'ewfewgfbgreg',
#             'pw': randint(0, 9),
#             'u_id': 0
#         }
#     ).json())
#     time.sleep(10)

# pprint(requests.post(
#     'http://127.0.0.1:5000/api/add_zhaba',
#     json={
#         'name1': 'sfeef',
#         'name2': 'ffffff',
#         'name3': 'ewfewgfbgreg',
#         'pw': randint(0, 9),
#         'u_id': 0
#     }
# ).json())

# pprint(requests.post(
#     'http://127.0.0.1:5000/api/add_new',
#     json={
#         'email': 'g@g.g',
#         'password': '123',
#         'text': 'ewfewgfwfqwefewfwgfsknn  grjwgjiwgji njwigjoisgnw aboba bgreg'
#     }
# ).json())

while True:
    pprint(requests.post(
        'http://127.0.0.1:5000/api/send_mess',
        json={
            'email': 'g@g.g',
            'password': '123',
            'text': 'ewfewgfwfqwefewfwgfsknn  grjwgjiwgji njwigjoisgnw aboba bgreg',
            'email_to': 'Vlad.aks03@mail.ru'
        }
    ).json())
    time.sleep(1)
