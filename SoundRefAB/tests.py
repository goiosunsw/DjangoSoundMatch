import datetime

from django.utils import timezone
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from .models import Experiment, SoundTriplet, Subject, Scenario, ItemInScenario
import sample_gen as sg
import numpy as np
import tempfile
import os
import sys
import re
from glob import glob

# Create your tests here.

def create_scenario(name, nparams = 0):
    s = Scenario.objects.create(description=name, created_date=timezone.now())
    return s


def create_experiment_in_scenario(scenario, name, nparams = 0):
    x = Experiment.objects.create(description=name, created_date=timezone.now())
    xcont=ContentType.objects.get_for_model(x)
    scenario.iteminscenario_set.create(content_type=xcont,object_id=x.id)
    return x
    
    
def create_sound_triplet_for_subject(sub,experiment):
    now=timezone.now()
    s = sub.soundtriplet_set.create(shown_date=now, valid_date=now, experiment=experiment)
    return s
 
def create_subject_for_scenario(scenario):
    now=timezone.now()
    #sub = Subject.objects.create(start_date=now, finish_date=now)
    x = scenario.subject_set.create(start_date=now, finish_date=now)
    return x


# tests for a complete experiment scenario
class CompletScenarioTests(TestCase):
    def test_experiment_with_one_parameter(self):
        s = create_scenario('Scenario with single experiment')
        x = create_experiment_in_scenario(s, 'Experiment with single parameter')
        sub = create_subject_for_scenario(s)
        s = create_sound_triplet_for_subject(sub,x)
        s.valid_date=timezone.now()
        return True

class ExperimentTests(TestCase):
    def test_create_experiment(self):
        """
        Check for any errors in creating experiment instance
        """
        x = Experiment(description='Test experiment', created_date=datetime.datetime.now())
        return True
        
# Create your tests here.
class SoundTripletTests(TestCase):
    def test_create_sound_triplet(self):
        """
        Check for any errors in creating a sound triplet
        """
        s = create_scenario('Scenario for sound triplet')
        x = create_experiment_in_scenario(s,'Experiment for sound triplet')
        sub = create_subject_for_scenario(s)
        s = create_sound_triplet_for_subject(sub,x)
        s.valid_date=timezone.now()
        return True
        

class TestVibratoRefABCSequence(TestCase):
    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)
        
        self.subj_no=1000
        
    def test_parameter_reading(self, n_runs=10, n_similar=2):
        """
        Check that parameters for a vibrato ABC sequence are 
        created and read in the right order
        """
        self.subj_no=1000
        mypath = '/tmp'
        
        bb=sg.SlopeVibratoRefABC_init(self.subj_no,n_runs=n_runs,n_similar=n_similar)
        prev_param=[]
        prev_choice=0
        prev_confidence=0
        confidence_history = []
        
        try:
            sys.path.append(os.path.join(os.environ['HOME'],'Devel/PyPeVoc/trunk/'))
            import SoundUtils as su
            from scipy.io import wavfile
            do_analysis = True
        except ImportError:
            sys.stdout.write('No Sound Analysis!\n')
            do_analysis = False
            
        sys.stdout.write('\n%12s (%2s): %-14s|%-12s|%-12s|\n'%('File','#','(typ) Req dept','Ampl','Cent'))
        
        marg = 10
        
        for i in xrange(n_runs):
            sound_data, prev_param, difficulty_divider = sg.SlopeVibratoRefABC(self.subj_no, path=mypath)
            if do_analysis:
                #sys.stdout.write('Run #%d'%i)
                for sno,sd in enumerate(sound_data):
                    if sno == 0:
                        pref = 'ref'
                    else:
                        pref = 'smpl'
                        
                    if bb[pref+'_phase'][i] > 0:
                        type = 'A'
                    else:
                        type = 'B'
                    filename = sd['file']
                    shortf = re.findall('[0-9a-zA-Z]+',filename)
                    sr, w = wavfile.read(os.path.join(mypath,filename[1:]))
                    amp_t, tt = su.RMSWind(w[:,0]/2.**16)
                    amp = np.max(amp_t[marg:-marg]) - np.min(amp_t[marg:-marg])
                    cent = 0.0
                    sys.stdout.write('%12s (%2d): %s %-12f|%-12f|%-12f|\n'%(shortf[0],i,type,bb[pref+'_depth'][i],amp,cent))
                    
        
        cc = np.load(os.path.join(tempfile.gettempdir(),'subj%d_AllVib.npy'%self.subj_no))
        
        #[os.remove(ff) for ff in glob(os.path.join(mypath,'*.wav'))]
        if len(cc) > 0:
            return False

    def test_sound(self, n_runs=10, n_similar=2):
        """
        Check that parameters for a vibrato ABC sequence are 
        created and read in the right order
        """
        self.subj_no=1000
        bb=sg.SlopeVibratoRefABC_init(self.subj_no,n_runs=n_runs,n_similar=n_similar)
        prev_param=[]
        prev_choice=0
        prev_confidence=0
        confidence_history = []
        
        for i in xrange(n_runs):
            sound_data, prev_param, difficulty_divider = sg.SlopeVibratoRefABC(self.subj_no)
        
        cc = np.load(os.path.join(tempfile.gettempdir(),'subj%d_AllVib.npy'%self.subj_no))
        if len(cc) > 0:
            return False

        
    def test_parameter_creation(self, n_runs=1000, n_similar=200):
        """
        Check that parameters for a vibrato ABC sequence are 
        created and read in the right order
        """
        def compare_struct_arrays(a,b):
            a_fields = a.dtype.fields.keys()
            b_fields = b.dtype.fields.keys()
    
            for fld in a.dtype.fields.keys():
                ar = a[fld]
                br = b[fld]
                for aa,bb in zip(ar,br):
                    if aa != bb:
                        return False
    
            return True
        
        self.subj_no=1000
        bb=sg.SlopeVibratoRefABC_init(self.subj_no,n_runs=1000,n_similar=200)
        cc = np.load(os.path.join(tempfile.gettempdir(),'subj%d_AllVib.npy'%self.subj_no))
        if not compare_struct_arrays(bb,cc):
            return False
        
        return True

    def test_parameter_phase(self, n_runs=1000, n_similar=200):
        """
        Check that parameters for a vibrato ABC sequence are 
        created and read in the right order
        """
        def compare_struct_arrays(a,b):
            a_fields = a.dtype.fields.keys()
            b_fields = b.dtype.fields.keys()
    
            for fld in a.dtype.fields.keys():
                ar = a[fld]
                br = b[fld]
                for aa,bb in zip(ar,br):
                    if aa != bb:
                        return False
    
            return True
        
        self.subj_no=1000
        bb=sg.SlopeVibratoRefABC_init(self.subj_no,n_runs=n_runs,n_similar=n_similar)
        cc = np.load(os.path.join(tempfile.gettempdir(),'subj%d_AllVib.npy'%self.subj_no))
        n_runs_cc = 0
        n_sim_cc = 0
        for i in xrange(len(bb)):
            n_runs_cc += 1
            if cc['ref_phase'][i]==cc['smpl_phase'][i]:
                n_sim_cc += 1
                
        if ((n_runs_cc != n_runs) or (n_sim_cc != n_similar)):
            return False
            
        return True
            
