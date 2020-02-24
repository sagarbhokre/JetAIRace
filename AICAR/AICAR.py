#!/usr/bin/python3

from parser.util import *
from analyzer.analyze import *
from analyzer.annotate import JLabeler
from live_exec.util import JInfer
from manual_control.car import JCar
from manual_control.controller import JController
from capture_utils.gcapture import JCamera
import time

ENABLE_PROFILING_PRINTS = False
SPEED_LIMIT=0.6
INFER_MODEL_PATH='models/trained_v3.pth'
LIVEINFER_MODEL_PATH='models/livetrained_v1.pth'

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
        camera = JCamera(handle_keys=False, render=args.render)
        car = JCar()
        controller = JController()
        controller.start()

        speed = 0.3
        enable_prints = False
        curr_time = time.time()
        prev_time = time.time()
        while True:
            ret, img = camera.read()
            x,y = infer.runFrame(img, renderFlag=args.render)
            if controller.manual_mode:
                car.control(controller.steering, controller.throttle*0.5)
            else:
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
        camera = JCamera(handle_keys=False, render=args.render)
        car = JCar()
        controller = JController(enable_prints=False)
        controller.start()

        speed = 0.3
        enable_prints = False
        curr_time = time.time()
        prev_time = time.time()
        while True:
            if controller.manual_mode == True:
                car.control(controller.steering, controller.throttle)
            else:
                ret, img = camera.read()
                x,y = infer.runFrame(img, renderFlag=args.render)
                if controller.override:
                    controller.override = False
                    x1 = x + controller.steering
                    x1 = x1 if x1 < 1.0 else 1.0
                    x1 = x1 if x1 > -1.0 else -1.0
                    car.control(x1, speed + controller.throttle*0.3)
                    print("S: %.3f T: %.3f"%(x1, speed))
                    infer.trainFrame(img, x1, controller.throttle)
                else:
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
            if controller.saveModelFlag:
                controller.saveModelFlag = False
                infer.save_model(LIVEINFER_MODEL_PATH)

            speed = speed if speed < SPEED_LIMIT else SPEED_LIMIT
            speed = speed if speed > -SPEED_LIMIT else -SPEED_LIMIT

            if ENABLE_PROFILING_PRINTS:
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
