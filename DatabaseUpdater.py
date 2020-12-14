import mysql.connector

kulyutmazDatabase = ""

cloudDatabase = mysql.connector.connect(kulyutmazDatabase)
localDatabase = mysql.connector.connect(host)
