from django.core.management.base import BaseCommand
from SoundRefAB.models import SoundTriplet, Subject, Experiment, Scenario, ItemInScenario
from django.contrib.contenttypes.models import ContentType
import datetime

class Command(BaseCommand):
    args = ''
    help = 'generates the "run" field for experiments that have several repetitions'
    def handle(self, *args, **options):
        for sub in Subject.objects.all():
            self.add_run_field_subj(sub)

    def add_run_field_subj(self,subject):
        xcont = ContentType.objects.get_for_model(Experiment)
        exp_ids = ItemInScenario.objects.filter(content_type=xcont).values_list('object_id',flat=True)
        exp_list = Experiment.objects.filter(id__in=exp_ids)
        for exp in exp_list:
            self.add_run_field(subject,exp)
    
    def add_run_field(self,subject,experiment):
        st_list = subject.soundtriplet_set.filter(experiment=experiment).order_by('shown_date')
        run = 1
        last_trial = 0
        for st in st_list:
            if st.trial == last_trial+1:
                pass
            else:
                run += 1
            st.run = run
            print '%s; Subject %d (st %d): trial %d, run %d'%(experiment,subject.id,st.id,st.trial,run)
            last_trial = st.trial
            st.save()
            
