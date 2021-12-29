from flask import Flask, render_template, request, redirect, session,jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
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
        new_website = Website(name=website_name, address=website_address,star=0)
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
        new_website = Website(name=website_name, address=website_address,star=0)
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

@app.route("/undostar")
def undostar():
    wid = request.args.get('wid')
    website = Website.query.get(wid)
    website.star = 1-website.star
    db.session.commit()
    return redirect("/collect")

@app.route("/collect")
def collect():
    folders = Folder.query.all()
    return render_template('collect.html',folders=folders)

@app.route("/plots")
def plots():
    return render_template('plots.html')

@app.route("/bin")
def bin():
    binfolders = BinFolder.query.all()
    return render_template('bin.html',binfolders=binfolders)

@app.route("/restore_binfolder")
def restore_binfolder():
    fid = request.args.get('fid')
    binfolder = BinFolder.query.get(fid)
    binwebsites = binfolder.binwebsites
    folder = Folder.query.filter_by(name=binfolder.name).first()
    if folder:
        for binwebsite in binwebsites:
            new_website = Website(name=binwebsite.name, address=binwebsite.address,star=0)
            folder.websites.append(new_website)
            db.session.add(new_website)
            db.session.add_all([folder])
            db.session.commit()
            db.session.delete(binwebsite)
            db.session.commit()
    else:
        new_folder = Folder(name=binfolder.name)
        for binwebsite in binwebsites:
            new_website = Website(name=binwebsite.name, address=binwebsite.address,star=0)
            new_folder.websites.append(new_website)
            db.session.add(new_website)
            db.session.add_all([new_folder])
            db.session.commit()
            db.session.delete(binwebsite)
            db.session.commit()
    db.session.delete(binfolder)
    db.session.commit()
    return redirect("/bin")

@app.route("/delete_binwebsite")
def delete_binwebsite():
    wid = request.args.get('wid')
    binwebsite = BinWebsite.query.get(wid)
    db.session.delete(binwebsite)
    db.session.commit()
    return redirect("/bin")

@app.route("/delete_binfolder")
def delete_binfolder():
    fid = request.args.get('fid')
    binfolder = BinFolder.query.get(fid)
    binwebsites=binfolder.binwebsites
    for binwebsite in binwebsites:
        db.session.delete(binwebsite)
    db.session.delete(binfolder)
    db.session.commit()
    return redirect("/bin")

@app.route("/delete_website")
def delete_website():
    wid = request.args.get('wid')
    website = Website.query.get(wid)
    db.session.delete(website)
    db.session.commit()
    return redirect("/save")

@app.route("/delete_folder")
def delete_folder():
    fid = request.args.get('fid')
    folder = Folder.query.get(fid)
    websites = folder.websites
    binfolder = BinFolder.query.filter_by(name=folder.name).first()
    if binfolder:
        for website in websites:
            new_binwebsite = BinWebsite(name=website.name, address=website.address)
            binfolder.binwebsites.append(new_binwebsite)
            db.session.add(new_binwebsite)
            db.session.add_all([binfolder])
            db.session.commit()
            db.session.delete(website)
            db.session.commit()
    else:
        new_binfolder = BinFolder(name=folder.name)
        for website in websites:
            new_binwebsite = BinWebsite(name=website.name, address=website.address)
            new_binfolder.binwebsites.append(new_binwebsite)
            db.session.add(new_binwebsite)
            db.session.add_all([new_binfolder])
            db.session.commit()
            db.session.delete(website)
            db.session.commit()
    db.session.delete(folder)
    db.session.commit()
    return redirect("/save")

@app.route('/getfolder')
def getfolder():  # put application's code here
    conn = pymysql.connect(host='127.0.0.1',user='root',password='123456',db='ourflask')
    cur = conn.cursor()
    sql = 'SELECT a.name,COUNT(b.name) FROM websites b,FOLDERS a WHERE b.folder_id=a.id GROUP BY a.name'
    cur.execute(sql)
    u=cur.fetchall()
    jsonData = {}
    foldername = []
    websitecount = []

    for data in u:
        foldername.append(data[0])
        websitecount.append(data[1])

    jsonData['foldername'] = foldername
    jsonData['websitecount'] = websitecount

    cur.close()
    conn.close()
    return jsonify(jsonData)

if __name__ == '__main__':
    app.run()
