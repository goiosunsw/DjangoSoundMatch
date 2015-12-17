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
    def rewrite_order_nums(self, request, queryset):
        queryset.order_by('order')
        for ii,obj in enumerate(queryset):
            obj.order = ii
    def save_model(self, request, obj, form, change):
        eis_set = obj.experimentinscenario_set.all()
        
        for ii,eis in enumerate(eis_set.order_by('order')):
            eis.order = ii + 1
            eis.save()
        obj.save()

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Experiment)
admin.site.register(Subject, SubjectAdmin)
