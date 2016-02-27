import vibrato_obj as vo
import random
import os
import numpy as np
import sys

from decimal import Decimal

import data_file_io as dio 

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def MatchVibratoTypes(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        prev_param=[], path='.', url_path='/', prev_exp_dict=[]):
    '''A vibrato matching experiment where levels are fixed.
    Only 2 trials allowed'''
    
    
    # sound parameters per trial, Ref, S1 S2 inside trial
    slope_ampl = [0.1,0.2,0.5]
    loud_ampl = [0.1,0.2,0.5]
    phase = [[1, 1,-1],[-1, 1,-1]]
    ampl =  [[1, 2, 2],[ 1, 2, 2]]
    base_brightness = 0.5
    
    
    try:
        ntrial = int(prev_param[-1][0]['trial_no']) + 1
        sys.stderr.write('Trail nbr: %d\n'%ntrial)
    except (KeyError, IndexError) as e:
        ntrial = 0
        sys.stderr.write('Trail nbr not found in param data\n')
    
    sound_data=[] 
    param_data=[] 
    filename=[]
    
    # randomize sample order
    shorder = [1,2]
    random.shuffle(shorder)
    
    order = [0]
    order.extend(shorder)
    thisph = [phase[ntrial][oo] for oo in order] 
    thisa = [ampl[ntrial][oo] for oo in order] 
    
    count = 0
    for ph,amp in zip(thisph,thisa):
        if ph == -1:
            hdepth = loud_ampl[amp]
        else:
            hdepth = slope_ampl[amp]
            
        this_pd = {'hdepth': hdepth,
                   'vib_slope': ph,
                   'trial_no': ntrial}
        
        # reference sound
        basename = 'Sample%d_Subj%d.wav'%(count,int(subject_id))
        filename.append(os.path.join(path,basename))
        this_sd = {'name': 'Sample %d'%count,
                   'file': url_path+basename,
                   'choice': True}
        if count==0:
            this_sd['name'] = 'Reference'
            this_sd['choice'] = False
            
        count += 1   
        
        sound_data.append(this_sd)
        param_data.append(this_pd)
           
    nharm = 6
    vib = vo.Vibrato(harm0=np.ones(nharm)/float(nharm))
    vib.setProfile(t_prof=[0.0,0.3,0.7,1.5,1.6],v_prof=[0.0,0.0,0.5,1.0,0.0])
    vib.setEnvelope(t_att=0.05,t_rel=0.02)
               
    
    for i in xrange(len(sound_data)):
        # vibrato.SlopeVibratoWAV(filename=filename[i],
        #                    hdepth=param_data[i]['hdepth'],
        #                    vib_slope=param_data[i]['vib_slope'],
        #                    amp=0.05)
        depth = float(param_data[i]['hdepth'])
        if param_data[i]['vib_slope'] > 0:
            blims = base_brightness * (1 + depth *np.array([-1,1]))
            amplitude = 0.0
        else:
            amplitude = depth
            blims=np.array([1,1])*base_brightness
        vib.calculateWav(brightness=blims,amplitude=amplitude,frequency=0.0)
        vib.saveWav(filename=filename[i])
        
    
    return sound_data, param_data, difficulty_divider


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
                        prev_param=[], path='.', url_path='/', prev_exp_dict=[]):
                        
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
    
    try:
        twice_brigth = prev_exp_dict['med_twice_brightness']
    except KeyError:
        twice_brigth = 2
    
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
    
    nharm = 6
    vib = vo.Vibrato(harm0=np.ones(nharm)/float(nharm),vibfreq=6.0)
    vib.setProfile(t_prof=[0.0,0.3,0.7,1.5,1.6],v_prof=[0.0,0.0,0.5,1.0,0.0])
    vib.setEnvelope(t_att=0.05,t_rel=0.02)
    
    
    for i in [0,1,2]:
        # vibrato.SlopeVibratoWAV(filename=filename[i],
        #                    hdepth=param_data[i]['hdepth'],
        #                    vib_slope=param_data[i]['vib_slope'],
        #                    amp=0.05)
        depth = float(param_data[i]['hdepth'])
        if param_data[i]['vib_slope'] > 0:
            blims = base_brightness * (1 + depth *np.array([-1,1]))
            amplitude = 0.0
        else:
            amplitude = depth
            blims=np.array([1,1])*base_brightness
        vib.calculateWav(brightness=blims,amplitude=amplitude,frequency=0.0)
        vib.saveWav(filename=filename[i])
        
    
    return sound_data, param_data, difficulty_divider
    

def SlopeVibratoRefABC_init(subject_id, n_runs=3, n_similar=2):
    '''
    Generate a set of initialisation parameters for vibrato matching experiments.
    These are then randomised in order
    '''
    subj_no = int(subject_id)
    # rough conversion btween brightness depth and loudness depth:
    brightness_to_loudness_mult = 1.5
    
    # number of runs where matching different kinds
    n_diff = n_runs-n_similar
    
    # depth ranges
    brightness_lims = np.array([0.05,0.7])
    brightness_boundaries = np.linspace(*brightness_lims, num=n_diff/2+1)
    brightness_ranges = np.array([brightness_boundaries[i:i+2].tolist() for i in xrange(len(brightness_boundaries)-1)])
    #brightness_ranges = np.array([[0.05,0.15],[0.15,0.35],[0.35,0.7]])
    loudness_ranges = brightness_ranges * brightness_to_loudness_mult
    
    # central brightness range
    central_brightness = np.array([0.3,0.3])
    central_loudness = np.array([0.1,0.1])
    
    aa = np.empty(n_runs, dtype = [('ref_depth','f8'),('ref_phase','i'),('smpl_depth','f8'),('smpl_phase','i')])
    # ref_depths = np.empty((0,1))
    # ref_phases = np.empty((0,1))
    # smpl_depths = np.empty((0,1))
    # smpl_phases = np.empty((0,1))
    
    
    # generate loudness references
    count = 0
    for (ph_no,ranges) in enumerate((loudness_ranges, brightness_ranges)):
        n_ranges = ranges.shape[0]
        phase = [1,-1][ph_no]
        # multiplier for sample base depth
        mult = brightness_to_loudness_mult ** phase
        for i in range(n_runs/2):
            # generate different kinds or same?
            isdiff = i<n_diff/2
            this_range = ranges[i%n_ranges,...]
            vmin = np.min(this_range)
            vmax = np.max(this_range)
            this_ref_depth = vmin + np.random.random() * (vmax-vmin)
            aa['ref_depth'][count] = this_ref_depth
            aa['ref_phase'][count] = phase
            aa['smpl_depth'][count] = this_ref_depth * mult if isdiff else this_ref_depth
            aa['smpl_phase'][count] = -phase if isdiff else phase
            count +=1
            
    # randomize 
    # randomize sample order
    order = np.arange(len(aa))
    random.shuffle(order)
    
    aa = aa[order]
    arec = aa.view(np.recarray)
    dio.store_temp_data_file(arec, subj_no, suffix='AllVib')
    return aa
    
    
def SlopeVibratoRefABC(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        prev_param=[], path='.', url_path='/', prev_exp_dict=[]):
                        
    subj_no = int(subject_id)
    
    try:
        twice_bright = float(prev_exp_dict['med_twice_brightness'])
    except ( KeyError, TypeError ):
        twice_bright = 2.0
    
    n_sounds = 4
    
    # max amplitude fluctuation (max)
    max_amp = 1.0
    min_amp = 0.05
    max_slope = 1.0
    base_brightness = 0.5
    stop = False
    stop_confidence = 2
    
    
    # base values
    if prev_param==[]:
        aa = dio.retrieve_temp_data_file(subj_no, suffix='AllVib')
        try:
            # sys.stderr.write('Using pre-calculated parameters. Values stored for subject %d:\n'%subj_no)
            # sys.stderr.write('{}\t'.format(aa))
            base_amp_depth = aa['ref_depth'][0]
            base_phase = aa['ref_phase'][0]
            #last_chosen_amp = aa['smpl_depth'][0]
            last_chosen_amp = .5
            smpl_phase = aa['smpl_phase'][0]
            # sys.stderr.write('Values used:\n')
            # sys.stderr.write('ref_depth:\t %f\n'%base_amp_depth)
            # sys.stderr.write('ref_phase:\t %f\n'%base_phase)
            # sys.stderr.write('smpl_depth:\t %f\n'%last_chosen_amp)
            # sys.stderr.write('smpl_phase:\t %f\n'%smpl_phase)
        except IndexError:
            sys.stderr.write('Could not read parameters. Generating random.\n')
            base_amp_depth = random.random()
            base_phase = int(random.random()*2)-1
            last_chosen_amp = random.random()
            smpl_phase = int(random.random()*2)-1
        range_divider=1
        aa = aa[1:]
        dio.store_temp_data_file(aa, subj_no, suffix='AllVib')
    else:
        # Last chosen amplitude
        last_chosen_amp = prev_param[-1][prev_choice[-1]]['hdepth']
        
        range_divider = dio.retrieve_temp_data_file(subj_no)
        base_amp_depth = prev_param[-1][0]['hdepth']
        base_phase = prev_param[-1][0]['vib_slope']
        smpl_phase = prev_param[-1][-1]['vib_slope']
        if confidence_history[-1]>1:
            range_divider *= 1.3
        # if user has not been confident in last answers stop
        try:
            if confidence_history[-1]<stop_confidence :
                stop = True
        except KeyError:
            stop=False
        
    # check limits 
    base_amp_depth = np.clip(base_amp_depth, 0., 1.)
    last_chosen_amp = np.clip(last_chosen_amp, 0., 1.)
    
    
    sound_data=[] 
    param_data=[] 
    filename=[]
    
    # reference sound
    basename = 'Sample0_Subj%d.wav'%subj_no
    filename.append(os.path.join(path,basename))
    this_sd = {'name': 'Reference',
               'file': url_path+basename,
               'choice': False}
               
    this_pd = {'hdepth': base_amp_depth,
               'vib_slope': base_phase}
    
    if stop:
        this_pd['stop_conf'] = stop_confidence
    
    sound_data.append(this_sd)
    param_data.append(this_pd)
    
    # vibrato.VibratoWAV(filename=sound_data[0]['filename'],
    #                    hdepth=param_data[0]['hdepth'],
    #                    phrel=param_data[0]['phrel'])
    
    # test sounds
    amplitude = []
    new_phase =  smpl_phase
    amplitude.append(last_chosen_amp)
    
    range_around = twice_bright/range_divider
    multipliers = np.array([1./range_around,1.,range_around])
    amplitudes = float(last_chosen_amp) * multipliers
    
    # check that amplitudes are within bounds
    if ((np.min(amplitudes)<0.) or (np.max(amplitudes>1.))):
        amin = max((0.,np.min(amplitudes)))
        amax = min((1.,np.max(amplitudes)))
        amplitudes = np.linspace(amin,amax,3)

    
    # randomize sample order
    order = range(n_sounds-1)
    random.shuffle(order)
    
    # one of the new sounds has the same amplitude as ref
    # the other one is different
    # but in random order
    for i in xrange(1,n_sounds):
        this_pd = {'hdepth': amplitudes[order[i-1]],
                   'vib_slope': new_phase}
                   
        basename = 'Sample%d_Subj%d.wav'%(i,subj_no)
        filename.append(os.path.join(path,basename))
        this_sd = {'name': 'Sample %d'%i,
                   'file': url_path+basename,
                   'choice': True}
        
        sound_data.append(this_sd)
        param_data.append(this_pd)
    
    nharm = 6
    vib = vo.Vibrato(harm0=np.ones(nharm)/float(nharm),vibfreq=6.0)
    vib.setProfile(t_prof=[0.0,0.3,0.7,1.5,1.6],v_prof=[0.0,0.0,0.5,1.0,0.0])
    vib.setEnvelope(t_att=0.05,t_rel=0.02)
    
    
    for i in xrange(n_sounds):
        # vibrato.SlopeVibratoWAV(filename=filename[i],
        #                    hdepth=float(param_data[i]['hdepth']),
        #                    vib_slope=param_data[i]['vib_slope'],
        #                    amp=0.05)
        depth = float(param_data[i]['hdepth'])
        if param_data[i]['vib_slope'] > 0:
            blims = base_brightness * (1 + depth/2 *np.array([-1,1]))
            amplitude = 0.0
        else:
            amplitude = depth
            blims=np.array([1,1])*base_brightness
        vib.calculateWav(brightness=blims,amplitude=amplitude,frequency=0.0)
        vib.saveWav(filename=filename[i])
                           
    dio.store_temp_data_file(range_divider, subj_no)
    
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
    
    #default slider position
    default_val=0.0
    
    try:
        nharm = prev_param[-1][0]['nharm']
        ampl_list = dio.retrieve_temp_data_file(subj_no)
        
    except (IOError, KeyError, IndexError) as e:
        # first trial
        sys.stderr.write('First trial in LoudnessAdjust\n')
        ampl_list = np.logspace(-1.3,-0.6,ntrials).tolist()
        random.shuffle(ampl_list)
        dio.erase_temp_data_file(subj_no)
        for pp in prev_param[-1]:
            pp['ampl']=0.5
            pp['nharm']=15
            pp['slope']=0.2
            pp['dur']=0.6
            pp['freq']= 500
            #pp['trial_no']=0
        
        
        
    
    
    param_data = []
    new_param = prev_param[-1]
    #print prev_param
    
    try:    
        newampl = ampl_list.pop()
    except IndexError:
        # something went wrong wit sequence, maybe user has clicked reload
        #temp_list = np.linspace(0,1,ntrials).tolist()
        sys.stderr.write('Couldn''t get an amplitude value from original list\n')
        temp_list = np.logspace(-1.3,-0.3,ntrials).tolist()
        random.shuffle(temp_list)
        newampl = temp_list.pop()
    
    for thispar in new_param:
        thispar['ampl'] = newampl
        thispar['adj_par_name'] = 'ampl'
        thispar['val0'] = newampl
    
    new_param[1]['val0'] = default_val
    # for sd in sound_data:
    #     param_data.append(new_param)
    param_data = new_param
    dio.store_temp_data_file(ampl_list, subj_no)
    
    return sound_data, param_data, difficulty_divider
    
def LoudnessAdjust_process(param_dict):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    vals = []
    
    for pp in param_dict:
        try:
            vals.append(pp[1]['ampl']/pp[0]['ampl'])
        except (KeyError, IndexError,ZeroDivisionError) as e:
            pass
    
    if vals:
        med_twice_loudness = np.median(vals)
    else:
        med_twice_loudness = 3.16
    
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
    
    #default slider position
    default_val=0.0
    
    try:
        nharm = prev_param[-1][0]['nharm']
        slope_list = dio.retrieve_temp_data_file(subj_no)
    except (IOError, KeyError, IndexError) as e: 
        sys.stderr.write('First trial in BrightnessAdjust\n')
        slope_list = np.linspace(0,.7,ntrials).tolist()
        random.shuffle(slope_list)
        dio.erase_temp_data_file(subj_no)
        for pp in prev_param[-1]:
            pp['ampl']=0.5
            pp['nharm']=15
            pp['slope']=0.5
            pp['dur']=0.6
            pp['freq']= 500
            #pp['trial_no']=0
    
    
    param_data = []
    new_param = prev_param[-1]
    #print prev_param
    try:
        newslope = slope_list.pop()
    except IndexError:
        # something went wrong wit sequence, maybe user has clicked reload
        sys.stderr.write('Couldn''t get a slope value from original list\n')
        temp_list = np.linspace(0,1,ntrials).tolist()
        random.shuffle(temp_list)
        newslope = temp_list.pop()
        
        
    for thispar in new_param:
        thispar['slope'] = newslope
        thispar['adj_par_name'] = 'slope'
        thispar['val0'] = newslope
    
    new_param[1]['val0'] = default_val
    
    # for sd in sound_data:
    #     param_data.append(new_param)
    param_data = new_param
    dio.store_temp_data_file(slope_list, subj_no)
    
    return sound_data, param_data, difficulty_divider

def BrightnessAdjust_process(param_dict):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
    
    vals = []
    
    for pp in param_dict:
        try:
            vals.append(pp[1]['slope']-pp[0]['slope'])
        except (KeyError, IndexError,ZeroDivisionError) as e:
            pass
       
    if vals:
        #med_twice_brightness = np.median(vals)
        # FIXME: brightness scaling cannot work now because 
        # slider is not linear
        med_twice_brightness = 2.0
    else:
        med_twice_brightness = 2.0
    
    result_dict = {'med_twice_brightness': med_twice_brightness}
    
    return result_dict

def BrightnessAdjust_analyse(param_dict, path='.', url_path='/'):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    vals = []
    res=[]
    ref=[]
    graph=[]
    
    nharm = 6

    for pp in param_dict:
        try:
            sc1 = pp[1]['slope'] * (nharm-1) + 1 
            sc0 = pp[0]['slope'] * (nharm-1) + 1 
            vals.append(float(sc1/sc0))
            ref.append(pp[0]['slope'])
        except (KeyError, IndexError,ZeroDivisionError) as e:
            pass
    
    figbase = 'Analysis_BrightnessAdjust.png'
    figfile=os.path.join(path,figbase)
    figurl = url_path+figbase
    fig=Figure(figsize=(3,2))
    ax=fig.add_subplot(111)
    ax.plot(ref, vals, 'o')
    #fig.savefig(figname)
    canvas=FigureCanvas(fig)
    canvas.print_png(figfile)
    graph.append(figurl)
    
    
    if vals:
        twice_bright = Decimal(np.mean(vals))
        twice_bright_std = Decimal(np.std(vals))
        res.append({'name':'"Twice as bright" spectral cent. ratio','value':twice_bright})
        res.append({'name':'"Twice as bright" ratio dev','value':twice_bright_std})
    
    return res, graph


    
def LoudnessAdjust_analyse(param_dict, path='.', url_path='/'):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    vals = []
    ref = []
    res=[]
    graph=[]
    
    for pp in param_dict:
        try:
            
            vals.append(float(pp[1]['ampl']/pp[0]['ampl']))
            ref.append(float(pp[0]['ampl']))
        except (KeyError, IndexError,ZeroDivisionError) as e:
            sys.stderr.write('Error %s\n'%e)
            pass
    
    
    figbase = 'Analysis_LoudnessAdjust.png'
    figfile=os.path.join(path,figbase)
    figurl = url_path+figbase
    fig=Figure(figsize=(3,2))
    ax=fig.add_subplot(111)
    ax.plot(ref, vals, 'o')
    #fig.savefig(figname)
    canvas=FigureCanvas(fig)
    canvas.print_png(figfile)
    graph.append(figurl)
    
    if vals:
        twice_loudness = Decimal(np.mean(vals))
        twice_loudness_std = Decimal(np.std(vals))
        res.append({'name':'"Twice as loud" loudness ratio','value':twice_loudness})
        res.append({'name':'"Twice as loud" ratio deviation','value':twice_loudness_std})

    return res, graph


def SameLoudnessAdjust(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
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
    
    #default slider position
    default_val=0.0
    
    ref_slope=0.2
    other_slope=0.4
    
    try:
        nharm = prev_param[-1][0]['nharm']
        ampl_list = dio.retrieve_temp_data_file(subj_no)
        
    except (IOError, KeyError, IndexError) as e:
        # first trial
        sys.stderr.write('First trial in SameLoudnessAdjust\n')
        ampl_list = np.logspace(-1.3,-0.1,ntrials).tolist()
        random.shuffle(ampl_list)
        dio.erase_temp_data_file(subj_no)
        for pp in prev_param[-1]:
            pp['ampl']=0.5
            pp['nharm']=15
            pp['slope']=ref_slope
            pp['dur']=0.6
            pp['freq']= 500
            #pp['trial_no']=0
        
        
        
    
    
    param_data = []
    new_param = prev_param[-1]
    #print prev_param
    
    try:    
        newampl = ampl_list.pop()
    except IndexError:
        # something went wrong wit sequence, maybe user has clicked reload
        #temp_list = np.linspace(0,1,ntrials).tolist()
        sys.stderr.write('Couldn''t get an amplitude value from original list\n')
        temp_list = np.logspace(-1.3,-0.3,ntrials).tolist()
        random.shuffle(temp_list)
        newampl = temp_list.pop()
    
    for thispar in new_param:
        thispar['ampl'] = newampl
        thispar['adj_par_name'] = 'ampl'
        thispar['val0'] = newampl
    
    new_param[1]['val0'] = default_val
    new_param[1]['slope'] = other_slope
    # for sd in sound_data:
    #     param_data.append(new_param)
    param_data = new_param
    dio.store_temp_data_file(ampl_list, subj_no)
    
    return sound_data, param_data, difficulty_divider
    
def SameLoudnessAdjust_process(param_dict):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    vals = []
    
    for pp in param_dict:
        try:
            vals.append(pp[1]['ampl']/pp[0]['ampl'])
        except (KeyError, IndexError,ZeroDivisionError) as e:
            pass
    
    if vals:
        same_loudness_for_brighter = np.median(vals)
    else:
        same_loudness_for_brighter = 1.0
    
    result_dict = {'same_loudness_for_brighter' : same_loudness_for_brighter}
    
    return result_dict

def SameLoudnessAdjust_analyse(param_dict, path='.', url_path='/'):
    '''processes the results from the experiment 
       to get an indication of the 2x brightness value
    '''
       
    vals = []
    res=[]
    graph=[]
    ref=[]
    
    for pp in param_dict:
        try:
            vals.append(float(pp[1]['ampl']/pp[0]['ampl']))
            ref.append(pp[0]['ampl'])
        except (KeyError, IndexError,ZeroDivisionError) as e:
            pass
    
    figbase = 'Analysis_SameLoudnessAdjust.png'
    figfile=os.path.join(path,figbase)
    figurl = url_path+figbase
    fig=Figure(figsize=(3,2))
    ax=fig.add_subplot(111)
    ax.plot(ref, vals, 'o')
    #fig.savefig(figname)
    canvas=FigureCanvas(fig)
    canvas.print_png(figfile)
    graph.append(figurl)
    
    if vals:
        same_loudness_for_brighter = Decimal(np.mean(vals))
        same_loudness_for_brighter_std = Decimal(np.std(vals))
        res.append({'name':'Brighter to darker loudness ratio','value':same_loudness_for_brighter})
        res.append({'name':'Brighter to darker ratio dev','value':same_loudness_for_brighter_std})

    return res, graph
    
def LoudnessIntro(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        ntrials = 1, const_par=[],prev_param=[], path='.', url_path='/'):       
                        
    param_data = [{'html_template': 'trial_loudness_intro.html'}]
    sound_data = [{}]
    dificulty_divider = 1.
    
    return sound_data, param_data, difficulty_divider
    
def LoudnessIntro_process(param_dict):
    pass


def BrightnessIntro(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        ntrials = 1, const_par=[],prev_param=[], path='.', url_path='/'):       
                        
    param_data = [{'html_template': 'trial_brightness_intro.html'}]
    sound_data = [{}]
    dificulty_divider = 1.
    
    return sound_data, param_data, difficulty_divider
    
def BrightnessIntro_process(param_dict):
    pass

def DescribeVibrato(subject_id, difficulty_divider=1.0, confidence_history=[], prev_choice=0, 
                        ntrials = 1, const_par=[],prev_param=[], path='.', url_path='/'):       
                        
    param_data = [{'html_template': 'trial_vibrato_comment.html'}]
    sound_data = [{}]
    dificulty_divider = 1.
    
    return sound_data, param_data, difficulty_divider
    
def DescribeVibrato_process(param_dict):
    pass
    
