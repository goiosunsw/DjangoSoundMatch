from django.core.management.base import BaseCommand
from SoundRefAB.models import Experiment, Page, Scenario, ItemInScenario

class Command(BaseCommand):
    args = ''
    help = 'will populate with our perceptual experiment. For now, nothing'

    def handle(self, *args, **options):
        print 'HI'
