from openalpr import Alpr
import time
import re

class PlateID():

    def __init__(self):
        self.alpr = Alpr("br", "/usr/share/openalpr/config/openalpr.defaults.conf", "/usr/share/openalpr/runtime_data")

        if not self.alpr.is_loaded():
            print("Error loading OpenALPR")
            sys.exit(1)

        self.alpr.set_top_n(20)
        self.alpr.set_default_region("br")

    def getPlate(self, arq='/home/pi/imgteste.jpg'):
        results = self.alpr.recognize_file(arq) 
        plate = None
        pat = re.compile('[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9]') 
        for plates in results['results']:
            for candidate in plates['candidates']:
                if pat.match(candidate['plate']):
                    plate = candidate['plate']
                    break;
        return plate






