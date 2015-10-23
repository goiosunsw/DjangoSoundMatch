import vibrato
import random
import os

def VibratoTripletRefAB(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        prev_param=[], path='.', url_path='/'):
    n_sounds = 3
    
    # max amplitude fluctuation (max)
    max_amp = 12.0
    
    # base values
    base_phase = [-1,1][random.randint(0,1)]
    base_amp_depth = max_amp * random.random()
    
    sound_data=[] 
    param_data=[] 
    filename=[]
    
    # reference sound
    basename = 'Sample0_Subj%d.wav'%int(subject_id)
    filename.append(os.path.join(path,basename))
    this_sd = {'name': 'Reference',
               'file': url_path+basename,
               'choice': False}
               
    this_pd = {'hdepth': base_amp_depth,
               'phrel': base_phase}
               
    sound_data.append(this_sd)
    param_data.append(this_pd)
    
    # vibrato.VibratoWAV(filename=sound_data[0]['filename'],
    #                    hdepth=param_data[0]['hdepth'],
    #                    phrel=param_data[0]['phrel'])
    
    # test sounds
    amplitude = []
    new_phase =  - base_phase
    amplitude.append(base_amp_depth)

    amp_min = max(0,base_amp_depth + max_amp/2.0 / difficulty_divider)
    amp_max = min(max_amp,base_amp_depth + max_amp/2.0 / difficulty_divider)
    amp_range = amp_max - amp_min
    amplitude.append( random.random() * amp_range + amp_min )
        
    # randomize sample order
    order = [0,1]
    random.shuffle(order)
    
    # one of the new sounds has the same amplitude as ref
    # the other one is different
    # but in random order
    for i in [1,2]:
        this_pd = {'hdepth': amplitude[order[i-1]],
                   'phrel': new_phase}
                   
        basename = 'Sample%d_Subj%d.wav'%(i,int(subject_id))
        filename.append(os.path.join(path,basename))
        this_sd = {'name': 'Sample %d'%i,
                   'file': url_path+basename,
                   'choice': True}
        
        sound_data.append(this_sd)
        param_data.append(this_pd)
    
    for i in [0,1,2]:
        vibrato.VibratoWAV(filename=filename[i], 
                           hdepth=param_data[i]['hdepth'], 
                           phrel=param_data[i]['phrel'],
                           amp=0.05)
    
    return sound_data, param_data, difficulty_divider
    
def SlopeVibratoTripletRefAB(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        prev_param=[], path='.', url_path='/'):
                        
    # use confidence history to increase or decrease difficulty
    avg_last_confidence = sum([xx*2-3 for ii,xx in enumerate(confidence_history) 
                            if ii>=len(confidence_history)-4 and ii>0])
    if avg_last_confidence > +2:
        difficulty_divider *= 2.0
    if avg_last_confidence < -3:
        difficulty_divider *= 0.5
        
    if difficulty_divider < 0.6:
        difficulty_divider = 0.5

    if difficulty_divider > 8:
        difficulty_divider = 8.0

    
    n_sounds = 3
    
    # max amplitude fluctuation (max)
    max_amp = 6.0
    
    # base values
    base_phase = [-1,1][random.randint(0,1)]
    base_amp_depth = max_amp * random.random()
    
    sound_data=[] 
    param_data=[] 
    filename=[]
    
    # reference sound
    basename = 'Sample0_Subj%d.wav'%int(subject_id)
    filename.append(os.path.join(path,basename))
    this_sd = {'name': 'Reference',
               'file': url_path+basename,
               'choice': False}
               
    this_pd = {'hdepth': base_amp_depth,
               'vib_slope': base_phase}
               
    sound_data.append(this_sd)
    param_data.append(this_pd)
    
    # vibrato.VibratoWAV(filename=sound_data[0]['filename'],
    #                    hdepth=param_data[0]['hdepth'],
    #                    phrel=param_data[0]['phrel'])
    
    # test sounds
    amplitude = []
    new_phase =  - base_phase
    amplitude.append(base_amp_depth)

    amp_min = max(0,base_amp_depth - max_amp/2.0 / difficulty_divider)
    amp_max = min(max_amp,base_amp_depth + max_amp/2.0 / difficulty_divider)
    amp_range = amp_max - amp_min
    amplitude.append( random.random() * amp_range + amp_min )
        
    # randomize sample order
    order = [0,1]
    random.shuffle(order)
    
    # one of the new sounds has the same amplitude as ref
    # the other one is different
    # but in random order
    for i in [1,2]:
        this_pd = {'hdepth': amplitude[order[i-1]],
                   'vib_slope': new_phase}
                   
        basename = 'Sample%d_Subj%d.wav'%(i,int(subject_id))
        filename.append(os.path.join(path,basename))
        this_sd = {'name': 'Sample %d'%i,
                   'file': url_path+basename,
                   'choice': True}
        
        sound_data.append(this_sd)
        param_data.append(this_pd)
    
    for i in [0,1,2]:
        vibrato.SlopeVibratoWAV(filename=filename[i], 
                           hdepth=param_data[i]['hdepth'], 
                           vib_slope=param_data[i]['vib_slope'],
                           amp=0.05)
    
    return sound_data, param_data, difficulty_divider