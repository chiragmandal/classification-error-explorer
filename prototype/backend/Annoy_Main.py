import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import fire
import logging
from pathlib import Path
import os
from annoy_sim import run_annoy



LOGGER = logging.getLogger(__name__)

def main():
    # train_path = Path.cwd() / 'train_embeddings'
    # test_path = Path.cwd() / 'val_embeddings'
    train_path = '/project/dsilva/TinyImagenet_IS/train_embeddings'
    test_path = '/project/dsilva/TinyImagenet_IS/val_embeddings'

    p = 145
    run_annoy(p, train_path, test_path )

    return
main()