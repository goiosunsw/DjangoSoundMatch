from django.core.management.base import BaseCommand
from SoundRefAB import vibrato
from django.conf import settings

import os
import sys

def LoudnessSamples():
    '''Generate samples for loudness page'''
    pass
    
def BrightnessSamples():
    '''Generate samples for brightness page'''
    pass
    
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
        base_path = os.path.join(settings.STATIC_ROOT,'SoundRefAB','static','SoundRefAB')
        LoudnessSamples()
        BrightnessSamples()
        VibratoExplainSamples(base_path=base_path)
        
        
            
                     
