import csv
import json
import os
import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
######################################################################################
os.environ['HTTP_PROXY'] = 'http://proxy:3128/'
os.environ['HTTPS_PROXY'] = 'http://proxy:3128/'
model = InceptionV3(weights='imagenet', include_top=True)
######################################################################################
filepath = '/data/objectnet/objectnet-1.0/mappings/objectnet_to_imagenet_1k.json'
objectNet_Class_Names = []
imageNet_Class_Names = []
with open(filepath) as fp:
    line = fp.readline()
    cnt = 1
    while line:
        if (':' in line.strip()):
            objectNet_Class_Names.append(line.strip().split(":")[0])
            temp = (line.strip().split(":")[1]).strip()
            temp = re.sub(r"(?i)^[^a-z\d()]*|[^a-z\d()]+$", "", temp)
            imageNet_Class_Names.append(temp)
        line = fp.readline()
        cnt += 1
objectToImageNet_dictionary = dict(zip(objectNet_Class_Names, imageNet_Class_Names))
#############################################################################################
filepath = '/project/cmandal/tmp/cee_project/project-app/FlaskImplementation/imagenet1000_clsidx_to_labels.json'
class_idx = []
class_name = []
with open(filepath) as fp:
    line = fp.readline()
    cnt = 1
    while line:
        class_idx.append(line.strip().split(":")[0])
        temp = (line.strip().split(":")[1]).strip()
        temp = re.sub(r"(?i)^[^a-z\d()]*|[^a-z\d()]+$", "", temp)
        class_name.append(temp)
        line = fp.readline()
        cnt += 1

objectNet_dictionary = dict(zip(class_name, class_idx))
#############################################################################################
filepath = '/project/cmandal/tmp/cee_project/project-app/FlaskImplementation/imagenet1000_clsidx_to_labels.json'
class_idx = []
class_name = []
with open(filepath) as fp:
    line = fp.readline()
    cnt = 1
    while line:
        class_idx.append(line.strip().split(":")[0])
        temp = (line.strip().split(":")[1]).strip()
        temp = re.sub(r"(?i)^[^a-z\d()]*|[^a-z\d()]+$", "", temp)
        class_name.append(temp)
        line = fp.readline()
        cnt += 1
imagetNet_dictionary = dict(zip(class_idx, class_name))
#############################################################################################
def imageNet_idxToClass(class_id):
    if len(list(value for key, value in imagetNet_dictionary.items() if class_id in key.lower())) > 0:
        return (list(value for key, value in imagetNet_dictionary.items() if class_id in key.lower())[0])
    return -1
#############################################################################################
def objectNetClass_to_ImageNet_idx(class_name_search):
    imageNet_class = "NotFound"
    if len(list(value for key, value in objectToImageNet_dictionary.items() if class_name_search in key.lower())) > 0:
        imageNet_class = \
        list(value for key, value in objectToImageNet_dictionary.items() if class_name_search in key.lower())[0]
        orig = imageNet_class
        l = list(imageNet_class)
        l = [e for e in l if e not in ('!', ',', '(', ')', '"', ':')]
        op_str = ''.join(l)
        imageNet_class = "NotFound"
        if(len(op_str.split())>0):
            for i in range(len(op_str.split())):
                if(class_name_search==op_str.split()[i]): imageNet_class = orig
        else:
            if(class_name_search == imageNet_class): imageNet_class = orig

    if len(list(value for key, value in objectNet_dictionary.items() if imageNet_class == key.lower())) > 0:
        return (list(value for key, value in objectNet_dictionary.items() if imageNet_class == key.lower())[0])
    return -1

#############################################################################################
def make_json(csvFilePath, jsonFilePath):
    data = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            key = rows['IDX']
            data[key] = rows
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
#############################################################################################
def main():
    path = r'/data/objectnet/objectnet-1.0/images'
    f = open("../tmp/MisclassifiedImages.csv", "w")
    temp = "IDX,FILENAME,CLASS_ACTUAL_IDX,CLASS_PRED_IDX,CLASS_ACTUAL,CLASS_PRED\r\n"
    f.write(temp)
    f.close()
    i = 0
    for subdir, dirs, files in os.walk(path):
        for filename in files:
            filepath = subdir + os.sep + filename

            objNet_class_label = (subdir + os.sep).split("/")[-2]
            imgNet_class_index_objToimagenet = objectNetClass_to_ImageNet_idx(objNet_class_label)

            img = image.load_img(filepath, target_size=(224, 224))
            img_data = image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            feature = model.predict(img_data)
            predictions = tf.where(feature < 0.5, 0, 1)
            imgNet_class_index_output = predictions.numpy().argmax()

            if (imgNet_class_index_output != int(imgNet_class_index_objToimagenet)):
                filepaths = filepath
                predictions= imgNet_class_index_output
                class_idx = objectNetClass_to_ImageNet_idx(filepaths.split("/")[-2])
                objNet_class_actual = str(filepaths.split("/")[-2])
                if(class_idx == -1):
                    objNet_class_actual = str(filepaths.split("/")[-2]) + " (Not in ImageNet)"
                f = open("../tmp/MisclassifiedImages.csv", 'a')
                temp = str(i + 1) + "," + filepaths + "," + str(class_idx) + "," + \
                       str(predictions) + "," + objNet_class_actual + "," + \
                       imageNet_idxToClass(str(predictions)).split(",")[0] + "\r\n"
                i = i + 1
                f.write(temp)
                f.close()

        print("Completed a class")

#############################################################################################
csvFilePath = r'../tmp/MisclassifiedImages.csv'
jsonFilePath = r'../tmp/output.json'

# Call the make_json function
main()
make_json(csvFilePath, jsonFilePath)
print("End")
############################################################################################