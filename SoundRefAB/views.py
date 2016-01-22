from django.shortcuts import get_object_or_404, render

from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static
from django.db.models import F

from random import shuffle
from decimal import Decimal
from datetime import timedelta
from numbers import Number
import os
import numpy as np
import tempfile


from .models import Subject,Experiment, Scenario, SoundTriplet, Page, ItemInScenario

import random

# module with sample generating functions
import sample_gen

# Helper functions
def store_sound_parameters(st, sound_data, param_list):
    for sound_nbr, data in enumerate(zip(sound_data,param_list)):
        sounddata, soundpar = data
        for parkey,parval in soundpar.items():
            if isinstance(parval, Number):
                parinst = st.parameterinstance_set.create(subject=st.subject)
            else:
                parinst = st.stringparameterinstance_set.create(subject=st.subject)
            parinst.name = parkey
            #parinst.description = par['description']
            parinst.value = parval
            parinst.position = sound_nbr

            parinst.save()

def retrieve_sound_parameters(st):
    confidence = st.confidence
    choice = st.choice
    par=[]
    # Unpack numeric parameters
    pset = st.parameterinstance_set.all().order_by('position')
    # and string parameters
    spset = st.stringparameterinstance_set.all().order_by('position')
    for pos in pset.values_list('position',flat=True).distinct():
        thisdict=dict()
        thispar = pset.filter(position=pos)
        for parinst in thispar:
            thisdict[parinst.name] = parinst.value
        thispar = spset.filter(position=pos)
        for parinst in thispar:
            thisdict[parinst.name] = parinst.value
        
        par.append(thisdict)

    return par, choice, confidence


# Create your views here.
class ExperimentListView(ListView):
    template_name='SoundRefAB/index.html'
    model = Experiment
    fields = ['description','date_created']


class ScenarioListView(ListView):
    template_name='SoundRefAB/index.html'
    model = Scenario
    fields = ['description','date_created']


class NewSubjectView(CreateView):
    template_name='SoundRefAB/subject_form.html'

    model = Subject
    fields = ['age_group','music_experience','hearing_prob','device']

    def get_success_url(self):
        return reverse('srefab:next', args = (self.object.pk,))

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.instance.scenario = Scenario.objects.get(pk=self.kwargs['pk'])
        form.instance.trials_done = 0
        form.instance.exp_id=0
        form.instance.save()
        #print pk
        #self.success_url=
        return super(CreateView, self).form_valid(form)

def NextExp(request, subject_id):
    
    this_subj = Subject.objects.get(pk=subject_id)
    ord_no = this_subj.exp_id + 1
    this_subj.exp_id = ord_no 
    
    this_scenario = this_subj.scenario
    n_exp = max(this_scenario.iteminscenario_set.values_list('order', flat=True))
    
    if ord_no <= n_exp:
        #next_exp = this_scenario.iteminscenario_set.get(order=ord_no).experiment
        #exprevurl = next_exp.design
        exprevurl = this_scenario.iteminscenario_set.get(order=ord_no).get_url_for_subject_id(subject_id)
        #return reverse('srefab:'+exprevurl, args = (self.object.pk,))
        # reset number of trials
        this_subj.trials_done = 0
        this_subj.save()
        
        return HttpResponseRedirect(exprevurl)
        
    else:
        this_subj.save()
         
        return HttpResponseRedirect(reverse('srefab:thanks', args=(subject_id,)))
        

def SoundPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object


        # retrieve data from previous experiment
        try:
            valid_prev_st = sub.soundtriplet_set.filter(experiment_id=x.id, valid_date__gt=F('shown_date')+timedelta(seconds=2))
            old_st = valid_prev_st.latest('id')
            print 'Using data from previous trial no. %d'%(old_st.id)
            print 'Number of parameter items in it: %d'%(len(old_st.parameterinstance_set.all()))
            prev_param, prev_choice, prev_confidence = retrieve_sound_parameters(old_st)
            confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
        except SoundTriplet.DoesNotExist:
            prev_param=[]
            prev_choice=0
            prev_confidence=0
            confidence_history = []

        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub, experiment_id = x.id)
        
        st.trial = sub.trials_done + 1
        st.save()


        function_name = x.function
        try:
            f = getattr(sample_gen, function_name)
        except AttributeError:
            raise Http404("Error in sample generating function name: "+function_name)

        sound_data, param_dict, difficulty_divider = f(subject_id, prev_param=prev_param,
                                   prev_choice=prev_choice, confidence_history=confidence_history,
                                   difficulty_divider = float(sub.difficulty_divider),
                                   path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

        #store sound data in db
        store_sound_parameters(st, sound_data, param_dict)
        sub.difficulty_divider=difficulty_divider
        sub.save()

        # anti-caching
        for s in sound_data:
            s['file']+='?v=%06d'%st.trial

        #parameter_vals.append(par.value)
        #parameter_list = zip(parameter_names,parameter_vals)
        context = RequestContext(request, {
            'sound_list': sound_data,
            'subject_id': subject_id,
            'trial_id': st.trial,
            'sample_id': st.pk,
            'n_trials': x.number_of_trials,
            'difficulty': sub.difficulty_divider
            }
        )



        template = loader.get_template('SoundRefAB/trial.html')
        return HttpResponse(template.render(context))

    except (KeyError):
        raise Http404("Error in subject or experiment data")
    # generate parameters

def ProcessPage(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
    st.choice = int(request.POST['choice'])
    st.confidence = int(request.POST['slider'])
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.trials_done += 1
    
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    

    sub.save()
    
    #WRONG: trials is now total in scenario...
    if sub.trials_done >= x.number_of_trials:
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))


##############
# Text / Sound demo page

def TextPage(request, subject_id, page_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    pag = get_object_or_404(Page, pk=page_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)


        template = loader.get_template('SoundRefAB/'+pag.template)
        context = RequestContext(request, {
            'subject_id': subject_id
            }
        )
        
        return HttpResponse(template.render(context))

    except (KeyError):
        raise Http404("Error fetching info page")
    # generate parameters





def SoundAdjustPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object

        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub, experiment_id = x.id)
        st.trial = sub.trials_done + 1
        st.save()
        
    except (KeyError):
        raise Http404("Error in subject or experiment data")
    

    # retrieve data from previous experiment
    try:
        print 'Using data from previous trial'
        valid_prev_st = sub.soundtriplet_set.filter(experiment_id=x.id, valid_date__gt=F('shown_date')+timedelta(seconds=2))
        old_st = valid_prev_st.latest('id')
        #print old_st
        dummy, prev_choice, prev_confidence = retrieve_sound_parameters(old_st)
        confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
    except SoundTriplet.DoesNotExist:
        print 'Initialising experiment data...'
        
        prev_choice=1
        prev_confidence=0
        confidence_history = []

    prev_param = [{'ampl':0.5},{'ampl':0.5}]
    ntrials = x.number_of_trials
    function_name = x.function
    try:
        f = getattr(sample_gen, function_name)
    except AttributeError:
        raise Http404("Error in sample generating function name: "+function_name)

    sound_data, param_dict, difficulty_divider = f(subject_id, ntrials = ntrials, prev_param= prev_param,
                               prev_choice=prev_choice, confidence_history=confidence_history,
                               difficulty_divider = float(sub.difficulty_divider),
                               path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

    #store sound data in db        
    print "sound generated"
    print param_dict

    store_sound_parameters(st, sound_data, param_dict)
    
    sub.difficulty_divider=difficulty_divider
    sub.save()

    #param_dict['trial_no']
    #parameter_vals.append(par.value)
    #parameter_list = zip(parameter_names,parameter_vals)
    context = RequestContext(request, {
        'param_list': param_dict,
        #'ampl_list': ampl_list,
        'subject_id': subject_id,
        'trial_id': st.trial,
        'sample_id': st.pk,
        'n_trials': x.number_of_trials,
        'difficulty': sub.difficulty_divider
        }
    )


    template = loader.get_template('SoundRefAB/trial_adjust.html')
    return HttpResponse(template.render(context))

    # generate parameters

def ProcessAdjustPage(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
    st.choice = 1
    st.value = float(request.POST['adjval'])
    st.confidence = int(request.POST['confidence'])
    #ampl_list=request.POST['ampl_list']
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.trials_done += 1
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    # need to store adjusted value
    adjparinst = st.parameterinstance_set.get(name='ampl', position=1)
    adjparinst.value = float(request.POST['adjval'])
    adjparinst.save()

    sub.save()

    if sub.trials_done >= x.number_of_trials:
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:soundadjustpage', args=(sub.pk,)))

class SubjectList(ListView):
    template_name='SoundRefAB/subjects.html'
    model = Subject
    fields = ['pk','start_date']

class SubjectDetail(DetailView):
    template_name='SoundRefAB/subject_detail.html'
    model = Subject
    #fields = ['pk','parameterlist']


def ThanksPage(request, subject_id):
    now = timezone.now()

    try:
        sub = get_object_or_404(Subject, pk=subject_id)

        # record finished date
        sub.finish_date = now
        sub.save()

        # get experiment for subject
        #ord_no = sub.exp_id 
        #x = sub.scenario.iteminscenario_set.get(order=ord_no).experiment
        
        context = RequestContext(request, {
            'exp_name': sub.scenario.description,
            'trials_done': sub.trials_done
        })


        template = loader.get_template('SoundRefAB/thanks.html')
        return HttpResponse(template.render(context))
    except (KeyError):
        raise Http404("Error in subject or experiment data")
