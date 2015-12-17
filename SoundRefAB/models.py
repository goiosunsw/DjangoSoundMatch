import datetime

from django.db import models
from django.utils import timezone

# Create your models here.



class Experiment(models.Model):
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    #module = models.CharField('Python module',max_length=100)
    try:
        import types
        import sample_gen as sg
        fnames = [sg.__dict__.get(a).func_name for a in dir(sg) if isinstance(sg.__dict__.get(a), types.FunctionType)]
        function = models.CharField('Sound generating function',max_length=100, choices = [(fn,fn) for fn in fnames])
    except ImportError:
        function = models.CharField('Sound generating function',max_length=100)
        
    number_of_trials = models.IntegerField('Number of Trials',default=1)
    # change here when a new design is to be introduced
    design = models.CharField('Design class',         
        max_length=100, choices = (
            ('soundpage','Reference presented with N sounds, single choice'),
            ('soundadjustpage','Reference presented with single adjustable sound'), 
            ), default='Reference-A-B'
    )
    #fixed_params = models.ForeignKey(FixedParameter) 
    #variable_params = models.ForeignKey(VariableParameter) 
        
    def __str__(self):
        return self.description

class Scenario(models.Model):
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    #module = models.CharField('Python module',max_length=100)
    experiments = models.ManyToManyField(Experiment, through='ExperimentInScenario')

    

    def __str__(self):
        return self.description
    
class ExperimentInScenario(models.Model):
    experiment = models.ForeignKey(Experiment)
    scenario = models.ForeignKey(Scenario)
    order = models.IntegerField('Order in Scenario', default=1)
    
    def __str__(self):
        return '%s : Nbr %d in %s'%(self.experiment.description, self.order, self.scenario.description)

    
class Subject(models.Model):
    start_date = models.DateTimeField('date Started',auto_now_add=True)
    finish_date = models.DateTimeField('date Finished',auto_now_add=True)
    age_group = models.CharField('What is your age group?', 
        max_length=2, choices = (
            ('15','under 15'),
            ('25','15-25'),
            ('35','25-35'),
            ('45','35-45'),
            ('55','55-65'),
            ('65','65-75'),
            ('75','75 or more'), ), default='25'
    )
    music_experience = models.CharField('Which better describes your musical experience?',
        max_length=2, choices = (
            ('NO','No experience'),
            ('AM','Amateur'),
            ('ST','Music student, less than 8 years'),
            ('AD','Music student, more than 8 years'),
            ('RG','Non-professional but perform in public'),
            ('PR','Professional'), ), default='NO'
    )
    hearing_prob = models.BooleanField('Do you experience hearing loss?', default=False)
    device = models.CharField('How are you listening to the sounds in this test?'
        ,max_length=2, choices = (
            ('CO','Computer loudspeakers'),
            ('LA','Laptop loudspeakers'),
            ('PD','Phone or tablet loudspeakers'),
            ('EX','External amplified loudspeakers'),
            ('PH','Headphones'), ) , default = 'PH'
    )
    scenario = models.ForeignKey(Scenario)
    exp_id = models.IntegerField(default=0)
    trials_done = models.IntegerField(default=0)
    stop_experiment = models.BooleanField(default=False)
    difficulty_divider = models.DecimalField(default=1.0,max_digits=10,decimal_places=2)

class SoundTriplet(models.Model):
    #var_params = models.ForeignModel(ParameterInstance)
    shown_date = models.DateTimeField('date triplet shown to user',auto_now_add=True)
    valid_date = models.DateTimeField('date triplet validated by user',auto_now_add=True)
    confidence = models.IntegerField(default=0)
    subject = models.ForeignKey(Subject)
    # number of trial for the subject and experiment
    trial = models.IntegerField(default=0)
    experiment = models.ForeignKey(Experiment)
    # chosen instance
    choice = models.IntegerField(default=0)
        
    def __str__(self):
        return '%d'%self.id
    def was_completed(self):
        timediff = self.valid_date - self.shown_date
        if timediff.total_seconds() > 1:
            return True
        else:
            return False


class ParameterInstance(models.Model):
    # holds the actual value of a parameter
    # a parameter instance or value belongs to a particular experiment
    # and a particular parameter model
    name = models.CharField(max_length=100, default = '')
    value = models.DecimalField('Value', max_digits=10, decimal_places=2, default=0.0)
    subject = models.ForeignKey(Subject)
    trial = models.ForeignKey(SoundTriplet)
    position = models.IntegerField(default=0)
    
    def __str__(self):
        return self.par_model.description+' in experiment '+self.subject.experiment.description+'(trial %d)'%self.pk


   