from flask import Blueprint, request, jsonify, session, current_app as app
from werkzeug.security import check_password_hash , generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User
from  website.database import db
from datetime import datetime
from flask_caching import Cache
import time
auth = Blueprint('auth', __name__)

app.config["CACHE_TYPE"] = "RedisCache"
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_HOST'] = "localhost"
app.config['CACHE_REDIS_PORT'] = 6379
app.config["CACHE_REDIS_URL"] = "redis://localhost:6379"  
app.config['CACHE_DEFAULT_TIMEOUT'] = 30
cache= Cache(app)



@app.route('/testing_cache')
@cache.cached(timeout=10)
def testingcache():
    time.sleep(10)
    return "Sucessfully cache"

@auth.route('/', methods=['POST'] )
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = str(data.get('email'))
        password = str(data.get('password'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            user.activeTime = datetime.now()
            db.session.commit()
            access_token = create_access_token(identity=user.id)
            
            return jsonify({'success': True, 'access_token': access_token, 'user_id':user.id}), 200
        else:
            return jsonify({'success': False, 'messages': 'Invalid email or password. Please try again or create an account.'}), 401
    else: 
            return jsonify({ 'messages': 'You are redirecting to Login Page'})






@auth.route('/signup', methods = ['GET', 'POST'])
def  signup():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        fname = data.get('firstname')
        lname = data.get('lastname')
        password1 = data.get('password1')
        password2 = data.get('password2')
        
        session['user_name'] = fname
        
        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({'messages':'You already have created an account. You should login with this email id or use a different email id.'}), 400
        elif len(fname) < 3:
            return jsonify({'messages':'First Name must be greater than 2 charachters.'}), 400
        elif str(password1) != str(password2):
            return jsonify({'messages':'Your passwords are not maching with each other.'}), 400
        elif len(password1) < 4:
            return jsonify({'messages':'Minimum length of the password should be 4 charachters.'}), 400
        else:

            new_user = User(email= email, first_name = fname, password = generate_password_hash(password1) , last_name = lname ,activeTime= datetime.now())
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.id
            access_token = create_access_token(identity=new_user.id)
            return jsonify({'success': True, 'messages': 'Welcome to Nuz Music App.', 'access_token': access_token}), 201
            

    return jsonify({'messages': 'Navigate to the signup page using Vue.js'})







@auth.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    # Perform any additional cleanup or logging here if needed
    return jsonify({'success': True, 'user_id': user_id, 'message': 'Successfully logged out'})

