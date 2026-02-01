from django.urls import path
from . import views

app_name = 'learning'  # Namespace para facilitar links (ex: learning:detail)

urlpatterns = [
    # A lista de todas as unidades (O "Mapa")
    path('', views.course_map, name='course_map'),

    # A tela de uma aula específica (ex: /aula/1/)
    path('aula/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
# Nova rota API
    path('api/check_answer/', views.check_answer, name='check_answer'),
]