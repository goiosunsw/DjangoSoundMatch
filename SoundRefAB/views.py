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
import os
import numpy as np
import tempfile


from .models import Subject,Experiment, Scenario, SoundTriplet

import random

# module with sample generating functions
import sample_gen

# Helper functions
def store_sound_parameters(st, sound_data, param_list):
    for sound_nbr, data in enumerate(zip(sound_data,param_list)):
        sounddata, soundpar = data
        for parkey,parval in soundpar.items():
            parinst = st.parameterinstance_set.create(subject=st.subject)
            parinst.name = parkey
            #parinst.description = par['description']
            parinst.value = parval
            parinst.position = sound_nbr

            parinst.save()

def retrieve_sound_parameters(st):
    confidence = st.confidence
    choice = st.choice
    par=[]
    for parinst in st.parameterinstance_set.all():
        sound_nbr = parinst.position
        par[sound_nbr]['name'] = parinst.name
        par[sound_nbr]['description'] = parinst.description
        par[sound_nbr]['value'] = parinst.value

    return par, choice, confidence

def store_temp_data_file(data, scenario_id=0, experiment_id=0, subject_id=0):
    filename=tempfile.gettempdir()+'scen%d_exp%d_subj%d_temp.npy'%(scenario_id,experiment_id,subject_id)
    np.save(filename,data)

def retrieve_temp_data_file(scenario_id=0, experiment_id=0, subject_id=0):
    filename=tempfile.gettempdir()+'scen%d_exp%d_subj%d_temp.npy'%(scenario_id,experiment_id,subject_id)
    data = np.load(filename)
    return data.tolist()

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
    this_subj.save()
    
    this_scenario = this_subj.scenario
    n_exp = max(this_scenario.experimentinscenario_set.values_list('order', flat=True))
    
    if ord_no <= n_exp:
        next_exp = this_scenario.experimentinscenario_set.get(order=ord_no).experiment
        exprevurl = next_exp.design
        #return reverse('srefab:'+exprevurl, args = (self.object.pk,))
        return HttpResponseRedirect(reverse('srefab:'+exprevurl, args = (subject_id,)))
    else: 
        return HttpResponseRedirect(reverse('srefab:thanks', args=(subject_id,)))
        

def SoundPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.experimentinscenario_set.get(order=ord_no).experiment

        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub)
        st.trial = sub.trials_done + 1
        st.save()

        # retrieve data from previous experiment
        try:
            old_st = sub.soundtriplet_set.latest('id')
            prev_param, prev_choice, prev_confidence = retrieve_sound_parameters(old_st)
            confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
        except SoundTriplet.DoesNotExist:
            prev_param=[]
            prev_choice=0
            prev_confidence=0



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
    x = sub.scenario.experimentinscenario_set.get(order=ord_no).experiment
    

    sub.save()

    if sub.trials_done >= x.number_of_trials:
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))


def SoundAdjustPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.experimentinscenario_set.get(order=ord_no).experiment

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
        prev_param = retrieve_temp_data_file(scenario_id=sub.scenario.id, 
                                         experiment_id=x.id,
                                         subject_id=sub.pk)
        confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
    except SoundTriplet.DoesNotExist:
        print 'Initialising experiment data...'
        
        ntrials = x.number_of_trials
        ampl_list = np.logspace(-1.3,-0.3,ntrials)
        random.shuffle(ampl_list)
        prev_param = {'ampl':0.5,
                     'nharm':15,
                     'slope':20,
                     'dur':0.6,
                     'freq': 500,
                     'ampl_list': ampl_list,
                     'trial_no':0}
        prev_choice=0
        prev_confidence=0
        confidence_history = []



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
    print "sound generated"
    print param_dict

    #store_sound_parameters(st, sound_data, param_dict)
    store_temp_data_file(param_dict, scenario_id=sub.scenario.id, 
                                     experiment_id=x.id,
                                     subject_id=sub.pk)
    
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
    x = sub.scenario.experimentinscenario_set.get(order=ord_no).experiment

    sub.save()

    if sub.trials_done >= x.number_of_trials:
        return HttpResponseRedirect(reverse('srefab:thanks', args=(st.subject.pk,)))
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
        ord_no = sub.exp_id 
        x = sub.scenario.experimentinscenario_set.get(order=ord_no).experiment
        
        context = RequestContext(request, {
            'exp_name': x.description,
            'trials_done': sub.trials_done
        })


        template = loader.get_template('SoundRefAB/thanks.html')
        return HttpResponse(template.render(context))
    except (KeyError):
        raise Http404("Error in subject or experiment data")
