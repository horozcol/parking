import mysql.connector
cnx = None
def conn_op():
    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        passwd="Dev.123789",
        database="parkdb",
    )
    return cnx

def conn_cl():
    cnx.close()