from django.core.management.base import BaseCommand
from SoundRefAB.models import Experiment, Page, Scenario, ItemInScenario, Questionnaire
from django.contrib.contenttypes.models import ContentType
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Build one test scenario per experiment in database'

    def handle(self, *args, **options):
        
        thismodel = Experiment
        count = 0
        for x in thismodel.objects.all():
            # Create the scenario
            ss = Scenario(description= 'Test scenario for '+x.description,
                          created_date = datetime.datetime.now())
            ss.save()
        
            # link model to scenario
            ll = ItemInScenario(content_type=ContentType.objects.get_for_model(thismodel), 
                                object_id=x.id,
                                order=count+1,
                                scenario=ss)
            ll.save()
            ss.save()
        

            
                     
