#SQLAlchemy操作
from app import db,User,Folder,Website,BinWebsite,BinFolder
# 会删除所有继承db.Model的表
db.drop_all()
# 会创建所有继承自db.Model的表,会丢失数据库表中所有的数据
db.create_all()

user1 = User(username = 'admin',password = '123456')
user2 = User(username = 'chenchi',password = '12138')

fd1 = Folder(name='搜索')
fd2 = Folder(name='购物')
fd3 = Folder(name='学习')
bfd1 = BinFolder(name='学习')

ws1= Website(name='百度',address='https://www.baidu.com/')
ws2= Website(name='知乎',address='https://www.zhihu.com/')
ws3= Website(name='淘宝',address='https://www.taobao.com/')
ws4= Website(name='京东',address='https://www.jd.com/')
ws5= Website(name='学习通',address='http://i.mooc.chaoxing.com/')
bws1= BinWebsite(name='中国大学Mooc',address='https://www.icourse163.org/')

fd1.websites.append(ws1)
fd1.websites.append(ws2)
fd2.websites.append(ws3)
fd2.websites.append(ws4)
fd3.websites.append(ws5)
bfd1.binwebsites.append(bws1)

# 把数据提交
db.session.add_all([user1,user2])
db.session.add_all([fd1,fd2,fd3])
db.session.add_all([bfd1])
# 提交会话
db.session.commit()