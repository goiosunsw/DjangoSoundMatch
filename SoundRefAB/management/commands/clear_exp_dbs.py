from django.core.management.base import BaseCommand
from SoundRefAB.models import Experiment, Page, Scenario, ItemInScenario

class Command(BaseCommand):
    args = ''
    help = 'Clear scenarios, pages and experiments'

    def handle(self, *args, **options):
        models_to_clear = (ItemInScenario, Experiment, Page, Scenario)
        for m in models_to_clear:
            m.objects.all().delete()
