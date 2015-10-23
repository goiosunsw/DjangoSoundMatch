from django.contrib import admin

# Register your models here.
from .models import Experiment, Subject

#class ParameterModelInLine(admin.TabularInLine):
#    model = ParameterModel
#    extra = 1


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date')


admin.site.register(Experiment)
admin.site.register(Subject, SubjectAdmin)
