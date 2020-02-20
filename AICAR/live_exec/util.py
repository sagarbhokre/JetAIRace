import time
import torch
import torchvision
import torchvision.transforms as transforms
#import torch.nn.functional as F
import cv2
import PIL.Image


class JInfer:
    def __init__(self):
        from .xy_dataset import XYDataset
        self.device = torch.device('cuda')
        self.mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
        self.std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
        self.model_path = '/home/jetson/jetracer/notebooks/road_following_model.pth'
        self.BATCH_SIZE = 8

        TASK = 'road_following'

        CATEGORIES = ['apex']

        DATASETS = ['A', 'B']

        TRANSFORMS = transforms.Compose([
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        datasets = {}
        for name in DATASETS:
            datasets[name] = XYDataset(TASK + '_' + name, CATEGORIES, TRANSFORMS, random_hflip=True)

        self.dataset = datasets[DATASETS[0]]

        self.load_model()
        self.init_trainer()

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self.device)
        image.sub_(self.mean[:, None, None]).div_(self.std[:, None, None])
        return image[None, ...]

    def live(self, camera):
        while True:
            ret, image = camera.read()
            if ret == False:
                print("Failed to capture image")
                break

            preprocessed = self.preprocess(image)
            output = self.model(preprocessed).detach().cpu().numpy().flatten()
            category_index = self.dataset.categories.index('apex')
            x = output[2 * category_index]
            y = output[2 * category_index + 1]

            x = int(camera.width * (x / 2.0 + 0.5))
            y = int(camera.height * (y / 2.0 + 0.5))

            prediction = image.copy()
            hw = camera.width/2
            steering_angle = (x - hw) / hw

            prediction = cv2.circle(prediction, (x, y), 8, (255, 0, 0), 3)
            prediction = cv2.putText(prediction, 'Steering: %.3f Angle: %.2f'%(x, steering_angle),
                                     (10,10),
                                     cv2.FONT_HERSHEY_SIMPLEX, .3, (0,255,0), 1, cv2.LINE_AA)
            cv2.imshow("Prediction", prediction)

            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break


    def runFrame(self, image):
        preprocessed = self.preprocess(image)
        output = self.model(preprocessed).detach().cpu().numpy().flatten()
        category_index = self.dataset.categories.index('apex')
        x = float(output[2 * category_index])
        y = float(output[2 * category_index + 1])

        return x,y

    def render(self, image, x, y):
        x = int(image.shape[1] * (x / 2.0 + 0.5))
        y = int(image.shape[0] * (y / 2.0 + 0.5))
        hw = image.shape[1]/2
        steering_angle = (x - hw) / hw

        prediction = cv2.circle(image, (x, y), 8, (255, 0, 0), 3)
        prediction = cv2.putText(prediction, 'Steering: %.3f Angle: %.2f'%(x, steering_angle),
                                 (10,10),
                                 cv2.FONT_HERSHEY_SIMPLEX, .3, (0,255,0), 1, cv2.LINE_AA)
        cv2.imshow("Prediction", prediction)

    def load_model(self):
        output_dim = 2 * len(self.dataset.categories)  # x, y coordinate for each category

        self.model = torchvision.models.resnet18(pretrained=True)
        self.model.fc = torch.nn.Linear(512, output_dim)
        self.model = self.model.to(self.device)

        print("Loading model: %s"%(self.model_path))
        self.model.load_state_dict(torch.load(self.model_path))

    def init_trainer(self):
        self.optimizer = torch.optim.Adam(self.model.parameters())
        # self.optimizer = torch.optim.SGD(self.model.parameters(), lr=1e-3, momentum=0.9)

        self.epochs = 10
        self.loss_val = -1

    def train_eval(self, is_training):
        if True:
            #try:
            train_loader = torch.utils.data.DataLoader(
                self.dataset,
                batch_size=self.BATCH_SIZE,
                shuffle=True
            )

            time.sleep(1)

            if is_training:
                self.model = self.model.train()
            else:
                self.model = self.model.eval()

            epoch = 0
            while self.epochs > epoch:
                i = 0
                sum_loss = 0.0
                error_count = 0.0
                for images, category_idx, xy in iter(train_loader):
                    # send data to device
                    images = images.to(self.device)
                    xy = xy.to(self.device)

                    if is_training:
                        # zero gradients of parameters
                        self.optimizer.zero_grad()

                    # execute model to get outputs
                    outputs = self.model(images)

                    # compute MSE loss over x, y coordinates for associated categories
                    loss = 0.0
                    for batch_idx, cat_idx in enumerate(list(category_idx.flatten())):
                        loss += torch.mean((outputs[batch_idx][2 * cat_idx:2 * cat_idx+2] - xy[batch_idx])**2)
                    loss /= len(category_idx)

                    if is_training:
                        # run backpropogation to accumulate gradients
                        loss.backward()

                        # step optimizer to adjust parameters
                        self.optimizer.step()

                    # increment progress
                    count = len(category_idx.flatten())
                    i += count
                    sum_loss += float(loss)
                    progress_val = i / len(self.dataset)
                    loss_val = sum_loss / i
                    print("Epoch: %.2f/%d avg_loss:%.6f inst_loss: %.6f"%(epoch + progress_val, self.epochs, loss_val, float(loss)))
                epoch += 1

                if not is_training:
                    break
        #except e:
        #    pass
        self.model = self.model.eval()

    def load_modelfile(self, input_path):
        print("Loading model: %s"%(input_path))
        self.model.load_state_dict(torch.load(input_path))

    def save_model(self, output_path):
        print("Saving model: %s"%(output_path))
        torch.save(self.model.state_dict(), output_path)

if __name__ == '__main__':
    infer = JInfer()
    #infer.live(camera)
    infer.train_eval(is_training=True)
    infer.train_eval(is_training=False)
