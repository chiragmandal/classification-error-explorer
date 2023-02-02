import logging
from MainCode_Similarity import write_annoy_index, search
#LOGGER = logging.getLogger(__name__)

#################################################################

def get_similar_images_faiss(inp_path, classId):

    image_name = inp_path.split("/")[-1]
    actual_class = inp_path.split("/")[-2]

    scores, top_sim_images = search(classId, image_name, actual_class)
    #print("FAISS IMAGES:", top_sim_images)
    #print("FAISS SCORE: ", scores)
    return scores, top_sim_images
##################################################################
def get_similar_images_annoy(inp_path, classId):

    image_name = inp_path.split("/")[-1]
    actual_class = inp_path.split("/")[-2]

    scores, top_sim_images = write_annoy_index(classId, image_name, actual_class)
    #print("ANNOY IMAGES:", top_sim_images)
    #print("ANNOY SCORE: ", scores)

    return scores, top_sim_images
