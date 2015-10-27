from django.shortcuts import render

# Create your views here.
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
    
def SoundPage(request, subject_id):
    # get subject
    sub = get_object_or_404(Subject, pk=subject_id)
    now = timezone.now()

    try:
        # get experiment for subject
        x = sub.experiment

        # create sound set
        st = SoundSet.objects.create(shown_date=now, valid_date=now, subject=sub)
        st.trial = sub.trials_done + 1
        st.save()

        # retrieve data from previous experiment
        try:
            old_st = sub.soundset_set.latest('id')
            prev_param, prev_adj_val = retrieve_sound_parameters(old_st)
        except SoundSet.DoesNotExist:
            prev_param=[]
            prev_adj_val=0

        function_name = x.function
        try:
            f = getattr(sample_gen, function_name)
        except AttributeError:
            raise Http404("Error in sample generating function name: "+function_name)

        sound_data, param_dict, difficulty_divider = f(subject_id, prev_param=prev_param,
                                   path = settings.MEDIA_ROOT, url_path = settings.MEDIA_URL)

        #store sound data in db
        store_sound_parameters(st, sound_data, param_dict)
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
    st.choice = int(request.POST['adj_val'])
    st.valid_date = timezone.now()
    st.save()
    sub = st.subject
    sub.trials_done += 1
    x = sub.experiment

    sub.save()

    if sub.trials_done >= x.number_of_trials:
        return HttpResponseRedirect(reverse('srefab:thanks', args=(st.subject.pk,)))
        #return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))
    else:
        return HttpResponseRedirect(reverse('srefab:soundpage', args=(sub.pk,)))


