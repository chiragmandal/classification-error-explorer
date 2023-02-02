import pyarrow.parquet as pq

from dataclasses import dataclass
from IPython.display import Image, display
from ipywidgets import widgets, HBox, VBox
import faiss
import numpy as np
import random
import json
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg



def read_embeddings(path):
    emb = pq.read_table(path).to_pandas()
    # print(emb)
    id_to_name = {k: v.decode("utf-8") for k, v in enumerate(list(emb["image_name"]))}
    name_to_id = {v: k for k, v in id_to_name.items()}
    embgood = np.stack(emb["embedding"].to_numpy())
    return [id_to_name, name_to_id, embgood]

def embeddings_to_numpy(input_path, output_path):
    emb = pq.read_table(input_path).to_pandas()
    Path(output_path).mkdir(parents=True, exist_ok=True)
    id_name = [{"id": k, "name": v.decode("utf-8")} for k, v in enumerate(list(emb["image_name"]))]
    json.dump(id_name, open(output_path + "/id_name.json", "w"))

    emb = np.stack(emb["embedding"].to_numpy())
    np.save(open(output_path + "/embedding.npy", "wb"), emb)

def build_index(emb):
    d = emb.shape[1]
    xb = emb
    xb = xb /np.linalg.norm(xb)
    index = faiss.IndexFlatIP(d)
    index.add(xb)
    return index
def random_search(train_path, test_path ,p ):

    [id_to_name, name_to_id, embeddings_train] = read_embeddings(train_path)
    [id_to_name_test, name_to_id_test, embeddings_test] = read_embeddings(test_path)
    index = build_index(embeddings_train)
    # p = random.randint(0, len(id_to_name) - 1)
    print(id_to_name_test[p])
    embeddings_test[p] = embeddings_test[p]/np.linalg.norm(embeddings_test[p])
    results = search(index, id_to_name, embeddings_test[p])
    display_picture(image_name = id_to_name_test[p])
    display_results(results)
    for e in results:
        print(f"{e[0]:.2f} {e[1]}")

def search(index, id_to_name, emb, k=5):
    D, I = index.search(np.expand_dims(emb, 0), k)  # actual search
    print(D)
    return list(zip(D[0], [id_to_name[x] for x in I[0]]))

def display_picture( image_name):
    image_path = Path.cwd() / 'val_images'
    # image_path = Path.cwd() / 'train_images'
    # display(Image(filename=f"{image_path}/{image_name}.jpeg"))
    # im = Image.open(f"{image_path}/{image_name}.jpeg")
    # im.show()
    filename=f"{image_path}/{image_name}.jpeg"
    image = mpimg.imread(filename)
    plt.imshow(image)
    plt.show()


def display_results(results):
    image_path = Path.cwd() / 'train_images'
    for e in results:
        image_name = e[1]
        filename=f"{image_path}/{image_name}.jpeg"
        image = mpimg.imread(filename)
        plt.imshow(image)
        plt.show()
    # hbox = HBox(
    #     [
    #         VBox(
    #             [
    #                 widgets.Label(f"{distance:.2f} {image_name}"),
    #                 widgets.Image(value=open(f"{image_path}/{image_name}.jpeg", "rb").read()),
    #             ]
    #         )
    #         for distance, image_name in results
    #     ]
    # )
    # display(hbox)

