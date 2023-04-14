import mysql.connector 
# connect to the database "mydatabase"

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="attendance"
)

mycursor = mydb.cursor()
#mycursor.execute("CREATE TABLE accounts (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), password VARCHAR(255))")

# add a new record
sql = "INSERT INTO accounts (name, password) VALUES (%s, %s)"
val = ("ahmed", "1234")
mycursor.execute(sql, val)
mydb.commit()

