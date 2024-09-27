from conn import conn_op
import time
import math
max_not_seen =20

def exist_auto(plate):
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "SELECT * FROM autos WHERE placa = %s and dateout = %s order by id desc limit 1"
    pl = (plate, 0,)
    my_cursor.execute(sql, pl)
    result = my_cursor.fetchall()
    idauto = result[0][0]
    my_con.close()
    print(f"el auto con placas {plate} tiene id {idauto}")
    if len(result) == 0:
        return 0
    else:
        return 1, idauto

def up_fecha_liquidar(idauto):
    print(f"se actualiza la fecha de salida al auto con id: {idauto}")
    dateout = time.strftime("%Y-%m-%d %H:%M:%S")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set dateout = %s  where   id = %s"
    pl = (dateout, idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    my_con.close()
    liquidar_auto(idauto)


def is_paid_auto():
    print("chequear si ya se liquido el auto...")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "SELECT * FROM autos order by id desc limit 1"
    # pl = (plate,)
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    print(result)
    dout = result[0][3]
    idauto = result[0][0]
    my_con.close()
    return dout, idauto

def ins_new_auto(plate,score):
    datein = time.strftime("%Y-%m-%d %H:%M:%S")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    print(f"valores de placa:{plate}, score:{score}, datein:{datein} para hacer insersion")
    sql = "INSERT INTO autos (placa, datein, score) VALUES(%s,%s, %s)"
    vals = (plate, datein,score,)
    my_cursor.execute(sql, vals)
    my_con.commit()
    my_con.close()


def upd_auto():
    pass

def inc_seen(plate, idauto, score):
    print(f"incrementar el contador seen de la placa {plate} e idauto {idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set seen = seen + 1, lastseen = %s, score = %s  where  placa = %s and id = %s"
    my_now = time.strftime("%Y-%m-%d %H:%M:%S")
    pl = (my_now,score, plate ,idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    clr_notseen(plate, idauto)
    my_con.close()
    clr_notseen(plate, idauto)

def inc_not_seen_all():

    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set notseen = notseen + 1  where  id > %s"
    pl = (0,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    print("Se incremento not_seen de todos los autos")
    my_con.close()


def inc_not_seen(idauto):
    my_id_auto = idauto
    print(f"incrementar el contador NOTseen del id {idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set notseen = notseen + 1  where  id = %s"
    pl = (idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    sql = "select notseen from autos where id = %s"
    idauto = (idauto,)
    my_cursor.execute(sql, idauto)
    result = my_cursor.fetchall()
    my_con.close()
    # print(result)
    # print(f"result not seen del id {idauto}")

    # not_seen = 0
    (not_seen) = result[0][0]
    not_seen = int(not_seen)
    # print(not_seen)
    if not_seen > max_not_seen:
        set_dout_auto(my_id_auto)

def last_seen():
    pass

def clr_notseen(plate, idauto):
    print("limpiar el contador NOTseen")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set notseen = 0  where  placa = %s and id = %s"
    pl = (plate, idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()

def liquidar_auto(idauto):
    print(f"liquidar auto con id{idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "select placa,datein, dateout,  TIMEDIFF(dateout,datein) as minutes from autos where dateout >0 and id = %s"
    pl = (idauto,)
    my_cursor.execute(sql, pl)
    result = my_cursor.fetchall()
    print(f"result {result} del id {idauto} para liquidar")

    alltime = result[0][3].total_seconds()
    # totalseg = alltime.total_seconds()
    totalhoras = math.ceil(alltime / 3600)
    # print(totalseg)
    print(f"horas a liquidar: {totalhoras}")
    sql = "SELECT * FROM tarifas"
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    total_pago = result[0][0] * totalhoras
    print(f"${total_pago}")
    return total_pago

def set_dout_auto(idauto):
    print(f"se da salida al auto con id: {idauto}")
    dateout = time.strftime("%Y-%m-%d %H:%M:%S")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set dateout = %s  where   id = %s"
    pl = ( dateout,idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    my_con.close()
    liquidar_auto(idauto)

def is_auto_dout(plate):
    print("chequear si ya se liquido el auto...")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "SELECT * FROM autos order by id desc limit 1"
    # pl = (plate,)
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    #print(f"resultado de is_auto_dout {result}")
    if(len(result))==0:
        ins_new_auto(plate,0.5)
        return 0,1
    dout = result[0][3]
    print(f"valor dout: {dout} para la placa {plate}")
    idauto = result[0][0]
    if (len(dout))>1:
        return 1, idauto
    my_con.close()
    return dout, idauto