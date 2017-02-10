from django.core.management.base import BaseCommand
from SoundRefAB import vibrato_obj as vo
from django.conf import settings
import numpy as np

import os
import sys

class Command(BaseCommand):
    args = ''
    help = 'Generate javascript array for brightness sounds'

    def handle(self, *args, **options):
        base_path = os.path.join(settings.STATIC_ROOT,'SoundRefAB')
        outfile = os.path.join(base_path,'slopeAmps.js')
        sys.stdout = open(outfile,'w')
        sys.stderr.write('Writing to '+outfile+'\n')
        
        
        nharm=16
        # brightness limits in slider
        vlims=[0.0,0.9]
        # number of steps in slider
        n = 400
        
        sh = vo.SlopeHarmonicScaler(nharm=nharm)
        sh.outputJSArray(vlims=vlims,npoints=n)
        
        sys.stdout.close()
            
                     
