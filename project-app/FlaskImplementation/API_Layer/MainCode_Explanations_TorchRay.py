import torch
import torchvision.transforms as transforms
from PIL import Image
from torchray.attribution.grad_cam import grad_cam
from torchray.utils import imsc
from torchvision.utils import save_image

# Default device
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print("Using Device:", device)

data_transform = transforms.Compose([
    #transforms.Resize(256),
    #transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Grad cam
def torchray_Gradcam(model, category_id, layer, inp_path, out_path):
    img = Image.open(inp_path).convert('RGB')
    #img = Image.open(inp_path)
    try:
        inp_img = torch.unsqueeze(data_transform(img).to(device), 0)
        saliency = grad_cam(model, inp_img, category_id, saliency_layer=layer)
        img1, _ = imsc(saliency[0], interpolation='none')
        save_image(img1, out_path)
    except:
        print("Issue with file:",inp_path, "/n for class:", category_id )

