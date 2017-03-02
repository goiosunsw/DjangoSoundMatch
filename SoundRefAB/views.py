from django.shortcuts import get_object_or_404, render

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static
from django.db.models import F
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.contenttypes.models import ContentType

#from django.core.exceptions import DoesNotExist

from random import shuffle
from decimal import Decimal
from datetime import timedelta, datetime
from numbers import Number
import os
import numpy as np
import tempfile
import sys


from .models import Subject,Experiment, Scenario, SoundTriplet, Page, ItemInScenario, ParameterInstance, Comment

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
		parval = float(parval)
            else:
                parinst = st.stringparameterinstance_set.create(subject=st.subject)
            parinst.name = parkey
            #parinst.description = par['description']
            parinst.value = parval
            parinst.position = sound_nbr

            parinst.save()
    st.save()

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

def retrieve_all_prev_parameters(exp, subj):
    
    confidence=[]
    choice=[]
    allpar=[]
    
    for st in subj.soundtriplet_set.filter(experiment=exp):
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
            
        if par:
            allpar.append(par)
            confidence.append(st.confidence)
            choice.append(st.choice)
            
            
    return allpar, choice, confidence


def store_experiment_results(result_dict, exp, subj):
    sys.stderr.write('Storing results for experiment "'+exp.description+'", subject no.'+str(subj.id)+'\n')
    for name, value in result_dict.items():
        if isinstance(value, Number):
            expresult = exp.experimentresults_set.create(subject=subj)
            expresult.name = name
            #parinst.description = par['description']
            expresult.value = value

            expresult.save()

def get_experiment_results(subj):
    erd = dict()
    for er in subj.experimentresults_set.all():
        erd[er.name] = er.value
    
    return erd

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Create your views here.
class ExperimentListView(ListView):
    template_name='SoundRefAB/index.html'
    model = Experiment
    fields = ['description','date_created']


class ScenarioListView(ListView):
    template_name='SoundRefAB/index.html'
    model = Scenario
    fields = ['description','date_created']

def  NewSubjectView(request, pk=0):
    scen = Scenario.objects.get(pk=pk)
    ip = get_client_ip(request)
    sub = scen.subject_set.create(trials_done=0, exp_id=0, ip=ip)
    subject_id = sub.id
    
    return HttpResponseRedirect(reverse('srefab:next', args = (subject_id,)))

def  MainView(request, pk=0):
    scen = Scenario.objects.filter(description__contains='UNSW').last()
    return HttpResponseRedirect(reverse('srefab:new', args = (scen.id,)))
    #return HttpResponseRedirect(reverse('srefab:list'))

    
class SubjectQuestionnaireUpdate(UpdateView):
    template_name='SoundRefAB/subject_form.html'

    model = Subject
    #fields = ['age','music_experience','hearing_prob','device','loudspeaker_model','vol_change','instrument','student_ID','final_comment']
    fields = ['age','music_experience','hearing_prob','vol_change','instrument','student_ID','final_comment']

    def get_success_url(self):
        return reverse('srefab:next', args = (self.object.pk,))

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        #form.instance.scenario = Scenario.objects.get(pk=self.kwargs['pk'])
        #form.instance.trials_done = 0
        #form.instance.exp_id=0
        #form.instance.save()
        #print pk
        #self.success_url=
        return super(UpdateView, self).form_valid(form)
    
class SubjectQuestionnaire(CreateView):
    template_name='SoundRefAB/subject_form.html'

    model = Subject
    fields = ['age','music_experience','hearing_prob','device','instrument','student_ID','comment']

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
    
    sys.stderr.write('Redirecting to experiment %d of %d\n'%(ord_no,n_exp))
    
    if ord_no <= n_exp:
        #next_exp = this_scenario.iteminscenario_set.get(order=ord_no).experiment
        #exprevurl = next_exp.design
        exprevurl = this_scenario.iteminscenario_set.get(order=ord_no).get_url_for_subject_id(subject_id)
        #return reverse('srefab:'+exprevurl, args = (self.object.pk,))
        # reset number of trials
        this_subj.trials_done = 0
        
        
        if ord_no == n_exp:
            now = timezone.now()

            # record finished date
            this_subj.finish_date = now

        this_subj.save()
            
        return HttpResponseRedirect(exprevurl)
        
    else:
        this_subj.save()
         
        #return HttpResponseRedirect(reverse('srefab:list', args=(subject_id,)))
        return HttpResponseRedirect(reverse('srefab:main'))
        

def SoundPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
        #sys.stderr.write('Here\n')
        
        #number of runs: how many times does this experiment appear in scenario
        x_content_type = ContentType.objects.get_for_model(x)
        # number of runs of the experiment is the number
        # of times the same experiment appears in the scenario
        n_runs = sub.scenario.iteminscenario_set.filter(content_type__pk=x_content_type.id,object_id=x.id).count()
        qq=sub.scenario.iteminscenario_set.filter(content_type__pk=x_content_type.id,object_id=x.id).order_by('order')
        all_order_nos = qq.values_list('order',flat=True)
        first_order_no = min(all_order_nos)

        function_name = x.function
        
        
        # retrieve data from previous experiment
        try:
            if not this_subj.trials_done:
                raise SoundTriplet.DoesNotExist
            
            valid_prev_st = sub.soundtriplet_set.filter(experiment_id=x.id, valid_date__gt=F('shown_date')+timedelta(seconds=2))
            old_st = valid_prev_st.latest('id')
            sys.stderr.write('Using data from previous trial no. %d\n'%(old_st.id))
            sys.stderr.write('Number of parameter items in it: %d\n'%(len(old_st.parameterinstance_set.all())))
            prev_param, prev_choice, confidence_history = retrieve_all_prev_parameters(x,sub)
            #confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
        except SoundTriplet.DoesNotExist:
            prev_param=[]
            prev_choice=0
            prev_confidence=0
            confidence_history = []
            # initialise data for series of runs
            try:
                if ord_no == first_order_no:
                    init_function_name = function_name + '_init'
                    f = getattr(sample_gen, init_function_name)
                    f(subject_id, n_runs=n_runs)
            except AttributeError:
                pass

        
        # if 'trial_no' not in prev_param[-1][0].keys():
        #     prev_param[-1][0]['trial_no'] = sub.trials_done
            
        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub, experiment_id = x.id)
        
        st.trial = sub.trials_done + 1
        st.save()


        try:
            f = getattr(sample_gen, function_name)
        except AttributeError:
            raise Http404("Error in sample generating function name: "+function_name)
        
        prev_exp = get_experiment_results(this_subj)
        
        sound_data, param_dict, difficulty_divider = f(subject_id, prev_param=prev_param,
                                   prev_choice=prev_choice, confidence_history=confidence_history,
                                   difficulty_divider = float(sub.difficulty_divider),
                                   path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL,
                                   prev_exp_dict=prev_exp)

        #store sound data in db
        store_sound_parameters(st, sound_data, param_dict)
        sub.difficulty_divider=difficulty_divider
        sub.save()

        # anti-caching
        v_num = sub.total_trials
        for s in sound_data:
            s['file']+='?v=%06d'%v_num

        #parameter_vals.append(par.value)
        #parameter_list = zip(parameter_names,parameter_vals)
        context = RequestContext(request, {
            'instruction_text': x.instruction_text,
            'param_list': param_dict,
            'sound_list': sound_data,
            'progress': sub.get_progress(),
            'subject_id': subject_id,
            'trial_id': st.trial,
            'sample_id': st.pk,
            'n_trials': x.number_of_trials,
            'difficulty': sub.difficulty_divider
            }
        )



        template = loader.get_template('SoundRefAB/trial.html')
        return HttpResponse(template.render(context))

    except (KeyError) as e:
        #exargs = ', '.join([str(ii) for ii in e.args])
        #raise Http404("Error in subject or experiment data\n"+e.__str__()+"\n"+exargs)
        raise
    # generate parameters

def ProcessPage(request, trial_id):
    #print request.POST
    stop = False
    st = get_object_or_404(SoundTriplet, pk=trial_id)
    st.choice = int(request.POST['choice'])
    st.confidence = int(request.POST['confidence'])
    playseq = request.POST.get('playseq','')
    if len(playseq)<500:
        st.playseq = playseq
    else:
        st.playseq = playseq[:240]+'...'+playseq[-240:]
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.one_more_trial()
    
    comment_labels = [lab for lab in request.POST.keys() if 'comment' in lab]
    for lab in comment_labels:
        c = request.POST.get(lab,'')
        if len(c)>0:
            st.comment_set.create(text=c, subject = sub)
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    
    try:
        stop_confidence = st.parameterinstance_set.get(name='stop_conf', position=0).value
        if st.confidence < stop_confidence:
            sys.stderr.write('This confidence %d smaller than %d. Stoping!\n'%(st.confidence,stop_confidence))
            stop = True
    except (KeyError, ParameterInstance.DoesNotExist) as e:
        pass

    sub.save()
    
    #WRONG: trials is now total in scenario...
    if sub.trials_done >= x.number_of_trials or stop:
        return HttpResponseRedirect(reverse('srefab:next', args=(sub.pk,)))
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
    

    # retrieve data from previous trials
    try:
        sys.stderr.write('Using data from previous trial\n')
        valid_prev_st = sub.soundtriplet_set.filter(experiment_id=x.id, valid_date__gt=F('shown_date')+timedelta(seconds=2))
        old_st = valid_prev_st.latest('id')
        #print old_st
        dummy, prev_choice, prev_confidence = retrieve_sound_parameters(old_st)
        #confidence_history = sub.soundtriplet_set.order_by('id').values_list('confidence',flat=True)
        prev_param, prev_choice, confidence_history = retrieve_all_prev_parameters(x,sub)
        
    except SoundTriplet.DoesNotExist:
        sys.stderr.write('Initialising experiment data...\n')
        
        prev_choice=1
        prev_confidence=0
        confidence_history = []

        prev_param = [[{'ampl':0.5},{'ampl':0.5}]]
        
    ntrials = x.number_of_trials
    function_name = x.function
    try:
        f = getattr(sample_gen, function_name)
    except AttributeError:
        raise Http404("Error in sample generating function name: "+function_name+'\n')

    sound_data, param_dict, difficulty_divider = f(subject_id, ntrials = ntrials, prev_param= prev_param,
                               prev_choice=prev_choice, confidence_history=confidence_history,
                               difficulty_divider = float(sub.difficulty_divider),
                               path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

    #store sound data in db        
    sys.stderr.write("sound generated. parameters:\n")
    smpl_no=0
    for sample_pdict in param_dict:
        for name,val in sample_pdict.items():
            sys.stderr.write(name+' '+str(smpl_no)+': '+str(val)+'\n')
        smpl_no += 1

    store_sound_parameters(st, sound_data, param_dict)
    
    sub.difficulty_divider=difficulty_divider
    sub.save()

    #param_dict['trial_no']
    #parameter_vals.append(par.value)
    #parameter_list = zip(parameter_names,parameter_vals)
    context = RequestContext(request, {
        'instruction_text': x.instruction_text,
        'param_list': param_dict,
        #'ampl_list': ampl_list,
        'progress': sub.get_progress(),
        'subject_id': subject_id,
        'trial_id': st.trial,
        'sample_id': st.pk,
        'n_trials': x.number_of_trials,
        'difficulty': sub.difficulty_divider
        }
    )


    template = loader.get_template('SoundRefAB/trial_adjust_lr.html')
    return HttpResponse(template.render(context))

    # generate parameters

def ProcessAdjustPage(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
    for name,val in request.POST.items():
        try:
            sys.stderr.write(name+': '+ str(val)+'\n')
        except MultiValueDictKeyError as e:
            sys.stderr.write(name+': '+ 'ERROR\n')
    st.choice = 1
    val = float(request.POST['adjval'])
    left= float(request.POST['left'])
    right= float(request.POST['right'])
    st.value = val
    st.confidence = int(request.POST['confidence'])
    playseq = request.POST.get('playseq','')
    if len(playseq)<500:
        st.playseq = playseq
    else:
        st.playseq = playseq[:240]+'...'+playseq[-240:]
    #ampl_list=request.POST['ampl_list']
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.one_more_trial()

    comment = request.POST.get('comment','')
    if len(comment)>0:
        st.comment_set.create(text=comment, subject = sub)
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    # need to store adjusted value
    adjparname = st.stringparameterinstance_set.get(name='adj_par_name', position=1).value
    sys.stderr.write("Adjusted parameter: "+adjparname+"\n")
    adjparinst = st.parameterinstance_set.get(name=adjparname, position=1)
    adjparinst.value = float(request.POST['adjval'])
    adjparinst.save()

    sub.save()

    if sub.trials_done >= x.number_of_trials:
        function_name = x.function
        try:
            f = getattr(sample_gen, function_name+'_process')
            result_dict = f(x.get_all_trial_data(subject_pk=sub.pk))
            store_experiment_results(result_dict, x, sub)
        except AttributeError:
            sys.stderr.write('No processing done\n')
        
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:soundadjustpage', args=(sub.pk,)))

def SoundIntro(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
        ntrials = x.number_of_trials

        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub, experiment_id = x.id)
        st.trial = sub.trials_done + 1
        st.save()
        
    except (KeyError):
        raise Http404("Error in subject or experiment data")
    

    sys.stderr.write('Initialising intro page data...\n')
    
    prev_choice=0
    prev_confidence=0
    confidence_history = []
        
    function_name = x.function
    try:
        f = getattr(sample_gen, function_name)
    except AttributeError:
        raise Http404("Error in sample generating function name: "+function_name+'\n')

    sound_data, param_dict, difficulty_divider = f(subject_id, ntrials = ntrials, prev_param= [],
                               prev_choice=prev_choice, confidence_history=confidence_history,
                               difficulty_divider = float(sub.difficulty_divider),
                               path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

    #store sound data in db        
    sys.stderr.write("sound generated. parameters:\n")
    smpl_no=0
    for sample_pdict in param_dict:
        for name,val in sample_pdict.items():
            sys.stderr.write(name+' '+str(smpl_no)+': '+str(val)+'\n')
        smpl_no += 1

    store_sound_parameters(st, sound_data, param_dict)
    
    sub.difficulty_divider=difficulty_divider
    sub.save()

    context = RequestContext(request, {
        'instruction_text': x.instruction_text,
        'param_list': param_dict,
        'trial_id': st.trial,
        'progress': sub.get_progress(),
        'sample_id': st.pk,
        'subject_id': subject_id,
        'n_trials': x.number_of_trials,
        'difficulty': sub.difficulty_divider
        }
    )
    
    template_name = param_dict[0]['html_template']

    template = loader.get_template('SoundRefAB/'+template_name)
    return HttpResponse(template.render(context))
    
def ProcessIntro(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
            
    # mandatory parameters
    st.choice = 0
    conf = request.POST.get('confidence','')
    try:
        st.confidence = int(conf)
    except ValueError:
        st.confidence = 0
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.one_more_trial()
    
    answer = request.POST.get('answer','')
    comment = request.POST.get('comment','')
    
    answerpar =  st.stringparameterinstance_set.create(subject=st.subject)
    answerpar.name = 'answer'
    #parinst.description = par['description']
    answerpar.value = answer
    answerpar.position = 0
    answerpar.save()
    
    if len(comment)>0:
        st.comment_set.create(text=comment, subject = sub)
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    sub.save()

    if sub.trials_done >= x.number_of_trials:
        function_name = x.function
        try:
            f = getattr(sample_gen, function_name+'_process')
            result_dict = f(x.get_all_trial_data(subject_pk=sub.pk))
            store_experiment_results(result_dict, x, sub)
        except AttributeError:
            sys.stderr.write('No processing done\n')
        
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:intropage', args=(sub.pk,)))
    
def CommentPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        this_subj = Subject.objects.get(pk=subject_id)
        ord_no = this_subj.exp_id 
        x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
        ntrials = x.number_of_trials

        # create sound_triplet to store in db
        st = SoundTriplet.objects.create(shown_date=now, valid_date=now, subject=sub, experiment_id = x.id)
        st.trial = sub.trials_done + 1
        st.save()
        
    except (KeyError):
        raise Http404("Error in subject or experiment data")
    

    function_name = x.function
    try:
        f = getattr(sample_gen, function_name)
    except AttributeError:
        raise Http404("Error in sample generating function name: "+function_name+'\n')

    sound_data, param_dict, difficulty_divider = f(subject_id, ntrials = ntrials, prev_param= [],
                               prev_choice=prev_choice, confidence_history=confidence_history,
                               difficulty_divider = float(sub.difficulty_divider),
                               path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

    sub.save()
    context = RequestContext(request, {
        'instruction_text': x.instruction_text,
        'param_list': param_dict,
        'trial_id': st.trial,
        'progress': sub.get_progress(),
        'subject_id': subject_id,
        'n_trials': x.number_of_trials,
        }
    )
    
    template_name = param_dict[0]['html_template']

    template = loader.get_template('SoundRefAB/'+template_name)
    return HttpResponse(template.render(context))
    
def ProcessComment(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
            
    # mandatory parameters
    st.choice = 0
    conf = request.POST.get('confidence','')
    try:
        st.confidence = int(conf)
    except ValueError:
        st.confidence = 0
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.one_more_trial()
    
    comment_labels = [lab for lab in request.POST.keys() if 'comment' in lab]
    for lab in comment_labels:
        sys.stderr.write('Found comment %s'%lab)
        c = request.POST.get(lab,'')
        if len(c)>0:
            st.comment_set.create(text=c, subject = sub, label = lab)
    
    
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    sub.save()

    if sub.trials_done >= x.number_of_trials:
        function_name = x.function
        try:
            f = getattr(sample_gen, function_name+'_process')
            result_dict = f(x.get_all_trial_data(subject_pk=sub.pk))
            store_experiment_results(result_dict, x, sub)
        except AttributeError:
            sys.stderr.write('No processing done\n')
        
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:intropage', args=(sub.pk,)))
    

class SubjectList(ListView):
    template_name='SoundRefAB/subjects.html'
    model = Subject
    fields = ['pk','start_date']

class SubjectDetail(DetailView):
    template_name='SoundRefAB/subject_detail.html'
    model = Subject
    #fields = ['pk','parameterlist']
    
class ScenarioResults(DetailView):
    template_name='SoundRefAB/scenario_results.html'
    model = Scenario
    #fields = ['pk','parameterlist']


def CommentList(request, pk):
    # get scenario
    s = get_object_or_404(Scenario, pk=pk)
    now = timezone.now()

    try:
        # get experiment list
        exp_list = s.unique_experiments()
        
        
        experiment_comments = []
        for x in exp_list:
            these_comments=[]
            comments = Comment.objects.filter(trial__experiment=x)
            for c in comments:
                these_comments.append({'subj_id': c.subject_id,
                                       'trial': c.trial.trial,
                                       'text': c.text})
            experiment_comments.append({'comments': these_comments,
                                        'experiment_title': x.description})
        
        final_comments = []
        new_question_date = datetime(day=01,month=03,year=2016,hour=14,minute=30)
        comment_labels = ('comment','comment1','comment2','comment2')
        after_change_date = (-1, -1, 0, 1)
        questions = ('Please leave any comments about the nature of the fluctuations in the tones that you heard',
                'What do you think was the aim of this study?',
                'In you own words how would you define "regular fluctuations" as used in this study',
                'In you own words how would you define "fluctuations" as used in this study (feel free to answer in one or two words)')
        
        try:
            x=Experiment.objects.get(description__contains='impressions')
            
            for label,acd,question in zip(comment_labels,after_change_date,questions):
                this_question = {'question': question}
                these_answers = []
                if acd==1:
                    qs=Comment.objects.filter(label=label,trial__experiment=x,trial__shown_date__gt=new_question_date)
                if acd==0:
                    qs=Comment.objects.filter(label=label,trial__experiment=x,trial__shown_date__lt=new_question_date)
                if acd==-1:
                    qs=Comment.objects.filter(label=label,trial__experiment=x)
                for comment in qs:
                    these_answers.append({'text': comment.text,
                                          'subj_id': comment.subject_id,
                                          })
                final_comments.append({'question': question, 'comments': these_answers})
        except Experiment.DoesNotExist:
            pass
        
        finals = []
        for sub in Subject.objects.all():
            if sub.final_comment:
                finals.append({'text': sub.final_comment,
                               'subj_id': sub.id})
            
        final_comments.append({'question': 'Final comments',
                               'comments': finals})




        context = RequestContext(request, {
            'experiment_comments': experiment_comments,
            'final_comments': final_comments,
            'scenario': s,
            }
        )
        
        template = loader.get_template('SoundRefAB/final_comments.html')
        return HttpResponse(template.render(context))
    except (KeyError):
        raise Http404("Error in subject or experiment data")
    


    context = RequestContext(request, {
        'instruction_text': x.instruction_text,
        'param_list': param_dict,
        'trial_id': st.trial,
        'progress': sub.get_progress(),
        'sample_id': st.pk,
        'subject_id': subject_id,
        'n_trials': x.number_of_trials,
        'difficulty': sub.difficulty_divider
        }
    )
    
    template_name = 'comment_list.html' 

    template = loader.get_template('SoundRefAB/'+template_name)
    return HttpResponse(template.render(context))
    
def ProcessIntro(request, trial_id):
    st = get_object_or_404(SoundTriplet, pk=trial_id)
            
    # mandatory parameters
    st.choice = 0
    conf = request.POST.get('confidence','')
    try:
        st.confidence = int(conf)
    except ValueError:
        st.confidence = 0
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.one_more_trial()
    
    answer = request.POST.get('answer','')
    comment = request.POST.get('comment','')
    
    answerpar =  st.stringparameterinstance_set.create(subject=st.subject)
    answerpar.name = 'answer'
    #parinst.description = par['description']
    answerpar.value = answer
    answerpar.position = 0
    answerpar.save()
    
    if len(comment)>0:
        st.comment_set.create(text=comment, subject = sub)
    # get experiment for subject
    ord_no = sub.exp_id 
    x = sub.scenario.iteminscenario_set.get(order=ord_no).content_object
    sub.save()

    if sub.trials_done >= x.number_of_trials:
        function_name = x.function
        try:
            f = getattr(sample_gen, function_name+'_process')
            result_dict = f(x.get_all_trial_data(subject_pk=sub.pk))
            store_experiment_results(result_dict, x, sub)
        except AttributeError:
            sys.stderr.write('No processing done\n')
        
        return HttpResponseRedirect(reverse('srefab:next', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:intropage', args=(sub.pk,)))
 
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
