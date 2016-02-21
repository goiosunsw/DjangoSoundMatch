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
        base_path = os.path.join(settings.STATIC_ROOT,'SoundRefAB','static','SoundRefAB')
        sys.stdout = open(os.path.join(base_path,'slopeAmps.js'),'w')
        
        nharm=6
        
        sh = vo.SlopeHarmonicScaler(nharm=nharm)
        sh.outputJSArray()
            
                     
