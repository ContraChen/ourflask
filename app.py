from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
import Func as fc

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)

#用户模型
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128))

#收藏夹模型
class Folder(db.Model):
    __tablename__ = "folders"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(48), unique=True)
    websites = db.relationship("Website", backref="folder")  # 关系属性

# 网址模型
class Website(db.Model):
    __tablename__ = "websites"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(48), unique=True)
    address = db.Column(db.String(192))
    star = db.Column(db.Boolean)
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"))  # 设置外键

#回收站收藏夹模型
class BinFolder(db.Model):
    __tablename__ = "binfolders"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(48), unique=True)
    binwebsites = db.relationship("BinWebsite", backref="binfolder")  # 关系属性

# 回收站网址模型
class BinWebsite(db.Model):
    __tablename__ = "binwebsites"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(48), unique=True)
    address = db.Column(db.String(192))
    binfolder_id = db.Column(db.Integer, db.ForeignKey("binfolders.id"))  # 设置外键

#注册函数
@app.route('/register',methods=["GET","POST"])
def register():
    users = User.query.all()
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if not all([username,password]):
            return render_template('register.html',msg='请输入完整表单')
        savename, savepass = fc.query_users()
        if username in savename:
            return render_template('register.html', msg='用户已存在')
        else:
            new_user = User(username=username,password=password)
            db.session.add_all([new_user])
            db.session.commit()
            return render_template('login.html', error='注册成功，欢迎登录')

@app.route('/',methods=["GET","POST"])
def login():
    #request：请求对象
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        savename,savepass=fc.query_users()
        if (username in savename) and (password in savepass):
            session['username'] = username
            return redirect('/save')
        else:
            return render_template('login.html',error='用户名或密码错误')

@app.route('/save',methods=["GET","POST"])
def save():
    folders = Folder.query.all()
    if request.method == 'GET':
        return render_template('save.html', folders=folders)
    folder_name = request.form.get('folder_name')
    website_name = request.form.get('website_name')
    website_address = request.form.get('website_address')
    if not all([folder_name, website_name, website_address]):
        return render_template('save.html', msg='请输入表单', folders=folders)
    folder = Folder.query.filter_by(name=folder_name).first()
    if folder:
        website = Website.query.filter_by(address=website_address).first()
        if website:
            return render_template('save.html', msg='网址已存在', folders=folders)
        new_website = Website(name=website_name, address=website_address)
        folder.websites.append(new_website)
        db.session.add(new_website)
        db.session.commit()
        folders = Folder.query.all()
        return render_template('save.html', msg='添加成功', folders=folders)
    else:
        website = Website.query.filter_by(address=website_address).first()
        if website:
            return render_template('save.html', msg='网址已存在', folders=folders)
        new_folder = Folder(name=folder_name)
        new_website = Website(name=website_name, address=website_address)
        new_folder.websites.append(new_website)
        db.session.add(new_website)
        db.session.add_all([new_folder])
        db.session.commit()
        folders = Folder.query.all()
        return render_template('save.html', msg='添加成功', folders=folders)

@app.route("/star")
def star():
    wid = request.args.get('wid')
    website = Website.query.get(wid)
    # result = Book.query.filter(Book.id == '1').first()
    website.star = 1-website.star
    db.session.commit()
    return redirect("/save")

@app.route("/delete_website")
def delete_website():
    wid = request.args.get('wid')
    website = Website.query.get(wid)
    db.session.delete(website)
    db.session.commit()
    return redirect("/save")

@app.route("/delete_folder")
def delete_author():
    fid = request.args.get('fid')
    folder = Folder.query.get(fid)
    websites=folder.websites
    for website in websites:
        db.session.delete(website)
    db.session.delete(folder)
    db.session.commit()
    return redirect("/save")

if __name__ == '__main__':
    app.run()
