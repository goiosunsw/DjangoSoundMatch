from django.contrib import admin

# Register your models here.
from .models import Scenario, Experiment, ExperimentInScenario, Subject

#class ParameterModelInLine(admin.TabularInLine):
#    model = ParameterModel
#    extra = 1

class ExperimentInScenarioInline(admin.TabularInline):
    model = ExperimentInScenario
    extra = 1


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date')


class ScenarioAdmin(admin.ModelAdmin):
    inlines = (ExperimentInScenarioInline,)

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Experiment)
admin.site.register(Subject, SubjectAdmin)
