from django.db import models

# Create your models here.
from django.db import models


class TradeScenario(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Iniciante'),
        ('medium', 'Intermediário'),
        ('hard', 'Avançado'),
    ]

    ACTION_CHOICES = [
        ('BUY', 'Comprar (Long)'),
        ('SELL', 'Vender (Short)'),
        ('WAIT', 'Aguardar'),
    ]

    title = models.CharField(max_length=100, verbose_name="Título do Cenário")
    description = models.TextField(verbose_name="Contexto (O que o aluno deve analisar?)")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')

    # Aqui guardamos os dados do gráfico.
    # Ex: [{"time": "2023-10-01", "open": 100, "high": 105, "low": 90, "close": 102}, ...]
    chart_data = models.JSONField(verbose_name="Dados do Gráfico (OHLC JSON)")

    # A resposta correta
    correct_action = models.CharField(max_length=4, choices=ACTION_CHOICES)

    # Feedback educativo
    explanation = models.TextField(verbose_name="Explicação Técnica (Por que essa é a resposta?)")

    # Custo para jogar (Gamificação)
    cost_to_play = models.PositiveIntegerField(default=10, verbose_name="Custo em Moedas")
    reward_xp = models.PositiveIntegerField(default=20, verbose_name="Recompensa de XP")

    def __str__(self):
        return f"[{self.difficulty}] {self.title}"


class UserScenarioAttempt(models.Model):
    """
    Registra as tentativas do usuário no simulador.
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    scenario = models.ForeignKey(TradeScenario, on_delete=models.CASCADE)
    chosen_action = models.CharField(max_length=4)
    is_correct = models.BooleanField()
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "✅" if self.is_correct else "❌"
        return f"{self.user.username} - {self.scenario.title} {status}"