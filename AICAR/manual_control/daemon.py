from controller import JController
import psutil
import time


def write_pid_to_file():
    pid = os.getpid()
    pidfile = open(os.path.expanduser("~/.lockfile.vestibular.lock"), "w")
    pidfile.write("%d"%(pid))
    pidfile.close()

def findProcessIdByName(scriptName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''

    listOfProcessObjects = []
    processName = 'python'

    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               if len(proc.cmdline())>1 and scriptName in proc.cmdline()[1] and proc.pid !=os.getpid():
                   print("'{}' Process is running".format(scriptName))
                   listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           print("Pass")
           pass

    return listOfProcessObjects;

import os
import sys
def check_process_running():
    if os.access(os.path.expanduser("~/.lockfile.vestibular.lock"), os.F_OK):
        #if the lockfile is already there then check the PID number
        #in the lock file
        pidfile = open(os.path.expanduser("~/.lockfile.vestibular.lock"), "r")
        pidfile.seek(0)
        old_pid = pidfile.readline()
        # Now we check the PID from lock file matches to the current
        # process PID
        if os.path.exists("/proc/%s" % old_pid):
            print("You already have an instance of the program running")
            print("It is running as process %s," % old_pid)
        else:
            print("File is there but the program is not running")
            print("Removing lock file for the: %s as it can be there because of the program last time it was run" % old_pid)
            os.remove(os.path.expanduser("~/.lockfile.vestibular.lock"))
    return False

if __name__ == '__main__':
    print("Starting Daemon")
    write_pid_to_file()
    scriptName = "AICAR.py"

    controller = JController()
    controller.start()

    controller_paused = True
    while True:
        listOfProcessIds = findProcessIdByName(scriptName)
    
        if len(listOfProcessIds) > 0:
            if controller_paused == False:
                controller_paused = True
                print("Disable daemon")
        else :
            if controller_paused == True:
                controller_paused = False
                print('Controlling from daemon')

        if controller_paused == False:
            if controller.run_mode == True:
                controller.run_mode = False
                os.system('cd /home/jetson/JetAIRace/AICAR && python3 AICAR.py Run')
                print("Start AI algo on car")
            if controller.create_dataset_mode == True:
                controller.create_dataset_mode = False
                os.system('cd /home/jetson/JetAIRace/AICAR && python3 AICAR.py CreateDataset')
                print("Create dataset on car")
            if controller.start_live_train == True:
                controller.start_live_train = False
                os.system('cd /home/jetson/JetAIRace/AICAR && python3 AICAR.py LiveTrain')
                print("Live training on car")
        time.sleep(1)

    controller.kill()
