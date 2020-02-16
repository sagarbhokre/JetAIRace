import time
import torch
import torchvision
import torchvision.transforms as transforms
#import torch.nn.functional as F
import cv2
import PIL.Image

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

from xy_dataset import XYDataset

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

dataset = datasets[DATASETS[0]]

def preprocess(image):
    device = torch.device('cuda')
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

def live(model, camera):
    global dataset
    while True:
        ret, image = camera.getFrame()
        if ret == False:
            print("Failed to capture image")
            break

        preprocessed = preprocess(image)
        output = model(preprocessed).detach().cpu().numpy().flatten()
        category_index = dataset.categories.index('apex')
        x = output[2 * category_index]
        y = output[2 * category_index + 1]
        
        x = int(image.width * (x / 2.0 + 0.5))
        y = int(image.height * (y / 2.0 + 0.5))
        
        prediction = image.copy()
        #prediction = cv2.flip(prediction, -1)
        prediction = cv2.circle(prediction, (x, y), 8, (255, 0, 0), 3)
        cv2.imshow("Prediction", prediction)

        keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        if keyCode == 27:
            break

def start_live(change):
    if change['new'] == 'live':
        execute_thread = threading.Thread(target=live, args=(state_widget, model, camera, prediction_widget))
        execute_thread.start()


device = torch.device('cuda')
output_dim = 2 * len(dataset.categories)  # x, y coordinate for each category

model_path = '/home/jetson/jetracer/notebooks/road_following_model.pth'

model = torchvision.models.resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, output_dim)

model = model.to(device)

model.load_state_dict(torch.load(model_path))

live(model, camera)
