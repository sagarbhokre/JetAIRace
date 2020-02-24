import cv2
import time
from jetracer.nvidia_racecar import NvidiaRacecar

class JCar:
    def __init__(self):
        self.throttle_offset = 0.40
        self.steering_offset = 0.0
        self.delta = 0.02
        self.init_car()

    def control(self, s, t):
        self.car.steering = s
        self.car.throttle = t

    def handle_keys(self):
        k = cv2.waitKey(10) & 0xFF
        if(k == 81): # <- Key
            self.steering_offset = max(self.steering_offset-self.delta, -1.0)
            self.car.steering = self.steering_offset
        elif k == 83: #-> key
            self.steering_offset = min(self.steering_offset+self.delta, 1.0)
            self.car.steering = self.steering_offset
        elif k == 82: # ^ key
            self.car.throttle = self.throttle_offset
            time.sleep(0.2)
        elif k == 84: # v key
            #throttle_offset -= 0.02
            self.throttle_offset -= 0.0
        elif k == ord('w'):
            self.throttle_offset = min(self.throttle_offset+self.delta, 1.0)
        elif k == ord('s'):
            self.throttle_offset = max(self.throttle_offset-self.delta, -1.0)
    
        if(k == ord('q') or k == 27):
            self.car.steering = 0.0
            self.car.throttle = 0.0
            return False
    
        if(k != 255):
            self.car.throttle = 0.0
            #print("S: %.2f T: %.2f"%(self.steering_offset, self.throttle_offset))
    
        return True
    
    def init_car(self):
        self.car = NvidiaRacecar()
    
        self.car.throttle_gain = 0.5
        self.car.steering_offset = 0.0
        self.car.steering_gain = -1.0
        print("SG: %.2f SO: %.2f TG: %.2f"%(self.car.steering_gain, self.car.steering_offset, self.car.throttle_gain))

def init_img():
    img = cv2.imread('image.jpeg')
    cv2.imshow('JetRacer Manual Control',img)

if __name__ == '__main__':
    car_int = JCar()
    car_int.init_car()
    init_img()
    ret = True
    while ret:
        ret = car_int.handle_keys()
