from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Usuário customizado para o TraderEdu.
    Herda todos os campos padrão (username, password, email)
    e adiciona campos de gamificação.
    """

    # --- Gamificação ---
    coins = models.PositiveIntegerField(
        default=0,
        verbose_name="Moedas (TraderCoins)"
    )
    xp = models.PositiveIntegerField(
        default=0,
        verbose_name="Pontos de Experiência"
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name="Ofensiva (Dias seguidos)"
    )

    # --- Progressão e Permissões ---
    # Define se o usuário já desbloqueou o simulador (Seção 02)
    is_simulator_unlocked = models.BooleanField(
        default=False,
        verbose_name="Simulador Desbloqueado?"
    )

    # Opcional: Para saber em qual unidade o aluno está
    current_unit_index = models.PositiveIntegerField(
        default=1,
        verbose_name="Unidade Atual"
    )

    def __str__(self):
        return f"{self.username} - XP: {self.xp} | Coins: {self.coins}"