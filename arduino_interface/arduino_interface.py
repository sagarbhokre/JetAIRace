import serial
import time

serport = "/dev/ttyACM0"
ser = None

DEBUG = 1

def write_ser(data):
    global ser
    ser.write(bytes(data, 'utf-8'))
    ser.flush()

def read_ser():
    global ser
    serData = ser.readline()
    if len(serData) > 0 and serData[-1] == 10:
        return True, serData.decode("utf-8")

    return False, 'A'

def init_ser():
    global ser
    ser = serial.Serial(serport,115200, timeout=.4)
    ser.flushInput()

def retry_setup_connection():
    global ser
    count = 10
    if ser is not None:
        ser.close()

    while count > 0:
        if setup_connection():
            return True
        count -= 1

    return False

def setup_connection():
    print("Trying to setup connection")
    init_ser()
    write_ser("A\n");
    write_ser("A\n");
    write_ser("A\n");
    write_ser("A\n");

    ret, data = read_ser()
    if(ret == True):
        arduinoRet = data.strip().split(' ')[-1]
    else:
        return False

    if DEBUG: print("Read from %s: --%s--"%(serport, data))

    if arduinoRet == 'A':
        return True
    else:
        return False

def send_actuate(lDir, lSpeed, rDir, rSpeed):
    outStr = "L:%c%d R:%c%d\n"%(lDir, lSpeed, rDir, rSpeed)
    write_ser(outStr)

if __name__ == '__main__':
    count = 0
    direction = 0
    if retry_setup_connection():
        while True:
            count = (count + 1) % 10
            if count == 0:
                direction = (direction + 1) % 2
            lDir = '+' if direction == 1 else '-'
            rDir = '+' if direction == 0 else '-'

            send_actuate(lDir, 9-count, rDir, count)
            if DEBUG: time.sleep(.3)
            ret, line = read_ser()
            if ret == False:
                print("Read failed retrying connection")
                retry_setup_connection()

            if DEBUG: print("Read from %s: %s"%(serport, line.strip()))
    else:
        print("Setup failed")
