from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
import Func as fc

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)

#登录模型
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128))

@app.route('/',methods=["GET","POST"])
def home():
    return render_template('home.html')

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
            return render_template('register.html', msg='添加成功')

#登录界面
@app.route('/login',methods=["GET","POST"])
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

@app.route('/save')
def index():
    return "恭喜登录成功"
if __name__ == '__main__':
    app.run()
