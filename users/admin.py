from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Criamos uma classe de admin customizada para mostrar nossos campos novos
class CustomUserAdmin(UserAdmin):
    # Campos que aparecem na lista de usuários (tabela)
    list_display = ('username', 'email', 'xp', 'coins', 'is_simulator_unlocked', 'is_staff')

    # Adicionamos os novos campos na área de edição do usuário ("Fieldsets")
    fieldsets = UserAdmin.fieldsets + (
        ('Gamificação & Progresso',
         {'fields': ('coins', 'xp', 'current_streak', 'is_simulator_unlocked', 'current_unit_index')}),
    )


admin.site.register(User, CustomUserAdmin)