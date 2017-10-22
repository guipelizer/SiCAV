from threading import Thread
from motion import getFrame

class Video_Feed(Thread):

    def __init__(self, camera):
        Thread.__init__(self)
        self.camera = camera

    def run(self):
        firstFrame = None
        while True:
            firstFrame, img = getFrame(self.camera, firstFrame)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


