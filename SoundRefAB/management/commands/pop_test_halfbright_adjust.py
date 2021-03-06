from django.core.management.base import BaseCommand
from SoundRefAB.models import Experiment, Page, Scenario, ItemInScenario, Questionnaire
from django.contrib.contenttypes.models import ContentType
from django.db import models

import datetime
import sys
#import pdb; pdb.set_trace()

class Command(BaseCommand):
    args = ''
    help = 'Build scenario for a single brightness experiment'

    def handle(self, *args, **options):
        # Create the scenario
        ss = Scenario(description= 'Half-bright exp. test '+ str(datetime.datetime.now()),
                      created_date = datetime.datetime.now())
        ss.save()
        
        # Create all the info pages
        
        itemdata = ({'model': Page,
                     'description': 'Pre-questionnaire page',
                     'template': 'pg_halfbright_intro.html'},
                    {'model': Experiment,
                      'description': 'Half-Brightness adjust experiment',
                      'instruction_text': 'Adjust tone 2 so that it sounds <span style="color:red; font-weight:bold">half as bright</span> as tone 1',
                      'design': 'soundadjustpage',
                      'function': 'HalfBrightAdjust',
                       'number_of_trials': 5},)
                     
        count = 0
        for itd in itemdata:
            # create db object
            thismodel = itd['model']
            if thismodel == 'Repeat':
                # find an item whose description is the same as the respeat one
                thisdesc = itd['description']
                itref=None
                for itd2 in itemdata:
                    if ((itd2['description'] == thisdesc) and (itd2['model'] != 'Repeat')):
                        itref = itd2
                        content = ContentType.objects.get_for_model(itref['model'])
                        ii = content.get_object_for_this_type(description = itd['description'])
                        sys.stderr.write('Repeating model "%s" %d times\n'%(thisdesc,itd['number']))
                        for nn in xrange(itd['number']):
                            ll = ItemInScenario(content_type=ContentType.objects.get_for_model(itref['model']), 
                                                object_id=ii.id,
                                                order=count+1,
                                                scenario=ss)
                            ll.save()
                            count += 1
                    
                    else:
                        print itd2
                        #sys.stderr.write('%s is not %s in model %s\n'%(thisdesc,itd2['description'],itd2['model']))
                        
                if itref is None:
                    
                    sys.stderr.write('Repeated model %s not found!\n'%thisdesc)
            else:
                thisdesc = itd['description']
                itcopy = itd.copy()
                del itcopy['model']
                # check if description already exists
                try:
                    thismodel.objects.get(description=itcopy['description'])
                    itcopy['description'] += '%d'%ss.id
                    itd['description'] += '%d'%ss.id
                    sys.stderr.write('model name updated to %s\n'%itd['description'])

                    # update names in repeat models
                    for itd2 in itemdata:
                        if (itd2['model'] == 'Repeat' and itd2['description'] == thisdesc):
                            itd2['description'] = itcopy['description']
                            sys.stderr.write('repeat model updated to %s\n'%itd['description'])

 
                except thismodel.DoesNotExist:
                    pass
                finally:
                    ii = thismodel(created_date = datetime.datetime.now(), **itcopy)
                    ii.save()
                    # link model to scenario
                    ll = ItemInScenario(content_type=ContentType.objects.get_for_model(thismodel), 
                                        object_id=ii.id,
                                        order=count+1,
                                        scenario=ss)
                    ll.save()
                    count += 1
        
        ss.save()

            
                     
