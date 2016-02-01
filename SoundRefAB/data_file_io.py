import tempfile
import numpy as np
import os 

def store_temp_data_file(data,  subject_id=0):
    filename=tempfile.gettempdir()+'subj%d_temp.npy'%(subject_id)
    np.save(filename,data)

def retrieve_temp_data_file( subject_id=0):
    filename=tempfile.gettempdir()+'subj%d_temp.npy'%(subject_id)
    data = np.load(filename)
    return data.tolist()
    
def erase_temp_data_file(subject_id=0):
    filename=tempfile.gettempdir()+'subj%d_temp.npy'%(subject_id)
    try:
        os.remove(filename)
    except OSError:
        pass
