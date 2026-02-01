from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings  # Para referenciar o nosso User customizado


class Unit(models.Model):
    """
    Representa um Módulo macro. Ex: 'Unidade 1: Candlesticks'
    """
    title = models.CharField(max_length=100, verbose_name="Título da Unidade")
    description = models.TextField(verbose_name="Descrição", blank=True)
    order = models.PositiveIntegerField(unique=True, verbose_name="Ordem (1, 2, 3...)")

    class Meta:
        ordering = ['order']
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"

    def __str__(self):
        return f"{self.order}. {self.title}"


class Lesson(models.Model):
    """
    A aula em si. Ex: 'O que é um Doji?'
    """
    unit = models.ForeignKey(Unit, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Título da Aula")
    order = models.PositiveIntegerField(verbose_name="Ordem dentro da Unidade")

    # Conteúdo teórico (HTML simples ou Markdown)
    content = models.TextField(verbose_name="Conteúdo Teórico", help_text="Use HTML ou texto simples")

    # Recompensas
    xp_reward = models.PositiveIntegerField(default=10, verbose_name="XP de Recompensa")
    coins_reward = models.PositiveIntegerField(default=5, verbose_name="Moedas de Recompensa")

    class Meta:
        ordering = ['order']
        unique_together = ['unit', 'order']  # Não pode ter duas aulas nº 1 na mesma unidade

    def __str__(self):
        return f"{self.unit.order}.{self.order} - {self.title}"


class QuizQuestion(models.Model):
    """
    Perguntas vinculadas a uma lição.
    """
    lesson = models.ForeignKey(Lesson, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=300, verbose_name="Enunciado da Pergunta")

    # Vamos salvar as opções como JSON para simplificar.
    # Ex: {"a": "Sobe", "b": "Desce", "c": "Lateral"}
    options = models.JSONField(verbose_name="Opções (JSON)", default=dict)
    # Adicione este campo:
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True, verbose_name="Imagem de Apoio")

    correct_option = models.CharField(max_length=1, verbose_name="Opção Correta (a, b, c...)")
    explanation = models.TextField(verbose_name="Explicação do Erro/Acerto", blank=True)

    def __str__(self):
        return self.text[:50]


class UserLessonProgress(models.Model):
    """
    Tabela de ligação: Qual usuário completou qual lição?
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']  # Usuário só completa a lição uma vez

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"



