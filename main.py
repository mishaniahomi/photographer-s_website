from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os



UPLOAD_FOLDER = '/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_folder="img")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.String(200))
    photo_path = db.Column(db.String(200))
    text = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.String(200))
    text = db.Column(db.Text, nullable=True)
    photo_path = db.Column(db.String(200))
    Article_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Photo %r>' % self.id


@app.route('/home')
@app.route('/')
def index():
    articlies = Article.query.order_by(Article.id).all()
    return render_template("home.html", articlies=articlies)


@app.route('/about')
def about():
    return render_template("index.html")


@app.route('/photo/<int:id>')
def photo(id):
    Photos = Photo.query.filter_by(Article_id=id).all()
    lenght = len(Photos)
    article = Article.query.get(id)
    return render_template("index.html", Photos=Photos, lenght=lenght, article=article)


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        intro = request.form['intro']
        photo_path = "/img/" + str(request.form['photo_path'])
        text = request.form['text']
        article = Article(intro=intro, photo_path=photo_path, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавлении произошла ошибка"
    else:
        directory = 'img'
        files = os.listdir(directory)
        return render_template('create-article.html', files=files)


@app.route('/posts/<int:id>/editA', methods=['POST', 'GET'])
def editA(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.intro = request.form['intro']
        if article.photo_path != str(request.form['photo_path']):
            article.photo_path = "/img/" + str(request.form['photo_path'])
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "При добавлении произошла ошибка"
    else:
        directory = 'img'
        files = os.listdir(directory)

        return render_template('postA_update.html', files=files, article=article)


@app.route('/add_photo', methods=['POST', 'GET'])
def add_photo():
    if request.method == "POST":
        article_id = request.form['article']
        intro = request.form['intro']
        photo_path = "/img/" + str(request.form['photo_path'])
        text = request.form['text']
        photo = Photo(intro=intro, photo_path=photo_path, Article_id=article_id, text=text)

        try:
            db.session.add(photo)
            db.session.commit()
            return redirect('/posts')
        except:
            return "При добавлении произошла ошибка"

    else:
        articlies = Article.query.order_by(Article.id).all()
        directory = 'img'
        files = os.listdir(directory)
        return render_template('add_photo.html', articlies=articlies, files=files)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/imgload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = "img\\" + str(secure_filename(file.filename))
            print(filename)
            file.save(filename)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


from flask import send_from_directory


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/posts')
def posts():
    articlies = Article.query.order_by(Article.id).all()
    photos = Photo.query.order_by(Photo.id).all()
    return render_template('posts.html', articlies=articlies, photos=photos)


@app.route('/posts/<int:id>/deleteA')
def deleteA(id):
    article = Article.query.get_or_404(id)
    Photos = Photo.query.filter_by(Article_id=id).all()
    try:
        db.session.delete(article)
        for ph in Photos:
            db.session.delete(ph)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении альбома произошла ошибка"


@app.route('/posts/<int:id>/deleteP')
def deleteP(id):
    select_photo = Photo.query.get_or_404(id)
    try:
        db.session.delete(select_photo)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении фотографии произошла ошибка"


if __name__ == "__main__":
    app.run(debug=True)
