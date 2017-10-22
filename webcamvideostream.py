# import the necessary packages
from threading import Thread
import cv2
import time

class WebcamVideoStream:



    def __init__(self, src=0, measuring=False):
        # initialize the video camera stream and read the first frame
        # from the stream
        print("init")
        self.stream = cv2.VideoCapture(src)
        
        self.stream.set(3, 480)
        self.stream.set(4, 320)
        self.stream.set(5, 5)
        
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.measuring=measuring 

    def start(self):
        print("start thread")
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        print("read")
        # keep looping infinitely until the thread is stopped
        if self.measuring:
            output_file = open("/home/pi/meas/capture.dat", "w")
            count = 1 
            limit_samples_count = 0
            start_time = time.time()
        while True:
            if self.measuring and limit_samples_count < 1000:
                
                if count == 10:
                    count = 0
                    output_file.write("%s\n" % (time.time() - start_time))
                    start_time = time.time() 
                count = count + 1
                limit_samples_count = limit_samples_count + 1
                if limit_samples_count == 1000:
                    output_file.close()
            
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return


            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
