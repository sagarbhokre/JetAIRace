from inputs import get_gamepad
import threading
import time

class JController(threading.Thread):
    def __init__(self):
        self.steering = 0.0
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

            if event.code == 'ABS_RX':
                self.steering = event.state/32768.0;
                print("Steering: %.2f"%(self.steering))
            if event.code == 'ABS_RY':
                self.throttle = event.state/32768.0;
                print("Throttle: %.2f"%(self.throttle))
            if event.code == 'ABS_RZ':
                self.throttle = -1.0*event.state/255.0;
                print("Throttle: %.2f"%(self.throttle))
            if event.code == 'ABS_Z':
                self.throttle = event.state/255.0;
                print("Throttle: %.2f"%(self.throttle))
            if event.code == 'BTN_SOUTH':
                self.engage_motors = True
                print("Engaging motors")
            if event.code == 'BTN_EAST':
                self.engage_motors = False
                print("Disengaging motors")
            if event.code == 'BTN_SELECT':
                self.quit = True
                print("Quit")

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

