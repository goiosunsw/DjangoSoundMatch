from django.core.management.base import BaseCommand
from SoundRefAB.models import Experiment, Page, Scenario, ItemInScenario, Questionnaire
from django.contrib.contenttypes.models import ContentType
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Build databases for the experimental setup used in 2015 UNSW experiment'

    def handle(self, *args, **options):
        # Create the scenario
        ss = Scenario(description= 'UNSW 2016 vibrato perception experiment',
                      created_date = datetime.datetime.now())
        ss.save()
        
        # Create all the info pages
        
        itemdata = ({'model': Page,
                     'description': 'Welcome page',
                     'template': 'pg_welcome.html'},
                    {'model': Page,
                     'description': 'Loudness adjusting explanation',
                     'template': 'pg_loudness_adj_intro.html'},
                    {'model': Experiment,
                     'instruction_text': 'Adjust the second sound so that it sounds twice as loud as the first',
                      'description': 'Loudness adjust experiment',
                      'design': 'soundadjustpage',
                      'function': 'LoudnessAdjust',
                      'number_of_trials': 5},
                    {'model': Page,
                     'description': 'Brightness adjusting explanation',
                     'template': 'pg_brightness_adj_intro.html'},
                    {'model': Experiment,
                     'description': 'Brightness adjust experiment',
                     'instruction_text': 'Adjust the second sound so that it sounds twice as bright as the first',
                     'design': 'soundadjustpage',
                     'function': 'BrightnessAdjust',
                      'number_of_trials': 5},
                    {'model': Page,
                     'description': 'Vibrato matching explanation',
                     'template': 'pg_vibrato_intro.html'},
                    {'model': Experiment,
                     'description': 'Vibrato matching experiment',
                     'instruction_text': 'Which sample sounds closer to the reference?',
                     'design': 'soundpage',
                     'function': 'SlopeVibratoTripletRefAB',
                      'number_of_trials': 5},
                    {'model': Page,
                     'description': 'Pre-questionnaire page',
                     'template': 'pg_quest_info.html'},
                    {'model': Questionnaire,
                     'description': 'Subject questionnaire'},
                    {'model': Page,
                     'description': 'Thanks page',
                     'template': 'pg_thanks.html'})
        for count, itd in enumerate(itemdata):
            # create db object
            thismodel = itd['model']
            del itd['model']
            ii = thismodel(created_date = datetime.datetime.now(), **itd)
            ii.save()
            # link model to scenario
            ll = ItemInScenario(content_type=ContentType.objects.get_for_model(thismodel), 
                                object_id=ii.id,
                                order=count+1,
                                scenario=ss)
            ll.save()
        
        ss.save()

            
                     
