import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from learning.models import Lesson, QuizQuestion


import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from learning.models import Lesson, QuizQuestion

class Command(BaseCommand):
    help = 'Importa questões de um arquivo JSON para uma Lição específica'

    def add_arguments(self, parser):
        # Permite passar o nome do arquivo JSON (opcional, padrão anatomia.json)
        parser.add_argument('--file', type=str, default='anatomia.json', help='Nome do arquivo JSON na raiz do projeto')
        # Permite passar parte do título da aula para encontrar onde salvar
        parser.add_argument('--lesson', type=str, default='Candlestick', help='Parte do título da lição para vincular')

    def handle(self, *args, **options):
        file_name = options['file']
        lesson_search = options['lesson']

        # 1. Encontrar o arquivo JSON
        file_path = os.path.join(settings.BASE_DIR, file_name)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ Arquivo não encontrado: {file_path}"))
            self.stdout.write("Certifique-se de salvar o JSON na mesma pasta do manage.py")
            return

        # 2. Encontrar a Lição no Banco de Dados
        # Busca a primeira lição que contenha o texto (ex: "Leitura de Candlesticks")
        lesson = Lesson.objects.filter(title__icontains=lesson_search).first()

        if not lesson:
            self.stdout.write(self.style.ERROR(f"❌ Nenhuma lição encontrada com o título contendo '{lesson_search}'"))
            self.stdout.write("Dica: Crie a aula no Admin primeiro ou ajuste o termo de busca.")
            return

        self.stdout.write(f"📂 Lendo {file_name}...")
        self.stdout.write(f"🔗 Vinculando à aula: {lesson.title}")

        # 3. Ler e Importar
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)

            count = 0
            for item in questions_data:
                # Modificação solicitada: Usando get_or_create para incluir a imagem
                # Ele tenta buscar pela lição e texto da pergunta.
                # Se não achar, cria usando os dados em 'defaults'.
                question, created = QuizQuestion.objects.get_or_create(
                    lesson=lesson,
                    text=item['question'],
                    defaults={
                        'options': item['options'],
                        'correct_option': item['correct'],
                        'explanation': item['explanation'],
                        'image': item.get('image', None)  # Captura a imagem se existir no JSON
                    }
                )

                if created:
                    count += 1
                else:
                    self.stdout.write(f"⚠️ Pular duplicada: {item['question'][:30]}...")

            self.stdout.write(
                self.style.SUCCESS(f"✅ Sucesso! {count} novas perguntas importadas para '{lesson.title}'."))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("❌ Erro no formato do JSON. Verifique a sintaxe."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro inesperado: {e}"))

