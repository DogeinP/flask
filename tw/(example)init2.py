from flask import Flask, request, jsonify, Response, g
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import bcrypt, jwt
from datetime import datetime, timedelta
from functools import wraps


def create_app(test_config = None):
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_pyfile(test_config)
        
    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database
    
    return app

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)

def
    
def login_required(f):
    @wraps(f)
    def decorated_funtion(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None
            
            if payload is None: return Response(status=401)
            
            user_id = payload['user_id']
            g.user_id = user_id
            g.user = get_user_info(user_id) if user_id else None
        else:
            return Response(status=401)
        
        return f(*args, **kwargs)
    return decorated_funtion

    
app = create_app()
app.ChildProcessErrorsers = {}
app.id_count = 1
app.tweets = []
app.json_encoder = CustomJSONEncoder

@app.route('/')
def index():
    return "Hello Flask"

@app.route('/sign-up',methods=['POST'])
def sign_up():
    new_user = request.json
    new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'),bcrypt.gensalt())
    new_user_id = app.database.execute(text("""
    INSERT INTO users(
    name, email, profile, hashed_password)
    VALUES(
    :name, :email, :profile, :password)"""), new_user).lastrowid
    
    row = app.database.execute(text("""
    SELECT id, name, email, profile FROM users WHERE id = :user_id"""),{"user_id":new_user_id}).fetchone()
    
    created_user ={
        "id" :row["id"],
        "name" : row["name"],
        "email" : row["email"],
        "profile" : row["profile"]
    } if row else None
    return jsonify(created_user)

@app.route('/tweet', methods=['POST'])
@login_required
def tweet():
    user_tweet = request.json
    user_tweet['id'] = g.user_id
    tweet = user_tweet['tweet']
    
    if len(tweet) > 300:
        return "300자를 초과하였습니다.", 400
    
    app.database.execute(text("""
    INSERT INTO tweets (
    user_id, tweet)
    VALUES ( :id, :tweet)"""), user_tweet)
    
    return '', 200
        

@app.route('/follow', methods=['POST'])
@login_required
def follow():
    payload = request.json
    
    inspect_ids = app.database.execute(text("""
    SELECT id FROM users""")).fetchall()
    
    inspect_id = [ row['id'] for row in inspect_ids]
    
    if user_id not in inspect_id or user_id_to_follow not in inspect_id:
        return '사용자가 없습니다.', 400
    
    app.database.execute(text("""
    INSERT INTO users_follow_list (
    user_id, follow_user_id)
    VALUES (:id, :fui)"""),{'id':user_id, 'fui':user_id_to_follow})
    return '', 200

@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])
    
    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 없습니다.', 400
    
    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)
    
    return jsonify(user)

@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    rows = app.database.execute(text("""
    SELECT t.user_id, t.tweet
    FROM tweets t
    LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
    WHERE t.user_id = ufl.follow_user_id"""),{'user_id':user_id}).fetchall()
    
    timeline = [{
        "user_id" : row['user_id'],
        "tweet" : row['tweet']
    } for row in rows]
    return jsonify({"user_id" : user_id, "tweet":timeline})

@app.route('/login',methods=['POST'])
def login():
    credential = request.json
    email = credential['email']
    password = credential['password']
    
    row = app.database.execute(text("""
    SELECT id, hashed_password
    FROM users
    WHERE email =:email"""),{'email':email}).fetchone()
    
    if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
        user_id = row['id']
        payload = {'user_id':user_id,
                  'exp':datetime.utcnow() + timedelta(seconds = 60*60*24)}
        token = jwt.encode(payload, app.config['JWT_SECRET_KEY'],'HS256')
        return jsonify({'access_token':token.decode('UTF-8')})
    else:
        return '',401