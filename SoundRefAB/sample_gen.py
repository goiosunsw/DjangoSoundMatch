import vibrato
import random
import os
import numpy as np

import data_file_io as dio 


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
    
def LoudnessAdjust(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        ntrials = 1, const_par=[],prev_param=[], path='.', url_path='/'):
                 
    # include an empty string so that store params knows what to store
    ref_sd = {'name': 'Reference',
                'file': '',
                'choice': False}
    adj_sd = {'name': 'Adjusted',
                'file': '',
                'choice': True}
    sound_data=[ref_sd,adj_sd]
    
    subj_no = int(subject_id)
    
    try:
        #const_par = dio.retrieve_temp_data_file(subj_no)
        ampl_list = dio.retrieve_temp_data_file(subj_no)
    except IOError, KeyError: 
        ampl_list = np.logspace(-1.3,-0.3,ntrials).tolist()
        random.shuffle(ampl_list)
        
    if 'nharm' not in prev_param[0].keys():
        for pp in prev_param:
            pp['ampl']=0.5
            pp['nharm']=15
            pp['slope']=0.1
            pp['dur']=0.6
            pp['freq']= 500
            #pp['trial_no']=0
    
    
    param_data = []
    new_param = prev_param
    #print prev_param
    
    try:    
        newampl = ampl_list.pop()
    except IndexError:
        # something went wrong wit sequence, maybe user has clicked reload
        temp_list = np.linspace(0,1,ntrials).tolist()
        random.shuffle(temp_list)
        newampl = temp_list.pop()
    
    for thispar in new_param:
        thispar['ampl'] = newampl
        thispar['adj_par_name'] = 'ampl'
        thispar['val0'] = newampl
    
    # for sd in sound_data:
    #     param_data.append(new_param)
    param_data = new_param
    dio.store_temp_data_file(ampl_list, subj_no)
    
    return sound_data, param_data, difficulty_divider
    
def LoudnessAdjust_process(param_dict):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    try:
        med_twice_loudness = np.median([pp[1]['ampl']/pp[0]['ampl'] for pp in param_dict])
    except KeyError:
        med_twice_loudness = -1
    
    result_dict = {'med_twice_loudness' : med_twice_loudness}
    
    return result_dict


def BrightnessAdjust(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        ntrials = 1, const_par=[],prev_param=[], path='.', url_path='/'):
                 
    # include an empty string so that store params knows what to store
    ref_sd = {'name': 'Reference',
                'file': '',
                'choice': False}
    adj_sd = {'name': 'Adjusted',
                'file': '',
                'choice': True}
    sound_data=[ref_sd,adj_sd]
    
    subj_no = int(subject_id)
    
    try:
        #const_par = dio.retrieve_temp_data_file(subj_no)
        slope_list = dio.retrieve_temp_data_file(subj_no)
        # check that list is not empty
        dummy=slope_list[0]
    except (IOError, KeyError, IndexError) as e: 
        slope_list = np.linspace(0,1,ntrials).tolist()
        random.shuffle(slope_list)
        
    if 'nharm' not in prev_param[0].keys():
        for pp in prev_param:
            pp['ampl']=0.5
            pp['nharm']=15
            pp['slope']=20
            pp['dur']=0.6
            pp['freq']= 500
            #pp['trial_no']=0
    
    
    param_data = []
    new_param = prev_param
    #print prev_param
    try:
        newslope = slope_list.pop()
    except IndexError:
        # something went wrong wit sequence, maybe user has clicked reload
        temp_list = np.linspace(0,1,ntrials).tolist()
        random.shuffle(temp_list)
        newslope = temp_list.pop()
        
        
    for thispar in new_param:
        thispar['slope'] = newslope
        thispar['adj_par_name'] = 'slope'
        thispar['val0'] = newslope
    
    # for sd in sound_data:
    #     param_data.append(new_param)
    param_data = new_param
    dio.store_temp_data_file(slope_list, subj_no)
    
    return sound_data, param_data, difficulty_divider

def BrightnessAdjust_process(param_dict):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    try:
        med_twice_brightness = np.median([pp[1]['slope']-pp[0]['slope'] for pp in param_dict])
    except KeyError:
        med_twice_brightness = -1
    
    result_dict = {'med_twice_brightness': med_twice_brightness}
    
    return result_dict
                        