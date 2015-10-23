import vibrato
import random

def VibratoTripletRefAB(prev_param, prev_confidence, subject_id):
    n_sounds = 3
    
    
    
    #
    base_phase = random.randint(0,1)
    base_amp_depth = random.rand()
    
    
    # reference sound
    filename = 'Sample1_Subj%d'%subject_id
    sound_data['name'] = 'Reference'
    sound_data['file'] = filename
    
    vibrato.VibratoWAV(filename=filename, )
    
    # test sounds
    
    
    return sound_data, param_data