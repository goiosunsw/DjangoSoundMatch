import datetime

from django.db import models
from django.utils import timezone

# generic relations for item sequence
from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.conf import settings
from django.core.urlresolvers import reverse


import os
import string
MODEL_ROOT = os.path.dirname(os.path.realpath(__file__))



class Experiment(models.Model): 
    '''Holds information for a particular experiment, 
    based on a design given by the parameter "design" and a
    particular instance of the design given by "generating function"'''
    
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    instruction_text = models.CharField(max_length=1000, default='Please pick a sound')
    #module = models.CharField('Python module',max_length=100)
    item = GenericRelation('ItemInScenario')
    try:
        import types
        import sample_gen as sg
        fnames = [sg.__dict__.get(a).func_name for a in dir(sg) if isinstance(sg.__dict__.get(a), types.FunctionType)]
        function = models.CharField('Sound generating function',max_length=100, choices = [(fn,fn) for fn in fnames])
    except ImportError:
        function = models.CharField('Sound generating function',max_length=100)
        
    number_of_trials = models.IntegerField('Number of Trials',default=1)
    total_completed_trials = models.IntegerField('Totla number of completed trials',default=0)
    total_completed_runs = models.IntegerField('Totla number of completed runs',default=0)
    # change here when a new design is to be introduced
    design = models.CharField('Design class',         
        max_length=100, choices = (
            ('soundpage','Reference presented with N sounds, single choice'),
            ('soundadjustpage','Reference presented with single adjustable sound'),
            ('intropage', 'Intro page collecting confidence and comment'),
            ), default='soundpage'
    )
    #fixed_params = models.ForeignKey(FixedParameter) 
    #variable_params = models.ForeignKey(VariableParameter) 
    
    def get_url_for_subject_id(self, subject_pk):
        '''Return the url for this page, for subject referred to by "subject id"'''
        return reverse('srefab:'+self.design, args=(subject_pk,))
    
    def get_all_trial_data(self, subject_pk):
        stnum = 0
        parnum = 0
        allpar = []
        allst = self.soundtriplet_set.filter(subject__id=subject_pk)
        for st in allst:
            trialpar = []
            samples = st.parameterinstance_set.values_list('position',flat=True).distinct()
            for sam in samples:
                stpar=dict()
                for par in st.parameterinstance_set.filter(position = sam):
                    stpar[par.name] = par.value
                    parnum += 1
                for par in st.stringparameterinstance_set.filter(position = sam):
                    stpar[par.name] = par.value
                    parnum += 1
                trialpar.append(stpar)
            stnum +=1
            allpar.append(trialpar)
        return allpar
    
    def __str__(self):
        return self.description

class Questionnaire(models.Model):
    '''Dummy model to link to the subject questionnaire'''
    item = GenericRelation('ItemInScenario')
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    
    def get_url_for_subject_id(self, subject_pk):
        '''Return the url for this page, for subject referred to by "subject id"'''
        return reverse('srefab:subjectupdate', args=(subject_pk,))

class Page(models.Model):
    '''Pages do not return information to the database, 
    they link to a template and show it to the user, 
    and then redirect to the next item on the scenario'''
    
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    #module = models.CharField('Python module',max_length=100)
    item = GenericRelation('ItemInScenario')
    try:
        from django.template.loaders.app_directories import get_app_template_dirs
        rawdirs = get_app_template_dirs(os.path.dirname(__file__))
        uniquedirs = list(set(rawdirs))
        app_template_dir = [ss for ss in uniquedirs if string.find(ss,MODEL_ROOT)>-1 ]
        template_files = []
        for template_dir in app_template_dir:
            for dir, dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    if (filename[0:2]=='pg') & (filename[-4:]=='html') :
                        template_files.append(filename)
        template = models.CharField('Page file',max_length=100, choices = [(fn,fn) for fn in template_files], default='')
    except ImportError:
        template = models.CharField('Page file',max_length=100, default='')
    
    def get_url_for_subject_id(self, subject_pk):
        '''Return the url for this page, for subject referred to by "subject id"'''
        return reverse('srefab:textpage', args=(subject_pk,self.pk,))
    
                
    def __str__(self):
        return self.description

class Scenario(models.Model):
    '''Scenarios hold a sequence of info pages, demo pages and/or experiments'''
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    #module = models.CharField('Python module',max_length=100)
    #items = models.ManyToManyField('ItemInScenario')
    
    def __str__(self):
        return '%d:%s'%(self.id,self.description)
    
# class ExperimentInScenario(models.Model):
#     experiment = models.ForeignKey(Experiment)
#     scenario = models.ForeignKey(Scenario)
#     order = models.IntegerField('Order in Scenario', default=1)
#
#     def __str__(self):
#         return '%s : Nbr %d in %s'%(self.experiment.description, self.order, self.scenario.description)
class ItemInScenario(models.Model):
    '''Abstraction to refer to a single page (info, experiment or questionnaire)'''
    
    appl = u'SoundRefAB'
    limit = (models.Q(app_label = appl, model = u'experiment') | 
            models.Q(app_label = appl, model = u'page') |
            models.Q(app_label = appl, model = u'questionnaire'))
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    scenario = models.ForeignKey('Scenario')
    #gen = models.
    # experiment = models.ForeignKey('Experiment',null=True)
    # page = models.ForeignKey('Page',null=True)
    # sound_demo = models.ForeignKey('SoundDemo',null=True)
    order = models.IntegerField('Order in Scenario', default=1)
    
    def get_url_for_subject_id(self, subject_pk):
        '''Return the url for this page, for subject referred to by "subject id"'''
        
        return self.content_object.get_url_for_subject_id(subject_pk)
    
    def __str__(self):
        ct = self.content_type.model
        return '%s (%s): Nbr %d in %s'%(self.content_object.description, ct, self.order, self.scenario.description)

    
class Subject(models.Model):
    '''Subject data'''
    start_date = models.DateTimeField('date Started',auto_now_add=True)
    finish_date = models.DateTimeField('date Finished',auto_now_add=True)
    age = models.IntegerField('How old are you?', default=20)
    music_experience = models.CharField('Which better describes your musical experience?',
        max_length=2, choices = (
            ('NO','No experience'),
            ('AM','Amateur'),
            ('ST','Music student'),
            ('RG','Non-professional but perform in public'),
            ('PR','Professional'), ), default='NO'
    )
    #hearing_prob = models.BooleanField('Do you experience hearing loss?', default=False)
    hearing_prob = models.CharField('Do you experience any hearing problems?'
        ,max_length=2, choices = (
            ('NH','I have normal hearing'),
            ('SL','I have slight hearing loss'),
            ('HL','I have considerable hearing loss'),
        ) , default = 'NH'
    )
    
    device = models.CharField('How are you listening to the sounds in this test?'
        ,max_length=2, choices = (
            ('CO','Computer loudspeakers'),
            ('LA','Laptop loudspeakers'),
            ('PD','Phone or tablet loudspeakers'),
            ('EX','External amplified loudspeakers'),
            ('PH','Headphones'), ) , default = 'PH'
    )
    final_comment = models.TextField('Any final comments about the experiment?', default='')
    scenario = models.ForeignKey(Scenario)
    exp_id = models.IntegerField(default=0)
    trials_done = models.IntegerField(default=0)
    total_trials  = models.IntegerField(default=0)
    stop_experiment = models.BooleanField(default=False)
    difficulty_divider = models.DecimalField(default=1.0,max_digits=10,decimal_places=2)
    instrument = models.CharField('Sing or play any instrument? Which?',max_length=100, default='')
    student_ID = models.CharField('Student ID',max_length=10, default='')
    loudspeaker_model = models.CharField('Model of headphones / speakers (if appliccable)',max_length=10, default='')
    vol_change = models.BooleanField('Did you adjust the volume during the experiment?',default=False)

class SoundTriplet(models.Model):
    '''Data corresponding to a single sample presented to the user'''
    #var_params = models.ForeignModel(ParameterInstance)
    shown_date = models.DateTimeField('date triplet shown to user',auto_now_add=True)
    valid_date = models.DateTimeField('date triplet validated by user',auto_now_add=True)
    confidence = models.IntegerField(default=0)
    subject = models.ForeignKey(Subject)
    playseq = models.SlugField(default='')
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
    '''Holds the actual value of a parameter
    a parameter instance or value belongs to a particular experiment
    and a particular parameter model'''
    name = models.CharField(max_length=100, default = '')
    value = models.DecimalField('Value', max_digits=10, decimal_places=2, default=0.0)
    subject = models.ForeignKey(Subject)
    trial = models.ForeignKey(SoundTriplet)
    position = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name+' in sample %d of trial %d '%(self.position,self.trial.pk)+' of exp. '+self.trial.experiment.description

class StringParameterInstance(models.Model):
    '''Holds the actual (string) value of a parameter
    a parameter instance or value belongs to a particular experiment
    and a particular parameter model'''
    name = models.CharField(max_length=100, default = '')
    value = models.CharField('Value', max_length=50, default = '')
    subject = models.ForeignKey(Subject)
    trial = models.ForeignKey(SoundTriplet)
    position = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name+' in sample %d of trial %d '%(self.position,self.trial.pk)+' of exp. '+self.trial.experiment.description

class ExperimentResults(models.Model):
    '''Holds some post-experiment results that may be useful for initialising further experiments'''
    name = models.CharField(max_length=100, default = '')
    value = models.DecimalField('Value', max_digits=10, decimal_places=2, default=0.0)
    subject = models.ForeignKey(Subject)
    experiment = models.ForeignKey(Experiment)

class Comment(models.Model):
    '''Holds a comment associated with an experimental trial'''
    text = models.TextField(default='')
    subject = models.ForeignKey(Subject)
    trial = models.ForeignKey(SoundTriplet)
    
    def __str__(self):
        return self.name+' in sample %d of trial %d '%(self.position,self.trial.pk)+' of exp. '+self.trial.experiment.description
   