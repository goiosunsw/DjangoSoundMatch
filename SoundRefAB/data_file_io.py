import tempfile
import numpy as np
import os 

def store_temp_data_file(data,  subject_id=0, suffix='temp'):
    filename=os.path.join(tempfile.gettempdir(),'subj%d_%s.npy'%(subject_id, suffix))
    np.save(filename,data)

def retrieve_temp_data_file( subject_id=0, suffix='temp'):
    filename=os.path.join(tempfile.gettempdir(),'subj%d_%s.npy'%(subject_id, suffix))
    data = np.load(filename)
    if data.dtype.fields is None: 
        return data.tolist()
    else:
        return data
    
def erase_temp_data_file(subject_id=0, suffix='temp'):
    filename=os.path.join(tempfile.gettempdir(),'subj%d_%s.npy'%(subject_id, suffix))
    try:
        os.remove(filename)
    except OSError:
        pass
