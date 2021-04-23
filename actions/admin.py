from django.contrib import admin
from .models import AggregateAction

@admin.register(AggregateAction)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'n_actions', 'created')
    list_filter = ('created',)