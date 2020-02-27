#!/usr/bin/python3

from util.utils import *
from parser.util import *
from analyzer.analyze import *
from analyzer.annotate import JLabeler
from live_exec.util import JInfer
from manual_control.car import JCar
from manual_control.touch_controller import JTouchSensor
from manual_control.controller import JController
from capture_utils.gcapture import JCamera
import time

ENABLE_PROFILING_PRINTS = False
SPEED_LIMIT=0.6
INFER_MODEL_PATH='models/trained_v3.pth'
LIVEINFER_MODEL_PATH='models/livetrained_v1.pth'
SMOOTHEN = False

def cleanup(car):
    car.control(0.0, 0.0)

if __name__ == '__main__':
    args = parse_args()
    if args.mode == 'CreateDataset':
        cam = JCamera(handle_keys=False)
        car = JCar()
        controller = JController()
        controller.start()

        ret = True
        while ret and not controller.quit:
            ret, frame = cam.getFrame()
            ret = car.handle_keys()
            if True or controller.override:
                capped_throttle = controller.throttle * 0.5 if controller.throttle < SPEED_LIMIT else SPEED_LIMIT * 0.5
                car.control(controller.steering, capped_throttle)
        controller.kill()

    elif args.mode == 'Run':
        infer = JInfer(model_path=INFER_MODEL_PATH)
        print("Model loaded. Starting camera")
        camera = JCamera(handle_keys=False, render=args.render)
        print("Camera started. Starting car")
        car = JCar()
        print("Car started. Starting controller")
        controller = JController()
        controller.start()

        speed = 0.3
        enable_prints = False
        curr_time = time.time()
        prev_time = time.time()
        #prev_x = 0.0
        while True:
            ret, img = camera.read()
            x,y = infer.runFrame(img, renderFlag=args.render)
            if controller.manual_mode:
                car.control(controller.steering, controller.throttle*0.5)
            else:
                if SMOOTHEN:
                    x = cap(x)
                    x = 1.0*x*x if x > 0.0 else -1.0*x*x 
                    #x = (x + prev_x) / 2
                    #prev_x = x
                car.control(x, speed)
            #infer.render(img, x, y)
            if enable_prints:
                print('Steering: %0.2f  Throttle: %0.2f' % (x, y))
            #infer.live(camera)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q') or k == 27 or controller.quit:
                break
            elif k == ord('d'):
                enable_prints = True
            elif k == ord('w'):
                speed += 0.02
                print("Speed: %.2f"%(speed))
            elif k == ord('s'):
                speed -= 0.02
                print("Speed: %.2f"%(speed))

            if abs(controller.speed) >= 0.0001:
                speed += controller.speed * 0.02
                controller.speed = 0.0
                print("Speed: %.2f"%(speed))

            speed = speed if speed < SPEED_LIMIT else SPEED_LIMIT
            speed = speed if speed > -SPEED_LIMIT else -SPEED_LIMIT

            curr_time = time.time()
            if (curr_time - prev_time) > 0.025:
                print('Processing: %0.2f ms S: %.2f' % ((curr_time-prev_time)*1000, x))
            prev_time = curr_time
        print("Stopping car")
        cleanup(car)
        print("Stopping camera")
        camera.stop()
        print("Killing controller")
        controller.raise_exception()
        controller.kill()
        print("About to exit")
        os.system(r'kill -9 `pgrep -f "python3 AICAR.py"`')
        print("After kill")
        exit(1)

    elif args.mode == 'Train':
        infer = JInfer(model_path='models/trained_v2.pth')
        #infer.load_modelfile('models/trained_v1.pth')
        infer.train_eval(is_training=True)
        infer.save_model('models/trained_v3.pth')
        exit(1)

    elif args.mode == 'AnalyzeDataset':
        analyze_dataset(args.dataset_location)

    elif args.mode == 'LabelVideo':
        lblr = JLabeler()
        if args.input_file == '':
            print("Provide input video file")
            exit(1)
        lblr.label_video(args.input_file)
    elif args.mode == 'LiveTrain':
        infer = JInfer(model_path=LIVEINFER_MODEL_PATH)
        print("Model loaded. Starting camera")
        camera = JCamera(handle_keys=False, render=args.render)
        print("Camera started. Starting car")
        car = JCar()
        print("Car started. Starting controller")
        controller = JController(enable_prints=False)
        controller.start()
        touchSensor = JTouchSensor(enable_prints=False)

        speed = 0.3
        kb_angle = 0.0
        c_angle = 0.0
        enable_prints = False
        curr_time = time.time()
        prev_time = time.time()
        xm = 0.0
        ym = 0.0
        discrete_control = False
        while True:
            if controller.manual_mode == True:
                if controller.quit == True:
                    break
                car.control(controller.steering, controller.throttle)
                #car.control(touchSensor.xc, touchSensor.yc * 0.4)
            else:
                ret, img = camera.read()
                x,y = infer.runFrame(img, renderFlag=args.render)
                if False and controller.override:
                    controller.override = False
                    x1 = x + controller.steering
                    x1 = x1 if x1 < 1.0 else 1.0
                    x1 = x1 if x1 > -1.0 else -1.0
                    car.control(x1, speed + controller.throttle*0.3)
                    print("S: %.3f T: %.3f"%(x1, speed))
                    infer.trainFrame(img, x1, controller.throttle)
                if True:
                    xm = cap(x + kb_angle + c_angle)
                    ym = speed #+ touchSensor.yc * 0.2
                    if abs(controller.steering_discrete) > 0.0001:
                        c_angle += (controller.steering_discrete * 0.23)
                        controller.steering_discrete = 0.0
                        #x2, y2 = camera.unity_to_image(xm, ym)
                        #camera.save_entry(x2, y2)

                    xs, ys = camera.unity_to_image(xm, ym)
                    camera.save_entry(xs, ys)

                    #if SMOOTHEN:
                    #    xm = cap(xm)
                    #    xm = 1.0*xm*xm if x > 0.0 else -1.0*xm*xm 

                    if discrete_control:
                        car.control(xm, 0)
                    else:
                        car.control(xm, ym)

                    while abs(x - xm) >= 0.23:
                        print("x: %.3f xm: %.3f"%(x, xm))
                        car.control(xm, 0)
                        infer.trainFrame(img, xm, ym)
                        c_angle = 0.0
                        x,y = infer.runFrame(img, renderFlag=args.render)

                    car.control(xm, ym)
                    #print("S: %.3f T: %.3f"%(x1, y1))
                else:
                    car.control(x, speed)
            #infer.render(img, x, y)
            if enable_prints:
                print('Steering: %0.2f  Throttle: %0.2f' % (x, y))
            #infer.live(camera)
            #kb_angle = 0.0
            k = cv2.waitKey(50) & 0xFF
            if k == ord('q') or k == 27 or controller.quit:
                break
            elif k == ord('v'):
                enable_prints = True
            elif k == ord('w'):# or k == 82:
                speed += 0.02
                print("Speed: %.2f"%(speed))
            elif k == ord('s'):
                speed -= 0.02
                print("Speed: %.2f"%(speed))
            elif k == ord('d') or k == 83:
                kb_angle = cap(kb_angle + 0.1)
                print("S: T+Kb: %.2f + %.2f = %.2f"%(touchSensor.xc, kb_angle, touchSensor.xc + kb_angle) )
            elif k == ord('a') or k == 81:
                kb_angle = cap(kb_angle - 0.1)
                print("S: T+Kb: %.2f + %.2f = %.2f"%(touchSensor.xc, kb_angle, touchSensor.xc + kb_angle) )
            elif k == 82:
                car.control(xm, speed)
                time.sleep(0.2)
                car.control(xm, 0)
            elif k == ord('z'):
                discrete_control = not discrete_control
                print("Discrete control: ", discrete_control)
            elif k == ord('c'):
                x2, y2 = camera.unity_to_image(xm, ym)
                camera.save_entry(x2, y2)

            if abs(controller.speed) >= 0.0001:
                speed += controller.speed * 0.01
                controller.speed = 0.0
                print("Speed: %.2f"%(speed))
            if controller.saveModelFlag:
                controller.saveModelFlag = False
                infer.save_model('models/livetraining_v2.pth')

            speed = speed if speed < SPEED_LIMIT else SPEED_LIMIT
            speed = speed if speed > -SPEED_LIMIT else -SPEED_LIMIT

            if ENABLE_PROFILING_PRINTS:
                curr_time = time.time()
                if (curr_time - prev_time) > 0.025:
                    print('Processing: %0.2f ms S: %.2f' % ((curr_time-prev_time)*1000, x))
                prev_time = curr_time
        infer.save_model('models/liveTraining_inter.pth')
        print("Stopping car")
        cleanup(car)
        print("Stopping camera")
        camera.stop()
        print("Killing controller")
        controller.raise_exception()
        controller.kill()
        print("About to exit")
        os.system(r'kill -9 `pgrep -f "python3 AICAR.py"`')
        print("After kill")
        exit(1)
    elif args.mode == 'LiveRec':
        camera = JCamera(handle_keys=False, render=args.render)
        car = JCar()
        controller = JController(enable_prints=False)
        controller.start()
        x = 0
        y = 0
        while True and not controller.quit:
            if abs(controller.steering_discrete) > 0.0001:
                x = cap(x + controller.steering_discrete * 0.33)
                controller.steering_discrete = 0.0
            if abs(controller.speed) > 0.0001:
                y = cap(y + controller.speed*0.02)
                controller.speed = 0.0

            ret, img = camera.read()
            x2, y2 = camera.unity_to_image(x, y)
            camera.save_entry(x2, y2)
            car.control(x,y)
            time.sleep(0.1)
        controller.raise_exception()
        controller.kill()
        camera.stop()
