from django.contrib import admin
from django.contrib.contenttypes import admin as genadmin
from django.core.urlresolvers import reverse


# Register your models here.
from .models import Scenario, Experiment, Page, ItemInScenario, Subject

#class ParameterModelInLine(genadmin.TabularInLine):
#    model = ParameterModel
#    extra = 1

# class ExperimentInScenarioInline(admin.TabularInline):
#     model = ExperimentInScenario
#     extra = 1
class ItemInScenarioInline(genadmin.GenericTabularInline):
    # fields = ['content_type','object_id','order']
    model = ItemInScenario
    #list_filter = ('Scenario',)
    #extra = 1
    
class ItemInScenarioAdmin(admin.ModelAdmin):
    # fields = ['content_type','object_id','order']
    model = ItemInScenario
    list_filter = ('scenario',)
    list_display = ('id', 'scenario', 'content_type', 'object_id')
    
    #extra = 1


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date')

def get_admin_url(self):
    return "/admin/appname/books/%d/" %self.id

class ScenarioAdmin(admin.ModelAdmin):
    #inlines = (ItemInScenarioInline,)
    #exclude = ('items',)
    list_display = ['description', 'associated_items']
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
    def associated_items(self, obj):
        #redirect_url = reverse('admin:iteminscenario_changelist')
        #extra = "?iteminscenario__id__exact=%d" % (obj.id)
        #return "<a href='%s'>Items in scenario</a>" % (redirect_url + extra)
        html = ""
        for obj in ItemInScenario.objects.filter(scenario__id=obj.id):
            html += '<p><a href="%s">%s</a></p>' %(get_admin_url(obj), obj)
        return html
        
    associated_items.allow_tags = True
    

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Experiment)
admin.site.register(Page)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ItemInScenario,ItemInScenarioAdmin)
