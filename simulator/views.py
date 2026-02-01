from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import TradeScenario, UserScenarioAttempt


@login_required
def index(request):
    """Lista os desafios disponíveis"""
    scenarios = TradeScenario.objects.all()
    return render(request, 'simulator/index.html', {'scenarios': scenarios})


# simulator/views.py (apenas a função play_scenario muda)

from django.shortcuts import render, get_object_or_404, redirect  # Adicione redirect
from django.contrib import messages  # <--- Importante para mostrar o erro na tela


# ... (outros imports mantidos)

@login_required
def play_scenario(request, scenario_id):
    """Carrega a tela de trade com o gráfico"""
    scenario = get_object_or_404(TradeScenario, id=scenario_id)

    # --- 1. TRAVA DE SEGURANÇA (ECONOMIA) ---
    if request.user.coins < scenario.cost_to_play:
        # Se não tiver dinheiro, avisa e manda embora
        messages.error(request,
                       f"Saldo insuficiente! Você precisa de {scenario.cost_to_play} moedas para operar neste cenário.")
        return redirect('simulator:index')

    # --- 2. COBRANÇA (PEDÁGIO) ---
    # Se chegou aqui, tem saldo. Vamos cobrar.
    # Nota: Em produção, usaríamos uma lógica para evitar cobrar no F5 (Refresh),
    # mas para este MVP, "Entrou = Pagou".
    request.user.coins -= scenario.cost_to_play
    request.user.save()

    # Feedback visual discreto
    messages.success(request, f"Operação iniciada! -{scenario.cost_to_play} moedas.")

    # --- 3. PREPARAÇÃO DOS DADOS (CÓDIGO QUE JÁ TINHAMOS) ---
    data = scenario.chart_data
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = []

    chart_data_json = json.dumps(data)

    return render(request, 'simulator/play.html', {
        'scenario': scenario,
        'chart_data_json': chart_data_json
    })


@login_required
@require_POST
def check_trade(request):
    """Verifica se o usuário acertou a direção do mercado"""
    data = json.loads(request.body)
    scenario_id = data.get('scenario_id')
    action = data.get('action')  # BUY, SELL ou WAIT

    scenario = get_object_or_404(TradeScenario, id=scenario_id)

    is_correct = (action == scenario.correct_action)

    # Salva a tentativa
    UserScenarioAttempt.objects.create(
        user=request.user,
        scenario=scenario,
        chosen_action=action,
        is_correct=is_correct
    )

    if is_correct:
        # Recompensa
        request.user.xp += scenario.reward_xp
        request.user.save()

    return JsonResponse({
        'correct': is_correct,
        'explanation': scenario.explanation,
        'xp_gained': scenario.reward_xp if is_correct else 0
    })