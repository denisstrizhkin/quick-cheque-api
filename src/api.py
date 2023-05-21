from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime


# Flask app
app = Flask(__name__)

# Flask config
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# DB connection
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}' + \
    f'@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'

db = SQLAlchemy(app)


"""

## User

- ID (PK, int)
- Name (varchar(50))
- Email (UNIQUE, varchar(50))
- Password (varchar(16), min 8, eng letters + numbers)
- Photo Url (varchar(100))

## Room

- ID (PK, int)
- Name (varchar(30))
- OwnerID (FK -> User, int)

## Room <-> User

- RoomID (FK -> Room, int)
- UserID (FK -> User, int)

## Cheque

- ID (PK, int)
- RoomID (FK -> Room, int)
- OwnerID (FK -> User, int)
- Name (varchar(30))

## ProductItem

- ID (PK, int)
- Name (varchar(30))
- Price (int)
- Count (int)
- RoomId (FK -> Room)

## ProductItem <-> User

- ProductID (FK -> ProductItem, int)
- UserID (FK -> User, int)

"""


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    photo_url = db.Column(db.String(100))

    rooms = db.relationship('Room', backref='user')
    room_members = db.relationship('RoomMembers', backref='user')
    
    cheques = db.relationship('Cheque', backref='user')
    cheque_members = db.relationship('ChequeMembers', backref='user')


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable = False
    )

    cheques = db.relationship('Cheque', backref='room')
    room_members = db.relationship('RoomMembers', backref='room')


class Cheque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    room_id = db.Column(
        db.Integer,
        db.ForeignKey('room.id', ondelete='CASCADE'),
        nullable = False
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable = False
    )

    cheque_members = db.relationship('ChequeMembers', backref='cheque')


class RoomMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable = False
    )
    room_id = db.Column(
        db.Integer,
        db.ForeignKey('room.id', ondelete='CASCADE'),
        nullable = False
    )
    __table_args__ = (db.UniqueConstraint('member_id', 'room_id'),)


class ChequeMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable = False
    )
    cheque_id = db.Column(
        db.Integer,
        db.ForeignKey('cheque.id', ondelete='CASCADE'),
        nullable = False
    )
    __table_args__ = (db.UniqueConstraint('member_id', 'cheque_id'),)


def init_db():
    db.drop_all()
    db.create_all()


def verify_json_fields(json, fields):
    for field in fields:
        if not field in json:
            return False
    return True


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({ 'msg' : 'no token provided' }), 400

        try:
            json = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.filter_by(email=json['email']).first()
        except:
            return jsonify({ 'msg' : 'token is invalid' }), 400

        return f(user, *args, **kwargs)

    return decorated


def fields_required(fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            json = request.get_json()
            if not verify_json_fields(json, fields):
                return jsonify({ 'msg' : 'invalid fields'}), 400

            return f(json, *args, **kwargs)
        
        return decorated
    
    return decorator


@app.route('/register', methods=['POST'])
@fields_required(['email', 'name', 'password'])
def register(json):
    password = generate_password_hash(json['password'], method='scrypt')
    new_user = User(
        name=json['name'],
        email=json['email'],
        password=password
    )

    if User.query.filter_by(email=json['email']).first():
        return jsonify({ 'msg' : 'user already exists' }), 400
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({ 'msg' : 'user created' })


@app.route('/login', methods=['POST'])
@fields_required(['email', 'password'])
def login(json):
    user = User.query.filter_by(email=json['email']).first()
    if not user:
        return jsonify({ 'msg' : 'user does not exist' }), 400

    if not check_password_hash(user.password, json['password']):
        return jsonify({ 'msg' : 'wrong password' }), 400

    token = jwt.encode({
        'email' : user.email,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
      'token' : token,
      'id' : user.id,
      'email' : user.email,
      'name' : user.name
     })


@app.route('/auth', methods=['GET'])
@token_required
def auth(user):
    return jsonify({ 'msg' : f'access granted for {user.email}' })


@app.route('/delete_user', methods=['GET'])
@token_required
def delete_user(user):
    user = User.query.filter_by(email=user.email).first()
    db.session.delete(user)
    db.session.commit()

    return jsonify({ 'msg' : f'user deleted - {user.email}' })


@app.route('/add_room', methods=['POST'])
@token_required
@fields_required(['name'])
def add_room(json, user):
    room = Room(name=json['name'], owner_id=user.id)
    db.session.add(room)
    db.session.commit()

    return jsonify({ 'msg' : 'room created', 'id' : room.id })


@app.route('/delete_room', methods=['POST'])
@token_required
@fields_required(['id'])
def delete_room(json, user):
    room = Room.query.filter_by(id=json['id']).first()
    if not room or room.owner_id != user.id:
        return jsonify({ 'msg' : f'user does have room with id - {json["id"]}' }), 400
    
    db.session.delete(room)
    db.session.commit()

    return jsonify({ 'msg' : f'room deleted - {json["id"]}' }) 


def room_to_dic(id, is_admin):
    room = Room.query.filter_by(id=id).first()

    members = []
    for member in room.room_members:
        user = User.query.filter_by(id=member.member_id).first()
        members.append({
            "id" : user.id,
            "name" : user.name,
            "email" : user.email,
        })

    owner = User.query.filter_by(id=room.owner_id).first()

    dic = {
        'id' : room.id,
        'name' : room.name,
        'owner' : {
          'id' : owner.id,
          'name' : owner.name,
          'email' : owner.email
        },
        'cheque_cnt' : len(Cheque.query.filter_by(room_id=room.id).all()),
        'member' : members,
        'admin' : is_admin
    }

    return dic


def rooms_admin(user):
    rooms = []
    for room in user.rooms:
        rooms.append(room_to_dic(room.id, is_admin=True))
    return rooms


def rooms_member(user):
    rooms = []
    for member in user.room_members:
        room = Room.query.filter_by(id=member.room_id).first()
        rooms.append(room_to_dic(room.id, is_admin=False))
    return rooms


@app.route('/get_rooms_admin', methods=['GET'])
@token_required
def get_rooms_admin(user):
    rooms = rooms_admin(user)
    return jsonify({ 'msg' : rooms })


@app.route('/get_rooms_member', methods=['GET'])
@token_required
def get_rooms_member(user):
    rooms = rooms_member(user)
    return jsonify({ 'msg' : rooms })


@app.route('/get_rooms', methods=['GET'])
@token_required
def get_rooms(user):
    rooms = rooms_member(user) + rooms_admin(user)
    return jsonify({ 'msg' : rooms })


@app.route('/join_room', methods=['POST'])
@token_required
@fields_required(['id'])
def join_room(json, user):
    room = Room.query.filter_by(id=json['id']).first()
    if room is None:
      return jsonify({ 'msg' : f'room {json["id"]} does not exist' }), 400

    member = RoomMembers.query.filter_by(member_id=user.id, room_id=room.id).first()
    if member or room.owner_id == user.id:
        return jsonify({ 'msg' : 'this user have already joined' }), 400

    member = RoomMembers(member_id=user.id, room_id=json['id'])
    db.session.add(member)
    db.session.commit()

    return jsonify({ 'msg' : 'user have joined the room' })


@app.route('/leave_room', methods=['POST'])
@token_required
@fields_required(['id'])
def leave_room(json, user):
    room = Room.query.filter_by(id=json['id']).first()
    if room is None:
      return jsonify({ 'msg' : f'room {json["id"]} does not exist' }), 400

    member = RoomMembers.query.filter_by(member_id=user.id, room_id=json['id']).first()
    if not member:
        return jsonify({ 'msg' : 'user haven\'t joined this room' }), 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({ 'msg' : 'user have left the room' })


@app.route('/add_cheque', methods=['POST'])
@token_required
@fields_required(['room_id', 'name'])
def add_cheque(json, user):
    cheque = Cheque(
        name=json['name'],
        room_id=json['room_id'],
        owner_id=user.id
    )
    db.session.add(cheque)
    db.session.commit()

    return jsonify({ 'msg' : 'cheque added', 'id' : cheque.id })


@app.route('/delete_cheque', methods=['POST'])
@token_required
@fields_required(['id'])
def delete_cheque(json, user):
    cheque = Cheque.query.filter_by(owner_id=user.id, id=json['id']).first()
    if not cheque:
        return jsonify({ 'msg' : f"user does not have cheque - {json['id']}"}), 400

    return jsonify({ 'msg' : 'cheque deleted' })


@app.route('/join_cheque', methods=['POST'])
@token_required
@fields_required([ 'id', 'room_id' ])
def join_cheque(json, user):
    cheque = Cheque.query.filter_by(id=json['id'], room_id=json['room_id']).first()
    if cheque is None:
        return jsonify({ 'msg' : f'room {json["room_id"]} does not have cheque {json["id"]}' })

    member = ChequeMembers.query.filter_by(member_id=user.id, cheque_id=cheque.id).first()
    if member or cheque.owner_id == user.id:
        return jsonify({ 'msg' : 'this user have already joined' }), 400

    member = ChequeMembers(member_id=user.id, cheque_id=cheque.id)
    db.session.add(member)
    db.session.commit()

    return jsonify({ 'msg' : 'user have joined the cheque' })


@app.route('/leave_cheque', methods=['POST'])
@token_required
@fields_required(['id'])
def leave_cheque(json, user):
    member = ChequeMembers.query.filter_by(member_id=user.id, cheque_id=json['id']).first()
    if not member:
        return jsonify({ 'msg' : 'user haven\'t joined this cheque' }), 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({ 'msg' : 'user have left the cheque' })


def cheque_to_dic(id, room_id, is_admin):
    cheque = Cheque.query.filter_by(id=id).first()
    if cheque.room_id != room_id:
      return None

    members = []
    for member in cheque.cheque_members:
        user = User.query.filter_by(id=member.member_id).first()
        members.append({
            "id" : user.id,
            "name" : user.name,
            "email" : user.email,
        })
    
    owner = User.query.filter_by(id=cheque.owner_id).first()

    dic = {
        'id' : cheque.id,
        'name' : cheque.name,
        'owner' : {
          'id' : owner.id,
          'name' : owner.name,
          'email' : owner.email
        },
        'room_id' : cheque.room_id,
        'sum' : 0,
        'member' : members,
        'admin' : is_admin
    }

    return dic


def cheques_admin(user, room_id):
    cheques = []
    for cheque in user.cheques:
        dic = cheque_to_dic(cheque.id, room_id, is_admin=True)
        if dic:
          cheques.append(dic)
    return cheques


def cheques_member(user, room_id):
    cheques = []
    for cheque in Cheque.query.filter_by(room_id=room_id).all():
        dic = cheque_to_dic(cheque.id, room_id, is_admin=False)
        if dic:
          cheques.append(dic)
    return cheques


@app.route('/get_cheques_admin', methods=['GET'])
@token_required
def get_cheques_admin(user):
    cheques = cheques_admin(user)
    return jsonify({ 'msg' : cheques})


@app.route('/get_cheques_member', methods=['GET'])
@token_required
def get_cheques_member(user):
    cheques = cheques_member(user)
    return jsonify({ 'msg' : cheques})


@app.route('/get_cheques', methods=['POST'])
@token_required
@fields_required(['id'])
def get_cheques(json, user):
    room = Room.query.filter_by(id=json['id']).first()
    if room is None:
      return jsonify({ 'msg' : f'room {json["id"]} does not exist' })

    cheques = cheques_member(user, room.id) + cheques_admin(user, room.id)
    return jsonify({ 'msg' : cheques})
