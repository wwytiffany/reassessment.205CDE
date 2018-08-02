import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "10gicafe",
                           db = "company")
    c = conn.cursor()

    return c, conn
