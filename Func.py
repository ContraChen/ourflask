import pymysql

def query_users():
    username = []
    password = []
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='ourflask',charset='utf8')
    cur = conn.cursor()
    sql = 'select * from users'
    cur.execute(sql)
    for id,name,word in cur.fetchall():
        username.append(name)
        password.append(word)
    cur.close()
    conn.close()
    return username,password

# username,password=read_users()
# print(username,password)