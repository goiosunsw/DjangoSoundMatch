import datetime

from django.utils import timezone
from django.test import TestCase
from .models import Experiment, SoundTriplet, Subject

# Create your tests here.

def create_experiment(name, nparams = 0):
    x = Experiment.objects.create(description=name, created_date=timezone.now())
    return x
    
    
def create_sound_triplet_for_subject(sub):
    now=timezone.now()
    s = sub.soundtriplet_set.create(shown_date=now, valid_date=now)
    experiment = sub.experiment
    return s
 
def create_subject_for_experiment(experiment):
    now=timezone.now()
    #sub = Subject.objects.create(start_date=now, finish_date=now)
    x = experiment.subject_set.create(start_date=now, finish_date=now)
    return x


# tests for a complete experiment scenario
class CompletScenarioTests(TestCase):
    def test_experiment_with_one_parameter(self):
        x = create_experiment('Experiment with single parameter')
        sub = create_subject_for_experiment(x)
        s = create_sound_triplet_for_subject(sub)
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
        x = create_experiment('Experiment for sound triplet')
        sub = create_subject_for_experiment(x)
        s = create_sound_triplet_for_subject(sub)
        s.valid_date=timezone.now()
        return True
