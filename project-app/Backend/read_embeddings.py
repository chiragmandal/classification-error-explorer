import numpy as np
import os
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd


# training_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_embeddings'
training_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings'

emb = pq.read_table(training_emb_path+'/' + 'n02493793.parquet.gzip').to_pandas()
# emb = pq.read_table(training_emb_path+'/' + 'embeddings.parquet.gzip').to_pandas()

data = pd.DataFrame(emb)
# for index, row in data.iterrows():
#     print(row['id'], row['imagename'],row['folder'], row['embedding'], len(row['embedding']))

index_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/faiss_index/'
print(len(os.listdir(index_path)))