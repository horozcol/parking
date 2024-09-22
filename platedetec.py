import math
import time
from tkinter.font import names

from torch.utils.hipify.hipify_python import is_out_of_place

from util import read_license_plate
import cv2
import os
from ultralytics import YOLO
import string
import easyocr
os.environ["XDG_SESSION_TYPE"] = "xcb"
from conn import conn_op

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)
license_plate_detector = YOLO('license_plate_detector.pt')

delta = 10
thres = 80
maxval = 200
min_score = 0.39
max_not_seen = 1
def ocr_plate(frame, thres=80, maxval=150):

    license_plates = license_plate_detector(frame)[0]
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate
        license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
        # process license plate
        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
        _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, thres, maxval,cv2.THRESH_BINARY_INV)
        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
        print(f"Plate: {license_plate_text}, score:{license_plate_text_score}")
        if (license_plate_text is not None) and (license_plate_text_score is not None) and (license_plate_text_score > min_score):
            is_new_auto(license_plate_text)
        else:
            print(f"No se detectaron placas. Intento de nuevo con otros parametros {thres+delta}, {maxval-delta}")
            is_auto_out, idauto = is_auto_dout(license_plate_text)
            if (len(is_auto_out))>1:
                return 0,0

            is_auto_out = int(is_auto_out)


            if is_auto_out == 0:
                print("is_auto_out=0")
                inc_not_seen(idauto)
                print(is_auto_out)
            if (thres+delta) < 10:
                thres = 150
            if (maxval+delta) >250:
                maxval=0
            else:
                ocr_plate(frame, thres - delta, maxval + delta)
        return 0, 0

def insert_new_auto(plate):

    datein = time.strftime("%Y-%m-%d %H:%M:%S")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "INSERT INTO autos (placa, datein) VALUES(%s,%s)"
    vals = (plate, datein,)
    my_cursor.execute(sql, vals)
    my_con.commit()
    my_con.close()

def is_new_auto(plate):
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "SELECT * FROM autos WHERE placa = %s and dateout = %s order by id desc limit 1"
    pl = (plate,0,)
    my_cursor.execute(sql, pl)
    result = my_cursor.fetchall()
    if len(result) == 0:
        insert_new_auto(plate)
    else:
        idauto = result[0][0]
        inc_seen(plate, idauto)
    my_con.close()

def inc_seen(plate, idauto):
    print(f"incrementar el contador seen de la placa {plate} e idauto {idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set seen = seen + 1  where  placa = %s and id = %s"
    pl = (plate,idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    cero_notseen(plate,idauto)
    my_con.close()

def is_auto_dout(plate):
    print("chequear si ya se liquido el auto...")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "SELECT * FROM autos order by id desc limit 1"
    #pl = (plate,)
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    print(result)
    dout = result[0][3]
    idauto = result[0][0]
    my_con.close()
    return dout,idauto

def inc_not_seen(idauto):
    my_id_auto = idauto
    print(f"incrementar el contador NOTseen del id {idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set notseen = notseen + 1  where  id = %s"
    pl = ( idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()
    sql = "select notseen from autos where id = %s"
    idauto =(idauto,)
    my_cursor.execute(sql, idauto)
    result = my_cursor.fetchall()
    my_con.close()
    #print(result)
    #print(f"result not seen del id {idauto}")


    #not_seen = 0
    (not_seen) = result[0][0]
    not_seen = int(not_seen)
    #print(not_seen)
    if not_seen > max_not_seen :
        set_dout_auto(my_id_auto)



def cero_notseen(plate,idauto):
    print("limpiar el contador NOTseen")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "update autos set notseen = 0  where  placa = %s and id = %s"
    pl = (plate,idauto,)
    my_cursor.execute(sql, pl)
    my_con.commit()

def liquidar_auto(idauto):
    print(f"liquidar auto con id{idauto}")
    my_con = conn_op()
    my_cursor = my_con.cursor()
    sql = "select placa,datein, dateout,  TIMEDIFF(dateout,datein) as minutes from autos where dateout >0 and id = %s"
    pl = (idauto,)
    my_cursor.execute(sql,pl)
    result = my_cursor.fetchall()

    alltime =result[0][3].total_seconds()
    #totalseg = alltime.total_seconds()
    totalhoras = math.ceil(alltime/3600)
    #print(totalseg)
    print(f"horas a liquidar: {totalhoras}")
    sql = "SELECT * FROM tarifas"
    my_cursor.execute(sql)
    result = my_cursor.fetchall()
    total_pago = result[0][0] * totalhoras
    print(f"${total_pago}")


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







