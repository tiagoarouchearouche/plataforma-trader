from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TradeScenario, UserScenarioAttempt

class TradeScenarioAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'correct_action', 'cost_to_play')
    list_filter = ('difficulty', 'correct_action')
    # Dica: O JSONField já é validado pelo Django, mas cuidado ao colar o JSON aqui.

admin.site.register(TradeScenario, TradeScenarioAdmin)
admin.site.register(UserScenarioAttempt)