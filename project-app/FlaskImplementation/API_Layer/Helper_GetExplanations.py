import datetime
import os
import os.path
from MainCode_Explanations_TorchRay import torchray_Gradcam
import torch
from tensorflow.keras.applications import InceptionV3
# Default device
device = "cuda:0" if torch.cuda.is_available() else "cpu"
os.environ['HTTP_PROXY'] = 'http://proxy:3128/'
os.environ['HTTPS_PROXY'] = 'http://proxy:3128/'
model = torch.hub.load('pytorch/vision:v0.6.0', 'inception_v3', pretrained=True).to(device)


def call_explanations(inp_path, classID):
    L1 = 'Conv2d_2a_3x3'
    L2 = 'Mixed_6b'
    L3 = 'Mixed_7c'
    Current_Date = datetime.datetime.today().strftime('%d-%b-%Y')

    out_path_GradCam_L1 = ('../tmp/out_' + 'explain_GradCam_L1_' + str(Current_Date) + '.jpg')
    out_path_GradCam_L2 = ('../tmp/out_' + 'explain_GradCam_L2_' + str(Current_Date) + '.jpg')
    out_path_GradCam_L3 = ('../tmp/out_' + 'explain_GradCam_L3_' + str(Current_Date) + '.jpg')
    try:
        os.remove(out_path_GradCam_L1)
        os.remove(out_path_GradCam_L2)
        os.remove(out_path_GradCam_L3)
    except:
        print("File does not exist - New File created")
    torchray_Gradcam(model, classID, L1, inp_path, out_path_GradCam_L1)
    torchray_Gradcam(model, classID, L2, inp_path, out_path_GradCam_L2)
    torchray_Gradcam(model, classID, L3, inp_path, out_path_GradCam_L3)

    if not os.path.isfile(out_path_GradCam_L1):
        torchray_Gradcam(model, classID, L1, inp_path, out_path_GradCam_L1)

    if not os.path.isfile(out_path_GradCam_L2):
        torchray_Gradcam(model, classID, L2, inp_path, out_path_GradCam_L2)

    if not os.path.isfile(out_path_GradCam_L3):
        torchray_Gradcam(model, classID, L3, inp_path, out_path_GradCam_L3)

    return out_path_GradCam_L1, out_path_GradCam_L2, out_path_GradCam_L3


#params_to_update = model.parameters()
#print("Params to learn:")
#for name,param in model.named_parameters():
#    if param.requires_grad == True:
#        print("\t",name)
#inp_path = "/data/objectnet/objectnet-1.0/images/mug/a8cc852f22d9493.png"
#print(call_explanations(inp_path,504))
