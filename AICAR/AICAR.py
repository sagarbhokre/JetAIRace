#!/usr/bin/python3

from parser.util import *
from analyzer.analyze import *
from analyzer.annotate import JLabeler
from live_exec.util import JInfer
from manual_control.car import JCar
from manual_control.controller import JController
from capture_utils.gcapture import JCamera

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
        infer = JInfer()
        camera = JCamera(handle_keys=False, render=False)
        car = JCar()
        speed = 0.3
        infer.load_modelfile('models/trained_v1.pth')
        while True:
            ret, img = camera.read()
            x,y = infer.runFrame(img)
            car.control(x*1.2, speed)
            infer.render(img, x, y)
            #infer.live(camera)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q') or k == 27:
                break
            elif k == ord('w'):
                speed += 0.02
                print("Speed: %.2f"%(speed))
            elif k == ord('s'):
                speed -= 0.02
                print("Speed: %.2f"%(speed))

            speed = speed if speed < 1.0 else 1.0
            speed = speed if speed > -1.0 else -1.0
        exit(1)

    elif args.mode == 'Train':
        infer = JInfer()
        infer.load_modelfile('models/trained_v1.pth')
        infer.train_eval(is_training=True)
        infer.save_model('models/trained_v1.pth')
        exit(1)

    elif args.mode == 'AnalyzeDataset':
        analyze_dataset("./road_following_A/apex")

    elif args.mode == 'LabelVideo':
        lblr = JLabeler()
        if args.input_file == '':
            print("Provide input video file")
            exit(1)
        lblr.label_video(args.input_file)
