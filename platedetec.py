import math
import time
from tkinter.font import names
from crud import *

from util import read_license_plate
import cv2
import os
from ultralytics import YOLO
import string
import easyocr
os.environ["XDG_SESSION_TYPE"] = "xcb"

import torch
import gc


# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)
license_plate_detector = YOLO('license_plate_detector.pt')

delta = 10
min_score = 0.40
max_not_seen = 1
x_porc = 0
y_porc = 0



def clear_gpu_memory():
    print("Clear GPU cache")
    torch.cuda.empty_cache()
    gc.collect()

def ocr_plate(frame, thres=90, maxval=220):

    print(f"thres {thres}, maxval {maxval}")
    license_plates = license_plate_detector(frame)[0]
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate
        xcut_por = int((x2-x1)*x_porc)
        ycut_por = int((y2 - y1) * y_porc)
        print(f"recorto {xcut_por} pixeles")
        #recortar la imagen
        license_plate_crop = frame[int(y1+ycut_por):int(y2-(ycut_por+int(ycut_por/4))), int(x1+(xcut_por+int(xcut_por/10))):int(x2-xcut_por), :]
        # process license plate
        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
        _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, thres, maxval,cv2.THRESH_BINARY)

        #license_plate_crop_thresh = cv2.adaptiveThreshold(license_plate_crop_gray, 155, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 29, 10)

        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh, thres,maxval)

        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Plate: {license_plate_text}, score:{license_plate_text_score}")
        if (license_plate_text is None):
            print(f"incremenar not_seen de todos los autos")


        if (license_plate_text is not None) and (license_plate_text_score is not None) and (license_plate_text_score > min_score):

            is_auto_out, idauto = is_auto_dout(license_plate_text)
            is_auto_out=int(is_auto_out)
            print(f"is_auto_out {is_auto_out}")
            if is_auto_out == 0:
                print("is_auto_out=0")
                inc_seen(license_plate_text,idauto, license_plate_text_score)
            else:
                print(f"se inserta el auto con placas {license_plate_text}")
                ins_new_auto(license_plate_text, score)
                break
                #return license_plate
            return license_plate
        else:
            license_plate_text_score=0
            print(f"No se detectaron placas. Intento de nuevo con otros parametros {thres+delta}, {maxval+delta}")
            if(thres<10):
                #thres = 40
                #maxval =  120
                return 0
            if (maxval+delta) > 250:
                #thres = 40
                maxval =220
                return 0

            else:
                if license_plate_text_score < min_score:
                    #thres = thres + delta
                    maxval = maxval + delta
        ocr_plate(frame, thres , maxval )
        return license_plate, score
    return 0


