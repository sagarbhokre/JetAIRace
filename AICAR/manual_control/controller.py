from inputs import get_gamepad
import threading
import time

DEBUG = 0
class JController(threading.Thread):
    def __init__(self):
        self.steering = 0.0
        self.speed = 0.0
        self.throttle = 0.0
        self.engage_motors = False
        self.quit = False
        self.override = False
        threading.Thread.__init__(self)

    def run(self):
        while self.quit == False:
            self.handle_gamepad_events()

    def handle_gamepad_events(self):
        events = get_gamepad()
        for event in events:
            #print("Type: ", event.ev_type, " Code: ",  event.code, " State: ", event.state)

            if event.code == 'ABS_Y': # Left flat direction control up-down
                self.speed = -1.0*event.state/32768.0;
                if DEBUG: print("[Controller] Speed: %.2f"%(self.speed))
            if event.code == 'ABS_RX': # Right joystick left-right
                self.steering = event.state/32768.0;
                if DEBUG: print("[Controller] Steering: %.2f"%(self.steering))
            #if event.code == 'ABS_RY': # Right joystick up-down
            #    self.throttle = event.state/32768.0;
            #    print("[Controller] Throttle: %.2f"%(self.throttle))
            if event.code == 'ABS_RZ': # RT
                self.throttle = -1.0*event.state/255.0;
                if DEBUG: print("[Controller] Throttle: %.2f"%(self.throttle))
            if event.code == 'ABS_Z': # LT
                self.throttle = event.state/255.0;
                if DEBUG: print("[Controller] Throttle: %.2f"%(self.throttle))
            if event.code == 'BTN_SOUTH': # Green button 'A'
                self.engage_motors = True
                print("[Controller] Engaging motors")
            if event.code == 'BTN_EAST': # Red button 'B'
                self.engage_motors = False
                print("[Controller] Disengaging motors")
            if event.code == 'BTN_SELECT': # Back button
                self.quit = True
                print("[Controller] Quit")

        if abs(self.steering) > 0.001 or self.throttle > 0.01:
            self.override = True

        return True

    def control_car(self, car):
        if self.engage_motors:
            car.steering = self.steering
            car.throttle = self.throttle

if __name__ == '__main__':
    controller = JController()
    controller.start()
    while not controller.quit:
        time.sleep(1) #controller.handle_gamepad_events()
        break

