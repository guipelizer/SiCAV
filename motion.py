from threading import Thread
import imutils
import cv2
import time
from getPlate import PlateID
import time
from flaskext.mysql import MySQL
class Movement:
    
    def __init__(self, camera, bd):
        self.bd = bd
        self.camera = camera
        self.motion = False
        self.plate = None
        self.nome = None
        self.modelo = None
        self.cargo = None
        self.i = 0;
        self.plateID = PlateID()

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self


    def update(self):
        firstFrame = None
        while True:
            frame = self.camera.read()
                    
            firstFrame, img = self.getFrame(frame=frame, firstFrame=firstFrame)
            if self.motion == True:
                while self.motion == True:    
                    self.motion = False
                    frame = self.camera.read()
                    firstFrame, img = self.getFrame(frame=frame, firstFrame=firstFrame)
                print('oi')
                arq = '/home/pi/static/motion'
                ext = '.jpg'
                cv2.imwrite(arq+ext, frame)
                time.sleep(0.2)                
                #cv2.imwrite(arq+str(self.i)+ext, img)
                self.i = self.i + 1                
                possible_plate = self.plateID.getPlate(arq='/home/pi/static/motion.jpg')
                if possible_plate != None:
                    self.plate = possible_plate
                    conn = self.bd.connect()
                    cursor = conn.cursor()
                    cursor.callproc('sp_cadastraLog', (possible_plate, ))
                    data = cursor.fetchall()
                    if len(data) is 0:
                        conn.commit()
                    query = "SELECT carro.modelo, funcionario.nome, funcionario.cargo FROM carro JOIN funcionario ON carro.funcionario = funcionario.id_func WHERE carro.placa = '" + possible_plate + "'"
                    cursor.execute(query)
                    row = cursor.fetchone()
                    if row: 
                        (self.modelo, self.nome, self.cargo) = row
                    time.sleep(3)
                print(self.plate)

    def getFrame(self, frame, firstFrame):

        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if firstFrame is None:
            firstFrame = gray
            return (firstFrame, frame)

        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if cv2.contourArea(c) < 500:
                continue
            else:
                self.motion = True

        firstFrame = gray

        return (firstFrame, frame)
