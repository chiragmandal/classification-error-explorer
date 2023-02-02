import base64
import json
import math
import flask
from PIL import Image
from flask import Flask, jsonify, request, send_file
from flask_cors import cross_origin
from Helper_GetExplanations import call_explanations
from Helper_GetSimilarImages import get_similar_images_faiss, get_similar_images_annoy

app = Flask(__name__)
#################################################################################################
# GET PLACEHOLDER IMAGE- Operational
@app.route('/get_placeholder', methods=['GET'])
def get_placeholder_image():
    filename = "../tmp/temp_image.jpeg"
    img_data = rescaleImage(filename)
    data_set = {"IMG": {"IDX": '0',
                        "CLASS_ACTUAL": 'True Class',
                        "CLASS_PRED": 'Assigned Class',
                        "IMG_DATA": img_data.decode('utf-8')}}
    response = jsonify(data_set)
    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response

#################################################################################################
# GET MISCLASSIFIED IMAGES LIST- Operational
@app.route('/get_misclassified_images')
@cross_origin(origin='localhost')
def get_misclassified_images():
    jsonfile = open('../tmp/output.json', 'r')
    data = json.loads(jsonfile.read())

    return data


##################################################################################################
# GET MISCLASSIFIED IMAGES in batches  - Operational
@app.route('/get_misclassified_images_batches', methods=['GET'])
# @cross_origin(origin='localhost')
def get_misclassified_images_batches():
    jsonfile = open('../tmp/output.json', 'r')
    json_data = json.loads(jsonfile.read())
    batch_no = int(request.args['batchNo'])
    batch_length = 10
    start = batch_no * batch_length - batch_length + 1
    img_list = []
    for i in range(start, start+batch_length):
        if (i > len(json_data)):
            break
        filename = json_data[str(i)]['FILENAME']
        IDX = json_data[str(i)]['IDX']
        CLASS_ACTUAL_IDX = json_data[str(i)]['CLASS_ACTUAL_IDX']
        CLASS_PRED_IDX = json_data[str(i)]['CLASS_PRED_IDX']
        CLASS_ACTUAL = json_data[str(i)]['CLASS_ACTUAL']
        CLASS_PRED = json_data[str(i)]['CLASS_PRED']
        img_data = rescaleImage(filename)
        data_set = {"IMG": {"IDX": IDX,
                            "CLASS_ACTUAL_IDX": CLASS_ACTUAL_IDX,
                            "CLASS_PRED_IDX": CLASS_PRED_IDX,
                            "CLASS_ACTUAL": CLASS_ACTUAL,
                            "CLASS_PRED": CLASS_PRED,
                            "FILENAME": filename,
                            "IMG_DATA": img_data.decode('utf-8')}}
        img_list.append(data_set)

    response = jsonify(img_list)
    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


##################################################################################################
# GET MISCLASSIFIED IMAGE BY ID - Calling part by Budha
@app.route('/get_misclassified_image_byID', methods=['GET'])
# @cross_origin(origin='localhost')
def get_misclassified_image_byID():
    fileID = int(request.args['fileID'])
    jsonfile = open('../tmp/output.json', 'r')
    json_data = json.loads(jsonfile.read())

    filename = json_data[str(fileID)]['FILENAME']
    data = rescaleImage(filename)
    response = jsonify(data.decode('utf-8'))
    response.headers.add("Access-Control-Allow-Origin", "*")

    return data


###################################################################################################
# GET SIMILAR IMAGES - STUB Operational
@app.route('/get_similar_images', methods=['GET'])
def get_similar_images():
    fileID = request.args['fileID']
    classID = int(request.args['classID'])
    #print(fileID, classID)

    if classID == -1:
        resp = flask.Response(status=123)
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp

    jsonfile = open('../tmp/output.json', 'r')
    json_data = json.loads(jsonfile.read())
    filename_mainImage = json_data[str(fileID)]['FILENAME']
    #print("\nMain Filename:",filename_mainImage)

    scores , top_sim_images = get_similar_images_faiss(filename_mainImage, classID)
    #_, _= get_similar_images_annoy(filename_mainImage, classID)
    img_list = []

    for i in range(5):
        filename = top_sim_images[i]
        IDX = str(i)
        img_data = rescaleImage(filename)
        data_set = {"IMG": {"IDX": IDX,
                            "FILENAME": filename,
                            "SIM_SCORE": str(scores[0][i]),
                            "IMG_DATA": img_data.decode('utf-8')}}
        img_list.append(data_set)


    response = jsonify(img_list)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


###################################################################################################
# GET EXPLANATIONS - Operational
@app.route('/get_explanations', methods=['GET'])
def get_explanations():
    fileID = int(request.args['fileID'])
    classID = int(request.args['classID'])
    if classID == -1:
        resp = flask.Response(status=123)
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp

    jsonfile = open('../tmp/output.json', 'r')
    json_data = json.loads(jsonfile.read())
    filename = json_data[str(fileID)]['FILENAME']
    classPredictedID = classID
    path_1, path_2, path_3 = call_explanations(filename, classPredictedID)

    img_list = []

    L1 = 'Conv2d_2a_3x3'
    L2 = 'Mixed_5c'  # 'Conv2d_2a_3x3'
    L3 = 'Mixed_7c'
    with open(path_1, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    data_set = {"IMG": {"IDX": "1","FILENAME": path_1, "LAYER_NO": L1 , "IMG_DATA": encoded_string.decode('utf-8')}}
    img_list.append(data_set)

    with open(path_2, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    data_set = {"IMG": {"IDX": "2","FILENAME": path_2, "LAYER_NO": L2 , "IMG_DATA": encoded_string.decode('utf-8')}}
    img_list.append(data_set)

    with open(path_3, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    data_set = {"IMG": {"IDX": "3","FILENAME": path_3, "LAYER_NO": L3 , "IMG_DATA": encoded_string.decode('utf-8')}}
    img_list.append(data_set)


    response = jsonify(img_list)
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


###################################################################################################
# SAVE USER ACTIONS - Calling part by Chirag
@app.route('/save_user_action', methods=['GET'])
def save_user_action():
    fileID = request.args['fileID']
    userAction = request.args['userAction']
    correctedLabel = request.args['correctedLabel']
    print(fileID,userAction,correctedLabel)
    str_concat = fileID +","+ userAction +","+ correctedLabel

    jsonfile = open('../tmp/output.json', 'r')
    json_data = json.loads(jsonfile.read())
    filename = json_data[str(fileID)]['FILENAME']

    # Open a file with access mode 'a'
    file_object = open('../tmp/UserAction.txt', 'a')
    # Append at the end of file
    file_object.write(str_concat)
    # Close the file
    file_object.close()

    """
    save_user_action(current_img_id, action, corrected_label): returns void
	Action: Save user actoins in the folowing format
	
	    Save : CURRENT_IMAGE_PATH, USER_ACTION, CORRECTED_CLASS_ID
    
    :return:
    """
    response = jsonify("")
    response.headers.add("Access-Control-Allow-Origin", "*")
    #print(request)
    return response#"", 204


##################################################################################################
# GET FILES - Operational
@app.route('/files/get/', methods=['GET'])
def get_files():
    file_path = request.args['filePath']
    response = send_file(file_path)
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


###################################################################################################
# CUSTOM FUNCTIONS
def rescaleImage(image_path):
    foo = Image.open(image_path)
    foo = foo.convert('RGB')
    x, y = foo.size
    x2, y2 = math.floor(x - 50), math.floor(y - 20)
    foo = foo.resize((x2, y2), Image.ANTIALIAS)
    foo.save("../tmp/image_scaled.jpg", quality=10, optimize=True)
    with open("../tmp/image_scaled.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


####################################################################################################
# CALLING API
if __name__ == '__main__':
    app.run(host='10.2.1.21', port=9000, debug=True)
####################################################################################################

# Refer paper for CORS - https://dev.to/matheusguimaraes/fast-way-to-enable-cors-in-flask-servers-42p0
