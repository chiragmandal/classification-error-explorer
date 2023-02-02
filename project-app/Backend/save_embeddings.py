from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import ResNet50, InceptionV3
# from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.inception_v3 import preprocess_input
import numpy as np
import os
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import tensorflow as tf






def get_foldernames(folder_path, excel_file_path ):
    folder_list = []
    df = pd.read_excel(excel_file_path )
    folder_list = df['name'].tolist()
    print(len(folder_list))
    print(folder_list)


    # i = 0
    # for filename in os.listdir(folder_path):
    #     f = str(filename)
    #     folder_list.append(f)
    # print(folder_list)

    return folder_list

def save_embeddings_ds_to_pandas(df, id , features, filename, folder , path):
    # print(features.tolist())
    # embeddings = pa.array(features.tolist(), type=pa.list_(pa.float32()))
    #
    # imagenames = pa.array(filename ,  type = pa.list_(pa.string()))
    # foldernames = pa.array(folder , type = pa.list_(pa.string()) )
    # # print(filename, folder , embedding)
    # table = pa.Table.from_arrays([imagenames, foldernames , embeddings], ["image_name","folder" ,"embedding"])
    # pq.write_table(table, path)
    df_row = {}
    df_row['id'] = id
    df_row['imagename'] = filename[0]
    df_row['folder'] = folder[0]
    df_row['embedding'] = features.tolist()
    df = df.append(df_row, ignore_index=True)
    if(id == 0 or id == 1299):
        print("Dataframe for ", id)
    return df


def calculate_embedding( image_file, image_path,model , id ):


    img = image.load_img(image_path, target_size=(224,224))
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    # --------------------------------------
    # img_data /= 255
    # img_data -=0.5
    # img_data *=2
    # -------------------------------------------
    feature = model.predict(img_data)
    feature_np = np.array(feature).flatten()
    # print( "  saved")
    # print(len(feature_np), image_file)

    # print(feature_np, image_file)
    if(id == 0 or id == 1299):
        print("Emb calculation done for ", id)

    return feature_np


def save_embeddings(folder_path, embeddings_path , excel_file_path):

    filename = []
    foldername = []
    folder_length = []
    folder_list = get_foldernames(folder_path, excel_file_path)
    os.environ['HTTP_PROXY'] = 'http://proxy:3128/'
    os.environ['HTTPS_PROXY'] = 'http://proxy:3128/'
    # model = ResNet50(weights='imagenet', include_top=False)
    # model = InceptionV3(weights='imagenet', include_top=False)
    model = InceptionV3(weights='imagenet', include_top=False)
    # print(folder_list)
    df = pd.DataFrame(columns=["id", "imagename", "folder", "embedding"])
    # print(df)
    for folder in range(len(folder_list)):
    # for folder in range(312, 313):

        emb_list = [ ]
        id = 0
        image_folder_path = folder_path + '/'+ str(folder_list[folder])
        print("Folder: ", folder)

        for image_file in os.listdir(image_folder_path):

            # if image_file.endswith(".JPEG"):
            if image_file.endswith(".png"):
                image_path = image_folder_path + '/'+image_file
                embeddings = calculate_embedding( image_file,image_path,model, id)
                foldername = str(folder_list[folder])
                # filename.append(image_file)
                # foldername.append(str(folder_list[folder]))
                # df = save_embeddings_ds_to_pandas(df, id , embeddings , filename , foldername , embeddings_path)
                emb_list.append([id , image_file, foldername, embeddings])

                id = id + 1
                # df.to_parquet(embeddings_path+'/' + str(folder_list[folder]) + '.parquet.gzip')
        # df.to_parquet(embeddings_path+'/' + 'embeddings.parquet.gzip')
        emb_df = pd.DataFrame(data = emb_list, columns=["id", "imagename", "folder", "embedding"])
        emb_df.to_parquet(embeddings_path+'/' + foldername + '.parquet.gzip')
        # emb_df.to_parquet(embeddings_path+'/' + 'embeddings.parquet.gzip')
        # print(len(emb_df))
        # for index , row  in emb_df.iterrows():
        #     print(row['id'], row['imagename'], row['embedding'])
        print("Parquet saved for ", foldername," ", folder)
    #
    #
    # # print(df.head())
    # # print(len(df.index))
    #
    # emb = pq.read_table(embeddings_path+'/' + 'embeddings.parquet.gzip').to_pandas()
    # print(emb)
    return

train_folder_path = '/data/imagenet/ILSVRC2012_img_train'
training_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/imagenet_embeddings'
excel_file_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/folder_list.xlsx'

save_embeddings(train_folder_path , training_emb_path , excel_file_path)


test_folder_path = '/data/objectnet/objectnet-1.0/images'
test_emb_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_embeddings'
excel_file_path = '/project/dsilva/Implementation/ClassificationErrorExplorer/objectnet_folder_list.xlsx'

save_embeddings(test_folder_path , test_emb_path , excel_file_path)