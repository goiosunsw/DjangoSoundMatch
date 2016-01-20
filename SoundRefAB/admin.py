from django.contrib import admin
from django.contrib.contenttypes import admin as genadmin

# Register your models here.
from .models import Scenario, Experiment, Page, SoundDemo, ItemInScenario, Subject

#class ParameterModelInLine(genadmin.TabularInLine):
#    model = ParameterModel
#    extra = 1

# class ExperimentInScenarioInline(admin.TabularInline):
#     model = ExperimentInScenario
#     extra = 1
class ItemInScenarioInline(genadmin.GenericTabularInline):
    # fields = ['content_type','object_id','order']
    model = ItemInScenario
    extra = 1


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date')


class ScenarioAdmin(admin.ModelAdmin):
    inlines = (ItemInScenarioInline,)
    exclude = ('items',)
    def rewrite_order_nums(self, request, queryset):
        queryset.order_by('order')
        for ii,obj in enumerate(queryset):
            obj.order = ii
    def save_model(self, request, obj, form, change):
        eis_set = obj.iteminscenario_set.all()
        
        for ii,eis in enumerate(eis_set.order_by('order')):
            eis.order = ii + 1
            eis.save()
        obj.save()

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Experiment)
admin.site.register(Page)
admin.site.register(SoundDemo)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ItemInScenario)
