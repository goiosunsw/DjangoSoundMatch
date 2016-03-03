from django.core.management.base import BaseCommand
from SoundRefAB.models import Comment, Experiment, Page, Scenario, ItemInScenario, Questionnaire
from django.contrib.contenttypes.models import ContentType
import datetime

class Command(BaseCommand):
    args = ''
    help = ''
    def handle(self, *args, **options):
        default_date = datetime.date(day=01,month=01,year=2016)
        new_question_date = datetime.datetime(day=01,month=03,year=2016,hour=14,minute=30)
        comment_labels = ('comment','comment1','comment2','comment2')
        after_change_date = (-1, -1, 0, 1)
        questions = ('Please leave any comments about the nature of the fluctuations in the tones that you heard',
                'What do you think was the aim of this study?',
                'In you own words how would you define "regular fluctuations" as used in this study',
                'In you own words how would you define "fluctuations" as used in this study (feel free to answer in one or two words)')
        s=Scenario.objects.get(description__contains='UNSW')
        x=Experiment.objects.get(description__contains='impressions')
        for label,acd,question in zip(comment_labels,after_change_date,questions):
            print question
            print '-------------------------'
            if acd==1:
                qs=Comment.objects.filter(label=label,trial__experiment=x,trial__shown_date__gt=new_question_date)
            if acd==0:
                qs=Comment.objects.filter(label=label,trial__experiment=x,trial__shown_date__lt=new_question_date)
            if acd==-1:
                qs=Comment.objects.filter(label=label,trial__experiment=x)
            for comment in qs:
                print '* '+str(comment.trial.subject_id)+': '+comment.text
            print '.'
            print '.'


            


       

            
                     
