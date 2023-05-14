#!/bin/python

import requests
import json


API_URL = "http://localhost:8080"

REGISTER_URL = API_URL + "/register"
LOGIN_URL= API_URL + "/login"
AUTH_URL = API_URL + "/auth"
DELETE_USER_URL= API_URL + "/delete_user"

ADD_ROOM_URL = API_URL + "/add_room"
DELETE_ROOMS_URL = API_URL + "/delete_room"

GET_ROOMS_ADMIN_URL = API_URL + "/get_rooms_admin"
GET_ROOMS_MEMBER_URL = API_URL + "/get_rooms_member"
GET_ROOMS_URL = API_URL + "/get_rooms"

JOIN_ROOM_URL = API_URL + "/join_room"
LEAVE_ROOM_URL = API_URL + "/leave_room"
DELETE_MEMBER_URL = API_URL + "/delete_member"

ADD_CHEQUE_URL = API_URL + "/add_cheque"
GET_CHEQUES_URL = API_URL + "/get_cheques"
DELETE_CHEQUE_URL = API_URL + "/delete_cheque"


#MAX_USERNAME = 32
#MIN_USERNAME = 4
#
#MAX_PASSWORD = 16
#MIN_PASSWORD = 8
#
#MAX_EMAIL = 40


def create_user(letter):
    data = {
        'email': f'{letter}@test.com',
        'name': f'{letter}',
        'password': 'password'
    }
    return data, requests.post(REGISTER_URL, json=data)


def get_token(user):
    data = {
        'email': user['email'],
        'password': user['password']
    }
    x = requests.post(LOGIN_URL, json=data)
    info = json.loads(x.text)

    token = None
    if 'token' in info:
        token = info['token']
    return token, x


def delete_user(token):
    return requests.get(DELETE_USER_URL, headers={'x-access-token':token})


def add_room(token, name):
    data = { 'name' : name }
    x = requests.post(ADD_ROOM_URL, headers={'x-access-token':token}, json=data)
    info = json.loads(x.text)
    id = None
    if 'id' in info:
        id = info['id']
    return id, x


def delete_room(token, id):
    data = { 'id' : id }
    x = requests.post(DELETE_ROOMS_URL, headers={'x-access-token':token}, json=data)
    return x


def test_register_and_login():
    print('### test authentification ###')
    user, user_x = create_user('A')
    print(user_x.text)
    token, token_x = get_token(user)
    print(token_x.text)
    x = requests.get(AUTH_URL, headers={'x-access-token':token})
    print(x.text)
    x = delete_user(token)
    print(x.text)


def test_add_rooms():
    print('### test add rooms (get_rooms_admin) ###')
    
    user, user_x = create_user('A')
    token, token_x = get_token(user)
    
    room1, room1_x = add_room(token, 'aaa')
    print(room1_x.text)
    room2, room2_x = add_room(token, 'bbb')
    print(room2_x.text)

    x = requests.get(GET_ROOMS_ADMIN_URL, headers={'x-access-token':token})
    print(x.text)
    
    x = delete_room(token, room1)
    print(x.text)
    
    x = requests.get(GET_ROOMS_ADMIN_URL, headers={'x-access-token':token})
    print(x.text)

    delete_user(token)


def test_join_room():
    print('### test_join_rooms (get_rooms_member) ###')

    user_a, user_x = create_user('a')
    token_a, token_x = get_token(user_a)
    
    user_b, user_x = create_user('b')
    token_b, token_x = get_token(user_b)
    
    room, room_x = add_room(token_a, 'room') 

    x = requests.post(JOIN_ROOM_URL, headers={'x-acces-token':token}, json={'id':room})
    print(x.text)

    data = {
        'token': token_a,
        'name': 'room'
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': token_a,
        'room_id': room_id,
        'user_id': id_b
    }
    x = requests.post(DELETE_MEMBER_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': token_a,
    }
    x = requests.post(DELETE_ROOMS_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': token_a,
        'id' : id_a
    }
    requests.post(DELETE_URL, json=data)
    
    data = {
        'token': token_b,
        'id' : id_b
    }
    requests.post(DELETE_URL, json=data)


def test_add_cheques():
    print('### test_add_cheques ###')

    data = {
        'email': 'admin@test.com',
        'username': 'admin',
        'password': 'adminadmin'
    }
    requests.post(REGISTER_URL, json=data)
    
    data = {
        'email': 'admin@test.com',
        'password': 'adminadmin'
    }
    x = requests.post(LOGIN_URL, json=data)
    info = json.loads(x.text)

    data = {
        'token': info['token'],
        'name': 'room1'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    room_id = json.loads(x.text)['message'][0]['id']
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'name': 'cheque1',
        'room_id': room_id
    }
    x = requests.post(ADD_CHEQUE_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'username': 'admin'
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'room_id': room_id
    }
    x = requests.post(GET_CHEQUES_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'room_id': room_id
    }
    x = requests.post(DELETE_CHEQUE_URL, json=data)
    print(x.status_code, x.text)

    x = requests.post(DELETE_ROOMS_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'id' : info['id']
    }
    requests.post(DELETE_URL, json=data)


def main():
    test_register_and_login()
    
    test_add_rooms()
    #test_join_room()
    
    #test_add_cheques()


if __name__ == '__main__':
    main()
