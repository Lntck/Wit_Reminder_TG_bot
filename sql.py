import sqlite3
connection = sqlite3.connect('katalog.db')

cursor = connection.cursor()

sql = '''
create table if not exists products (
articul integer,
name text,
img_url text,
val integer,
price integer
)
'''

cursor.execute(sql)
connection.commit()