from django.db import models

import SoundRefAB.models

# Create your models here.
class SoundSet(models.Model):
    #var_params = models.ForeignModel(ParameterInstance)
    shown_date = models.DateTimeField('date set shown to user',auto_now_add=True)
    valid_date = models.DateTimeField('date set validated by user',auto_now_add=True)
    subject = models.ForeignKey(SoundRefAB.models.Subject)
    # number of trial for the subject
    trial = models.IntegerField(default=0)
    # chosen instance
    adj_val = models.IntegerField(default=0)
        
    def __str__(self):
        return '%d'%self.id

class ParameterInstance(models.Model):
    # holds the actual value of a parameter
    # a parameter instance or value belongs to a particular experiment
    # and a particular parameter model
    name = models.CharField(max_length=100, default = '')
    value = models.DecimalField('Value', max_digits=10, decimal_places=2, default=0.0)
    subject = models.ForeignKey(Subject)
    trial = models.ForeignKey(SoundSet)
    position = models.IntegerField(default=0)
    
    def __str__(self):
        return self.par_model.description+' in experiment '+self.subject.experiment.description+'(trial %d)'%self.pk

