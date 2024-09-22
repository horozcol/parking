import tkinter as tk
from tkinter import Label
from ultralytics import YOLO
import cv2
from conn import conn_op
import os
from platedetec import ocr_plate

os.environ["XDG_SESSION_TYPE"] = "xcb"
#dictionary
results = {}
# load models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('license_plate_detector.pt')
vehicles = [2, 5, 7]


# URL de la cámara IP
CAMERA_URL = "./placa5.png"  # Reemplaza con la URL de tu cámara

class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cámara IP y Hora Actual")

        # Etiqueta para mostrar el video
        self.video_label = Label(master)
        self.video_label.pack()

        # Etiqueta para mostrar la hora
        self.time_label = Label(master, font=("Helvetica", 16))
        self.time_label.pack()

        # Iniciar la captura de video

        self.update_video()
    def update_video(self):
        cap = cv2.VideoCapture(CAMERA_URL)
        ret, frame = cap.read()
        plate,accurate = ocr_plate(frame)

        self.video_label.after(10, self.update_video)


    # ask for a plate
    """def auto_exist(self, placa):
        my_con = conn_op()
        my_cursor = my_con.cursor()
        sql = 'INSERT INTO autos(placa, datein, dateout,path) VALUES(%s,%s,%s,%s)'
        vals = (placa)
        my_cursor.execute(sql, vals)
        my_con.commit()
        my_con.close()
        """



    """def __del__(self):
        if self.vid.isOpened():
            self.vid.release()"""

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
