import cv2
import tkinter as tk
from tkinter import Label, Button, Entry, ttk
from tkinter import *
from PIL import Image, ImageTk
from platedetec import ocr_plate, clear_gpu_memory
from crud import inc_not_seen_all, exist_auto, liquidar_auto, up_fecha_liquidar
from util import crea_image
# Reemplaza con la URL de tu cámara IP
camera_url = "http://192.168.1.172"


class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cámara IP")

        self.video_source = camera_url

        self.label = Label(master, text="Para retirar una placa, presione la tecla P e ingresele en la consola: ", font=("Arial",25))
        self.label.grid(row=10, column=10)

        #self.tx_placa = Entry(master, textvariable='Ingrese la placa')
        #self.tx_placa.grid(row=60,column=80)

        #self.bt_pago = Button( command=self.btpago_click(), text="Submit")
        #self.bt_pago.grid(row=60, column=60)

        self.update()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def win_pago(self):
        #print("estoy en win_pago")

        pass


    def update(self):
        self.win_pago()
        self.vid = cv2.VideoCapture(self.video_source)
        ret, frame = self.vid.read()
        if ret:

            # Convertir el frame a formato RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convertir a imagen de PIL
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            #self.label.imgtk = imgtk
            #self.label.configure(image=imgtk)
            print("llamo a la funcion ocr_plate")
            plate = ocr_plate(frame)
            type(f"tipo objeto plate {plate}")
            #int(plate)
            print(f"plate retornada por ocr_plate: {plate}")
            crea_image(frame, "in")
            if plate == 0:
                inc_not_seen_all()
        # Llamar a la función de actualización cada 10 ms
        self.label.after(10, self.update)
        #self.win_pago(100, self.update)

    def btpago_click(self):
        placa = self.tx_placa.get()
        print(f"se va a liquidar el auto {placa}")

    def on_closing(self):
        self.vid.release()
        self.master.destroy()
def win_pago():

       placa_retirar = input("+++++++++++++++++++++++++++++Que placa quiere retirar++++++++++++++++++++++++++++++++++++++++++\n")
       placa_retirar = placa_retirar.upper().replace(' ','').replace('-','')
       print(f"Busco la placa {placa_retirar} en la bd.")
       r, idauto = exist_auto(placa_retirar)
       r = int(r)
       idauto = int(idauto)

       if r==0:
           print(f"La placa {placa_retirar} no existe en la base de datos o ya fue retirado por el sistema, por favor verifique los datos ingresados.")
       else:
           print(f"Se retira la placa {placa_retirar} con id {idauto}")
           up_fecha_liquidar(idauto)
           total_pago = liquidar_auto(idauto)
           print(f"El auto paga ${total_pago}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.bind("p", lambda _:win_pago())
    root.mainloop()
