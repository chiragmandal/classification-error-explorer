import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import fire
import logging
from pathlib import Path
import os

from knn import random_search


LOGGER = logging.getLogger(__name__)


# print(tfds.list_builders())




def main():
    # sess = tf.compat.v1.Session.ConfigProto(log_device_placement=True)
    # print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
    # emb = save()
    #
    train_path = Path.cwd() / 'train_embeddings'
    test_path = Path.cwd() / 'val_embeddings'

    p = 145
    random_search(train_path,test_path ,p )


    # input_path = path
    # path = Path.cwd() / +'embeddings_numpy'
    # path.mkdir(parents=True , exist_ok=True)
    # output_path = path
    # embeddings_to_numpy(input_path, output_path)
# -------------------------------------------------------------------------------------------------
#     For listing dircetories
#     path = Path.cwd() / 'images'
#     dirs = [e for e in path.iterdir() if e.is_dir()]
#     print(dirs)
# -------------------------------------------------------------------------------------------------------

main()