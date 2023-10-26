import pymysql.cursors
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Thalapathi123@',
                             database = 'thalapathi'            
                             )
cursor = connection.cursor()

sql="select * from `sd`"

cursor.execute(sql)

for i in cursor:
    print(i)