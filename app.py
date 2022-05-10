from pymongo import MongoClient
import certifi
import jwt, datetime, hashlib

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.qvulw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
app = Flask(__name__)

SECRET_KEY = 'SPARTA'


########## HTML 파일 주기 (단순 페이지 이동 함수들은 여기에 정리) ##########

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/write_index')
def write_index():
    return render_template('write_index.html')



########## 게시물 기입 - 천희님 ##########


@app.route('/drama', methods=["POST"])
def write_post():
    title_receive = request.form['title_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    synopsis_receive = request.form['synopsis_give']
    image_receive = request.form['image_give']

    doc = {
        'title': title_receive,
        'image': image_receive,
        'star': star_receive,
        'synopsis': synopsis_receive,
        'comment': comment_receive
    }
    db.drama.insert_one(doc)
    return jsonify({'msg': 'saved'})


# @app.route('/drama', methods=["GET"])
# def detail():
#     return render_template("detail.html")


############ 재영 로그인 API #################

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:

        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=500)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


############  [유저 정보 확인 API] ############

@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


############ ############


############ 혜준 ############
# 회원가입 API
@app.route('/api/register', methods=['POST'])
def sign_up():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nick_receive = request.form['nick_give']

    password_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        "id": id_receive,
        "pw": password_hash,
        "nick": nick_receive,
    }
    db.users.insert_one(doc)

    return jsonify({'result': 'success'})


# 아이디 중복 확인
@app.route('/api/register/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

############ 병관 ############


@app.route('/drama', methods=["GET"])
def drama_get():
    drama_list = list(db.drama.find({},{'_id':False}))
    return jsonify({'dramas': drama_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
