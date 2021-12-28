#SQLAlchemy操作
from app import db, User
# 会删除所有继承db.Model的表
db.drop_all()
# 会创建所有继承自db.Model的表,会丢失数据库表中所有的数据
db.create_all()

user1 = User(username = 'admin',password = '123456')
user2 = User(username = 'chenchi',password = '12138')

# 把数据提交
db.session.add_all([user1,user2])
# 提交会话
db.session.commit()