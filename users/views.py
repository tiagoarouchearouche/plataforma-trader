from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from simulator.models import UserScenarioAttempt


@login_required
def profile_dashboard(request):
    user = request.user
    attempts = UserScenarioAttempt.objects.filter(user=user)

    # --- 1. KPIs Principais (Cards) ---
    total_trades = attempts.count()
    wins = attempts.filter(is_correct=True).count()
    losses = total_trades - wins

    win_rate = round((wins / total_trades * 100), 1) if total_trades > 0 else 0

    # --- 2. Dados para o Gráfico de Pizza (Win vs Loss) ---
    # Formato para Chart.js: [Wins, Losses]
    pie_data = [wins, losses]

    # --- 3. Dados para o Gráfico de Barras (Atividade Recente) ---
    # Agrupa trades por dia (últimos 7 dias com atividade)
    activity_data = (
        attempts
        .annotate(date=TruncDate('played_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Prepara listas para o JS (Eixo X = Datas, Eixo Y = Quantidade)
    bar_labels = [item['date'].strftime('%d/%m') for item in activity_data]
    bar_values = [item['count'] for item in activity_data]

    return render(request, 'users/profile.html', {
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'pie_data': pie_data,
        'bar_labels': bar_labels,
        'bar_values': bar_values,
    })