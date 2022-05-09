from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.qvulw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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


@app.route('/drama', methods=["GET"])
def detail():
    return render_template("detail.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


    