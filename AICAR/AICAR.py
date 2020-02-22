#!/usr/bin/python3

from parser.util import *
from analyzer.analyze import *
from analyzer.annotate import JLabeler
from live_exec.util import JInfer
from manual_control.car import JCar
from manual_control.controller import JController
from capture_utils.gcapture import JCamera
import time

SPEED_LIMIT=0.6

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
            if controller.override:
                car.control(controller.steering, controller.throttle*0.5)

    elif args.mode == 'Run':
        infer = JInfer(model_path='models/trained_v2.pth')
        camera = JCamera(handle_keys=False, render=False)
        car = JCar()
        controller = JController()
        controller.start()

        speed = 0.3
        enable_prints = False
        curr_time = time.time()
        prev_time = time.time()
        while True:
            ret, img = camera.read()
            x,y = infer.runFrame(img)
            if controller.engage_motors:
                car.control(controller.steering, controller.throttle*0.5)
            else:
                car.control(x*1.2, speed)
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
                print('Processing: %0.2f ms' % ((curr_time-prev_time)*1000))
            prev_time = curr_time
        cleanup(car)
        exit(1)

    elif args.mode == 'Train':
        infer = JInfer(model_path='models/trained_v1.pth')
        #infer.load_modelfile('models/trained_v1.pth')
        infer.train_eval(is_training=True)
        infer.save_model('models/trained_v2.pth')
        exit(1)

    elif args.mode == 'AnalyzeDataset':
        analyze_dataset("./road_following_A/apex")

    elif args.mode == 'LabelVideo':
        lblr = JLabeler()
        if args.input_file == '':
            print("Provide input video file")
            exit(1)
        lblr.label_video(args.input_file)
