import pyarrow.parquet as pq
import numpy as np
from pathlib import Path
import sys
import resource
import os
from collections import defaultdict
import gc
import json
import faiss
from annoy import AnnoyIndex
import matplotlib.pyplot as plt
import matplotlib.image as mpimg



def memory_limit():
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (int (get_memory() * 1024 * 0.8), hard))

def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    print("Free memory: ", free_memory)
    return free_memory

def store_index_mappings(embpath):
    id_index = defaultdict(list)
    start_id = 0
    key = 0

    for parquet_file in sorted(os.listdir(embpath)):
        if parquet_file.endswith('.parquet.gzip'):
            path = embpath +'/' + parquet_file
            emb = pq.read_table(path).to_pandas()
            end_id = start_id + len(emb) - 1
            # foldername is the key
            foldername = str(parquet_file)
            foldername = foldername[foldername.index('n') : foldername.index('.parquet.gzip')]
            id_index[foldername].append([start_id, end_id])
            #print(id_index)
            if(key% 100 == 0):
                print("folder: ",  key)
            gc.collect()
            key = key + 1
            start_id = end_id + 1



    with open('/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_index_mappings.json', 'w') as fp:
        json.dump(id_index,fp)

    return

def get_folderlist( ):
    json_path = '/data/imagenet/imagenet_class_index.json'
    with open(json_path) as f:
        data = json.load(f)
    foldername = [ ]
    for row in data:
        foldername.append(data[row][0])
        # print(foldername)
    #print(len(foldername))
    return foldername


def get_foldername(classID):
    json_path = '/data/imagenet/imagenet_class_index.json'
    with open(json_path) as f:
        data = json.load(f)
    foldername = data[classID][0]
    #print(data[classID][1])
    return foldername


def write_index(embpath):
    index_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/faiss_index/'

    dims = 51200
    index = faiss.IndexFlatL2(dims)
    # index = faiss.index_factory( 51200,"IVF65536_HNSW32,PQ64" )
    folderlist = get_folderlist()


    for i in range(874, 1000):
        parquet_file = Path(embpath + str(folderlist[i]) + '.parquet.gzip')
        if parquet_file.is_file():
            emb_df = pq.read_table(parquet_file).to_pandas()
            emb = np.stack(emb_df["embedding"].to_numpy())
            emb = emb/np.linalg.norm(emb)
            index.add(emb)
            faiss.write_index(index , index_path + str(folderlist[i]) +'.index' )
            gc.collect()
            if(i%100 == 0):
                print("Index saved for ", i)

    return


def fill_missing(emb_path):
    index_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/faiss_index/'
    dims = 51200
    index = faiss.IndexFlatIP(dims)
    folderlist = get_folderlist()

    for i in range(len(folderlist)):
        index_file = Path(index_path + str(folderlist[i]) + '.index')
        if not (index_file.is_file()):
            parquet_file = Path(emb_path + str(folderlist[i]) + '.parquet.gzip')
            if parquet_file.is_file():
                emb_df = pq.read_table(parquet_file).to_pandas()
                emb = np.stack(emb_df["embedding"].to_numpy())
                emb = emb/np.linalg.norm(emb)
                index.add(emb)
                faiss.write_index(index , index_path + str(folderlist[i]) +'.index' )
                gc.collect()
                print(" Index saved ", i)


    return
def get_imagename(emb_df , indexlist):
    imagelist =[]
    #print("Index list",  indexlist)
    # print(" dataframe, ", len(emb_df))
    for i in indexlist:
        name = emb_df.iloc[i]["imagename"]
        imagelist.append(name)

    return imagelist
def faiss_search(index, test_emb, train_emb_df):
    k = 5
    D, I = index.search(test_emb, k)
    #print(D)
    similar_images = get_imagename(train_emb_df, I[0])
    return D, similar_images

def build_index(foldername):
    imagenet_emb_path ='/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings/'
    dims = 51200
    index = faiss.IndexFlatIP(dims)
    parquet_file = imagenet_emb_path + foldername +'.parquet.gzip'
    emb_df = pq.read_table(parquet_file).to_pandas()
    emb = np.stack(emb_df["embedding"].to_numpy())
    emb = emb/np.linalg.norm(emb)
    index.add(emb)
    return index, emb_df


def search (classID, imagename, test_image_folder ):

    index_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/faiss_index/'
    test_embpath = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_embeddings/'
    similar_images = defaultdict(list)
    foldername = str(get_foldername(str(classID)))
    # print("Folder found", foldername)
    # index = faiss.read_index(index_path + foldername + '.index')
    index, train_emb_df = build_index(foldername)
    # print("Index built")
    test_emb_df = pq.read_table(test_embpath+test_image_folder +'.parquet.gzip').to_pandas()
    # print(type(test_emb_df))
    test_emb = test_emb_df.loc[test_emb_df['imagename'] == imagename]
    test_emb_np = np.stack(test_emb["embedding"].to_numpy())
    test_emb_np = test_emb_np/np.linalg.norm(test_emb_np)
    scores, sim_imagelist = faiss_search(index,test_emb_np, train_emb_df)
    #print("Similar images", sim_imagelist)
    top_sim_images = []
    for image in sim_imagelist:
        train_image_path = '/data/imagenet/ILSVRC2012_img_train/' + foldername + '/' + image
        top_sim_images.append(train_image_path)

    return scores, top_sim_images

def annoy_search(index, test_emb, train_emb_df ):
    k = 5
    I, D = index.get_nns_by_vector(test_emb[0], k ,include_distances=True)
    #print("Nearest neighbours", I)
    similar_images = get_imagename(train_emb_df, I)
    return D, similar_images

def build_annoy_index(foldername):
    index_path = '/project/mukhopad/tmp/'#'/project/dsilva/Implementation/ClassificationErrorExplorer/annoy_index/'
    dims = 51200
    index = AnnoyIndex(dims, 'euclidean')
    imagenet_emb_path ='/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings/'
    parquet_file = imagenet_emb_path + foldername +'.parquet.gzip'
    emb_df = pq.read_table(parquet_file).to_pandas()
    emb = np.stack(emb_df["embedding"].to_numpy())
    emb = emb/np.linalg.norm(emb)

    for i in range(len(emb)):
        index.add_item(i, emb[i])
    index.build(100)
    index.save(index_path + foldername + '.ann')
    return index,emb_df

def write_annoy_index(classID, imagename, test_image_folder):
    index_path = '/project/mukhopad/tmp/'#'/project/dsilva/Implementation/ClassificationErrorExplorer/annoy_index/'
    test_embpath = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_embeddings/'
    foldername = str(get_foldername(str(classID)))


    index, train_emb_df = build_annoy_index(foldername)
    test_emb_df = pq.read_table(test_embpath+test_image_folder +'.parquet.gzip').to_pandas()
    test_emb = test_emb_df.loc[test_emb_df['imagename'] == imagename]
    test_emb_np = np.stack(test_emb["embedding"].to_numpy())
    test_emb_np = test_emb_np/np.linalg.norm(test_emb_np)
    index.load(index_path + foldername + '.ann')
    scores, sim_imagelist = annoy_search(index,test_emb_np, train_emb_df)
    #print("Similar images", sim_imagelist)
    top_sim_images = []
    for image in sim_imagelist:
        train_image_path = '/data/imagenet/ILSVRC2012_img_train/' + foldername + '/' + image
        top_sim_images.append(train_image_path)

    return scores, top_sim_images

def display_image(path):
    image = mpimg.imread(path)
    plt.imshow(image)
    plt.show()
    return



def build_index_gpu():

    dims = 51200
    res = faiss.StandardGpuResources()
    # quantizer = faiss.IndexFlatL2(dims)
    index =  faiss.IndexFlatL2(dims)
    ncentroids =1000
    code_size = 16
    # index = faiss.IndexIVFPQ(quantizer, dims, ncentroids, code_size, 8 )
    imagenet_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings/'
    i = 0
    for parquet_file in sorted(os.listdir(imagenet_emb_path)):
        if parquet_file.endswith('.parquet.gzip'):
            emb = pq.read_table(imagenet_emb_path + parquet_file).to_pandas()
            emb_np = np.stack(emb["embedding"].to_numpy())
            # print(emb_np[0].shape)
            index.add(emb_np)
            if(i % 100 == 0):
                print("Folder", i)
            i = i + 1

    return index

def faiss_gpu_search(imagename, test_image_folder):
    index_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/faiss_index/'
    test_embpath = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_embeddings/'
    test_emb_df = pq.read_table(test_embpath+test_image_folder +'.parquet.gzip').to_pandas()
    test_emb = test_emb_df.loc[test_emb_df['imagename'] == imagename]
    test_emb_np = np.stack(test_emb["embedding"].to_numpy())
    test_emb_np = test_emb_np/np.linalg.norm(test_emb_np)
    index = build_index_gpu()
    faiss.write_index(index , index_path + 'faiss.index' )

    return
def main():
    imagenet_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings/'
    actual_classID = 725
    predclassId = "463"
    image_name = "1c85018ba1d043c.png"
    actual_class = 'pitcher'
    search(predclassId, image_name, actual_class)
    search(actual_classID, image_name,  actual_class)

    #write_annoy_index(predclassId,  image_name, actual_class)
    #write_annoy_index(actual_classID,  image_name, actual_class)

    return

if __name__ == '__main__':
    memory_limit() # Limitates maximun memory usage
    try:
        main()
    except MemoryError:
        sys.stderr.write('\n\nERROR: Memory Exception\n')
        sys.exit(1)
