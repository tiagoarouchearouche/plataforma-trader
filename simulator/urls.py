from django.urls import path
from . import views

app_name = 'simulator'

urlpatterns = [
    # Tela principal do simulador (lista de cenários ou botão "Jogar")
    path('', views.index, name='index'),

    # A tela do jogo em si (carrega um cenário específico)
    path('jogar/<int:scenario_id>/', views.play_scenario, name='play'),

    # API para checar se a decisão (Buy/Sell) foi correta
    path('api/check/', views.check_trade, name='check_trade'),
]