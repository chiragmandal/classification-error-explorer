from annoy import AnnoyIndex
import random
import numpy as np
import pyarrow.parquet as pq

from dataclasses import dataclass
from IPython.display import Image, display
from ipywidgets import widgets, HBox, VBox
import faiss
import random
import json
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.metrics.pairwise import cosine_similarity

def read_embeddings(path):
    emb = pq.read_table(path).to_pandas()
    # print(emb)
    id_to_name = {k: v.decode("utf-8") for k, v in enumerate(list(emb["image_name"]))}
    name_to_id = {v: k for k, v in id_to_name.items()}
    embgood = np.stack(emb["embedding"].to_numpy())
    return [id_to_name, name_to_id, embgood]

def build_index(emb_train, emb_test ):
    f = 2048
    emb_train = emb_train/np.linalg.norm(emb_train)
    emb_test = emb_test /np.linalg.norm(emb_test)
    index = AnnoyIndex(f, 'euclidean')
    index.add_item(0 , emb_test)
    for i in range(1, len(emb_train)):
        index.add_item(i, emb_train[i])
    index.build(1000)
    index.save('test.ann')
    index.load('test.ann')
    # print(index.get_nns_by_item(0, 6))
    nn = index.get_nns_by_item(0, 6)
    return index, nn

def run_annoy(p, train_path ,test_path):

    [id_to_name, name_to_id, embeddings_train] = read_embeddings(train_path)
    [id_to_name_test, name_to_id_test, embeddings_test] = read_embeddings(test_path)
    index, nn = build_index(embeddings_train , embeddings_test[p])
    print(id_to_name_test[p])
    display_picture(id_to_name_test[p] , "test")
    for i in range(1, len(nn)):
        print(id_to_name[nn[i]-1])
        image_name = id_to_name[nn[i]-1]
        display_picture(image_name, "train")
    return

def display_picture( image_name , m):
    if (m == "train"):
        # image_path = Path.cwd() / 'train_images'
        image_path = '/project/dsilva/TinyImagenet_IS/train_images'
    else:
        # image_path = Path.cwd() / 'val_images'
        image_path = '/project/dsilva/TinyImagenet_IS/val_images'
    # display(Image(filename=f"{image_path}/{image_name}.jpeg"))
    # im = Image.open(f"{image_path}/{image_name}.jpeg")
    # im.show()
    filename=f"{image_path}/{image_name}.jpeg"
    image = mpimg.imread(filename)
    plt.imshow(image)
    plt.show()
