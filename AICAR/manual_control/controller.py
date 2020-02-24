from inputs import get_gamepad
import threading
import time
import ctypes

def cap(self, x):
    x = x if x < 1.0 else 1.0
    x = x if x > -1.0 else -1.0
    return x

DEBUG = 0
class JController(threading.Thread):
    def __init__(self, enable_prints=True):
        self.steering = 0.0
        self.steering_discrete = 0.0
        self.speed = 0.0
        self.throttle = 0.0
        self.manual_mode = False
        self.run_mode = False
        self.create_dataset_mode = False
        self.start_live_train = False
        self.quit = False
        self.killFlag = False
        self.override = False
        self.pauseFlag = False
        self.saveModelFlag = False
        self.enable_prints = enable_prints
        threading.Thread.__init__(self)

    def pause(self):
        print("Pause controller")
        self.pauseFlag = True

    def resume(self):
        print("Resume controller")
        self.pauseFlag = False

    def restart(self):
        threading.Thread.__init__(self)
        self.quit = False
        self.start()

    def kill(self):
        self.killFlag = True

    def run(self):
        try:
            while self.killFlag == False:
                if self.pauseFlag == True:
                    print("Controller thread sleep")
                    time.sleep(1)
                    continue
                self.handle_gamepad_events()
        finally:
            print("Controller thread ended----------------")

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def handle_gamepad_events(self):
        events = get_gamepad()
        for event in events:
            #print("Type: ", event.ev_type, " Code: ",  event.code, " State: ", event.state)

            if event.code == 'ABS_Y' and event.state != -129: # Left flat direction control up-down
                self.speed = -1.0*event.state/32768.0;
                if DEBUG: print("[Controller] Speed: %.2f"%(self.speed))
            if event.code == 'ABS_X' and event.state != 128: # Left flat direction control left-right
                self.steering_discrete = event.state/32768.0;
                if DEBUG: print("[Controller] Steering_discrete: %.2f"%(self.steering_discrete))
            if event.code == 'ABS_RX': # Right joystick left-right
                self.steering = event.state/32768.0;
                if DEBUG: print("[Controller] Steering: %.2f"%(self.steering))
            #if event.code == 'ABS_RY': # Right joystick up-down
            #    self.throttle = event.state/32768.0;
            #    print("[Controller] Throttle: %.1f"%(self.throttle))
            if event.code == 'ABS_RZ': # RT
                self.throttle = -1.0*event.state/255.0;
                if DEBUG: print("[Controller] Throttle: %.2f"%(self.throttle))
            if event.code == 'ABS_Z': # LT
                self.throttle = event.state/255.0;
                if DEBUG: print("[Controller] Throttle: %.2f"%(self.throttle))
            if event.code == 'BTN_SOUTH': # Green button 'A'
                self.manual_mode = False
                print("[Controller] Autonomous mode")
            if event.code == 'BTN_EAST': # Red button 'B'
                self.manual_mode = True
                print("[Controller] Manual mode")
            if event.code == 'BTN_NORTH': # Red button 'Y'
                self.run_mode = True
                print("[Controller] Run AI")
            if event.code == 'BTN_WEST': # Red button 'Y'
                self.create_dataset_mode = True
                print("[Controller] Create Dataset")
            if event.code == 'BTN_TL': # LB button
                self.start_live_train = True
                print("[Controller] Start live train btn")
            if event.code == 'BTN_TR': # RB button
                self.saveModelFlag = True
                print("[Controller] Save model trigger")
            if event.code == 'BTN_SELECT': # Back button
                self.quit = True
                print("[Controller] Quit")

        if abs(self.steering) > 0.01 or abs(self.throttle) > 0.01:
            self.override = True

        return True

    def control_car(self, car):
        if self.manual_mode:
            car.steering = self.steering
            car.throttle = self.throttle

if __name__ == '__main__':
    controller = JController()
    controller.start()
    while not controller.quit:
        time.sleep(1) #controller.handle_gamepad_events()
        break

