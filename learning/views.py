import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Unit, Lesson, QuizQuestion, UserLessonProgress


@login_required
def course_map(request):
    units = Unit.objects.prefetch_related('lessons').all()
    completed_ids = UserLessonProgress.objects.filter(
        user=request.user
    ).values_list('lesson_id', flat=True)

    return render(request, 'learning/map.html', {
        'units': units,
        'completed_ids': completed_ids
    })


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Verifica se já completou para não dar recompensa dupla visualmente
    is_completed = UserLessonProgress.objects.filter(user=request.user, lesson=lesson).exists()

    if request.method == 'POST':
        # Ao clicar em "Concluir Aula"
        if not is_completed:
            # CORREÇÃO AQUI: Removemos o score=100
            UserLessonProgress.objects.create(user=request.user, lesson=lesson)

            # Adiciona recompensas ao perfil
            request.user.xp += lesson.xp_reward
            request.user.coins += lesson.coins_reward
            request.user.save()

        return redirect('learning:course_map')

    return render(request, 'learning/lesson_detail.html', {
        'lesson': lesson,
        'is_completed': is_completed
    })


@login_required
@require_POST
def check_answer(request):
    """
    API simples que recebe JSON: { "question_id": 1, "selected_option": "a" }
    Retorna: { "correct": true/false, "explanation": "..." }
    """
    data = json.loads(request.body)
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')

    question = get_object_or_404(QuizQuestion, id=question_id)

    is_correct = (selected_option == question.correct_option)

    # Se quiser dar XP por pergunta individual, faria aqui. 
    # Por enquanto vamos dar XP só ao concluir a aula.

    return JsonResponse({
        'correct': is_correct,
        'correct_option': question.correct_option,
        'explanation': question.explanation
    })