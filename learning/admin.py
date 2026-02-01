from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Unit, Lesson, QuizQuestion, UserLessonProgress

class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1 # Mostra 1 espaço em branco para adicionar pergunta por padrão

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'order', 'xp_reward')
    list_filter = ('unit',)
    inlines = [QuizQuestionInline] # Aqui acontece a mágica: perguntas dentro da lição

class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'description')

admin.site.register(Unit, UnitAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(UserLessonProgress) # Apenas para debug, para ver quem fez o que