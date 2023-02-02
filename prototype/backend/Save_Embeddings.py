import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import fire
import logging
from pathlib import Path
import os
import pyarrow.parquet as pq


from inference import run_inference, write_tfrecord
# from knn import random_search, embeddings_to_numpy
from save_examples_to_folder import save_examples_to_folder

LOGGER = logging.getLogger(__name__)

def load_dataset ():
    ds, ds_info = tfds.load('tf_flowers', split='train', with_info=True)
    return ds, ds_info

def save_embeddings_train_ds( ):
    os.environ['HTTP_PROXY'] = 'http://proxy:3128/'
    os.environ['HTTPS_PROXY'] = 'http://proxy:3128/'
    save_examples_to_folder("train", "train_images", images_count=30000)
    write_tfrecord("train_images", "train_tfrecords", 1)
    run_inference("train_tfrecords", "train_embeddings", 1000)
    emb = pq.read_table("train_embeddings").to_pandas()
    print(emb)
    return emb

def save_embeddings_val_ds( ):
    os.environ['HTTP_PROXY'] = 'http://proxy:3128/'
    os.environ['HTTPS_PROXY'] = 'http://proxy:3128/'
    save_examples_to_folder("validation", "val_images", images_count= 10000)
    write_tfrecord("val_images", "val_tfrecords", 1)
    run_inference("val_tfrecords", "val_embeddings", 10000)
    emb = pq.read_table("val_embeddings").to_pandas()
    print(emb)
    return

# print("Check ")
save_embeddings_train_ds()
# print("Check ")
save_embeddings_val_ds()