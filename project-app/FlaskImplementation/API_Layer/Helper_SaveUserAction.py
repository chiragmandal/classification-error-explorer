import os

import csv

from csv import writer


def get_user_action(file_name, userAction, corrected_label):

    f= open("../tmp/save_user_action.csv","w")
    #list_len = len(fileID)
    #print(list_len)





    temp = "FileID,Corrected_Label\r\n"
    f.write(temp)

    if(userAction == 'Fix_Image_Label'):

        with open(f, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(list_of_elem)

        temp = file_name + "," + corrected_label + "\r\n"
        append_list_as_row('save_user_action.csv', temp)
        f.write(temp)

    if(userAction == 'Tag_Out_Of_Distribution'):
        temp = file_name + "," + "Out of distribution" + "\r\n"
        f.write(temp)

    if(userAction=='Add_To_Training_Set'):
        temp = file_name + "," + "Add to training set" + "\r\n"
        f.write(temp)

    f.close()
