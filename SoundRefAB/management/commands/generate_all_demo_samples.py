from django.core.management.base import BaseCommand
from SoundRefAB import vibrato
import SoundRefAB.vibrato_obj as vo
from django.conf import settings
import numpy as np

import os
import sys

def ConstantTone(filename,ampl=0.05,sr=44100,nharm=6,vib_slope=0.0, dur=0.6):
    vib = vo.Vibrato(harm0=np.ones(nharm)/float(nharm)*ampl,vibfreq=6.0)
    vib.setProfile(t_prof=[0.0,dur],v_prof=[0.0,0.0])
    vib.setEnvelope(t_att=0.05,t_rel=0.02)
    
    blims = vib_slope
    amplitude = 0.0
    vib.calculateWav(brightness=[blims],amplitude=amplitude,frequency=0.0)
    vib.saveWav(filename=filename)

def LoudnessSamples(base_path='.'):
    '''Generate samples for loudness page'''
    sound_data=[{'filename': 'pg_loudness_adj_ref.wav',
                 'ampl': 0.4,
                 'slope': .2},
                {'filename': 'pg_loudness_adj_refX2.wav',
                 'ampl': 1,
                 'slope': .2}]
    for sd in sound_data:
        filename = os.path.join(base_path,sd['filename'])
        ConstantTone(filename=filename, 
                       ampl=sd['ampl'], 
                       vib_slope=sd['slope'])
    

    
def BrightnessSamples(base_path='.'):
    '''Generate samples for brightness page'''
    sound_data=[{'filename': 'pg_brightness_adj_dark.wav',
                 'ampl': 1,
                 'slope': .1},
                {'filename': 'pg_brightness_adj_bright.wav',
                 'ampl': 1,
                 'slope': .5}]
    for sd in sound_data:
        filename = os.path.join(base_path,sd['filename'])
        ConstantTone(filename=filename, 
                       ampl=sd['ampl'], 
                       vib_slope=sd['slope'])
    
    
def VibratoExplainSamples(base_path='.'):
    '''Generate samples for vibrato explanation pages'''
    sound_data=[{'filename': 'pg_vibrato_expl_no_vib.wav',
                 'hdepth': 0,
                 'slope': 1},
                {'filename': 'pg_vibrato_expl_small_timbre_vib.wav',
                 'hdepth': 2.5,
                 'slope': 1},
                {'filename': 'pg_vibrato_expl_small_loudness_vib.wav',
                 'hdepth': 3,
                 'slope': -1},
                {'filename': 'pg_vibrato_expl_large_timbre_vib.wav',
                 'hdepth': 6,
                 'slope': 1},
                {'filename': 'pg_vibrato_expl_large_loudness_vib.wav',
                 'hdepth': 8,
                 'slope': -1},
    ]
    
    for sd in sound_data:
        filename = os.path.join(base_path,sd['filename'])
        vibrato.SlopeVibratoWAV(filename=filename, 
                       hdepth=sd['hdepth'], 
                       vib_slope=sd['slope'],
                       amp=0.05)



class Command(BaseCommand):
    args = ''
    help = 'Generate all samples needed for demo pages (fixed samples)'

    def handle(self, *args, **options):
        base_path = os.path.join(settings.STATIC_ROOT,'SoundRefAB')
        LoudnessSamples(base_path=base_path)
        BrightnessSamples(base_path=base_path)
        VibratoExplainSamples(base_path=base_path)
        
        
            
                     
