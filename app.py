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

@app.route('/') ## 병관님 - jinja2 SSR 이 부분에서 처리됨 ##
def home():
    drama_list = list(db.drama.find({}, {'_id': False}))
    print (drama_list)
    return render_template('/index.html', dramas=drama_list)

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

    # 아래는 jinja2 방식으로 mypage를 SSR 해본 것. 삭제기능과 어울리지 않아 버림.
    # token_receive = request.cookies.get('mytoken')
    # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    # userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
    # usernick = userinfo['nick']
    # print(usernick)
    # search_drama = list(db.drama.find({'$or': [{'usernick': {'$regex': usernick}},
    #                                            ]}, {'_id': False}))
    # print(search_drama)
    # return render_template('mypage.html', dramas=search_drama)

@app.route('/write_index')
def write_index():
    return render_template('write_index.html')




########## 게시물 기입 - 천희님 ##########

@app.route('/drama', methods=["POST"])
def write_post():
    userid_receive = request.form['userid_give']
    usernick_receive = request.form['usernick_give']
    title_receive = request.form['title_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    synopsis_receive = request.form['synopsis_give']
    image_receive = request.form['image_give']

    doc = {
        'userid' : userid_receive,
        'usernick' : usernick_receive,
        'title': title_receive,
        'image': image_receive,
        'star': star_receive,
        'synopsis': synopsis_receive,
        'comment': comment_receive
    }
    db.drama.insert_one(doc)
    return jsonify({'msg': '저장 되었습니다.'})


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
    print(result)

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token, 'nick': result['nick']})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

########## 재영 -유저 확인 API ##########

@app.route('/api/login/user_check')
def user_check():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        id_nick = {'id': userinfo['id'], 'nick': userinfo['nick']}
        print(id_nick)
        return jsonify({'result': 'success', 'userinfo': id_nick})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 해주세요.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 해주세요.'})

##### 마이페이지 - 내 글만 리스팅 및 삭제 기능 #####

@app.route('/api/mypage/list')
def mypage_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
    usernick = userinfo['nick']
    my_drama = list(db.drama.find({'usernick': usernick},{'_id': False}))
    return jsonify ({'result': 'success', 'my_drama': my_drama})

@app.route('/api/mypage/delete', methods=['POST'])
def mypage_delete():
    title_receive = request.form['title_give']

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
    nick_receive = userinfo['nick']
    print (title_receive, nick_receive)
    db.drama.delete_one({'usernick': nick_receive} and {'title':title_receive})

    return jsonify ({'msg': '게시물을 삭제했습니다.'})


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


# 탈퇴 페이지 진입 시 토큰 확인
@app.route('/withdraw')
def withdraw():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
        user_id = userinfo['id']
        return render_template('withdraw.html', id=user_id)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))


# 유저 정보 삭제
@app.route("/withdraw/delete", methods=["POST"])
def withdraw_delete():
    id_receive = request.form['id_give']
    db.drama.delete_many({'userid': str(id_receive)})
    db.users.delete_one({'id': str(id_receive)})

    return jsonify({'msg': '탈퇴가 완료되었습니다.'})


@app.route('/change_pw')
def change_pw():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
        # user_id = userinfo['id']
        return render_template('change_pw.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))


# 현재 비밀번호 확인
@app.route('/check_pw', methods=['POST'])
def check_pw():
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
        user_pw = userinfo['pw']
        if user_pw == pw_hash:
            return jsonify({'result': 'success', 'same': 'pass'})
        else:
            return jsonify({'result': 'fail', 'same': 'fail'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))


# 비밀번호 변경
@app.route("/change_pw/update", methods=["POST"])
def update_pw():
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': False})
        user_id = userinfo['id']
        db.users.update_one({'id': str(user_id)}, {'$set': {'pw': pw_hash}})
        return jsonify({'result': 'success'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))


############ 병관 ############



@app.route('/search_drama', methods=["POST"])
def drama_get():
    search_d_receive = request.form['search_d_give']
    drama_list = list(db.drama.find( {},{'_id':False}) )
    print(drama_list)
    return jsonify({'dramas': drama_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
