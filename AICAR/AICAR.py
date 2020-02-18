#!/usr/bin/python3

from parser.util import *
from analyzer.analyze import *
from analyzer.annotate import JLabeler
from live_exec.util import JInfer
from manual_control.car import JCar
from capture_utils.gcapture import JCamera

if __name__ == '__main__':
    args = parse_args()
    if args.mode == 'CreateDataset':
        cam = JCamera(handle_keys=False)
        car = JCar()

        ret = True
        while ret:
            ret, frame = cam.getFrame()
            ret = car.handle_keys()

    elif args.mode == 'Run':
        infer = JInfer()
        camera = JCamera(handle_keys=False)
        infer.load_modelfile('models/trained_v1.pth')
        infer.live(camera)
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
