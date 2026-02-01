import json
import yfinance as yf
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from simulator.models import TradeScenario
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Gera cenários com Indicadores Técnicos (Média Móvel + RSI)'

    def add_arguments(self, parser):
        parser.add_argument('ticker', type=str, help='Símbolo (Ex: BTC-USD)')
        parser.add_argument('--days', type=int, default=7, help='Dias de histórico')

    def handle(self, *args, **options):
        ticker = options['ticker']
        days = options['days']

        self.stdout.write(f"🔍 Baixando dados e calculando indicadores para {ticker}...")

        end_date = datetime.now()
        # Pegamos dias extras para garantir que a Média de 100 tenha dados suficientes para começar
        start_date = end_date - timedelta(days=days + 5)

        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval="15m", progress=False)

            # --- LIMPEZA DE DADOS ---
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.loc[:, ~df.columns.duplicated()]

            # --- CÁLCULO DOS INDICADORES ---
            # 1. Médias Móveis
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            df['SMA_100'] = df['Close'].rolling(window=100).mean()

            # 2. RSI (14 periodos)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Removemos os NaN iniciais (que aparecem por causa da SMA 100)
            df.dropna(inplace=True)

            # Cortamos para ficar apenas os dias solicitados (ex: últimos 7 dias reais)
            # Isso evita mostrar o "período de aquecimento" das médias
            cut_date = pd.Timestamp(datetime.now() - timedelta(days=days)).tz_localize(df.index.dtype.tz)
            df = df[df.index >= cut_date]

            if len(df) < 50:
                self.stdout.write(self.style.ERROR(f"❌ Dados insuficientes após cálculo de indicadores."))
                return

            # --- SEPARAÇÃO PASSADO / FUTURO ---
            future_candles = 16
            df_chart = df.iloc[:-future_candles]
            df_future = df.iloc[-future_candles:]

            # Formata JSON com os NOVOS CAMPOS
            chart_data = []
            for index, row in df_chart.iterrows():
                # Função auxiliar para garantir float puro
                def get_val(val):
                    return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

                candle = {
                    "time": int(index.timestamp()),
                    "open": get_val(row['Open']),
                    "high": get_val(row['High']),
                    "low": get_val(row['Low']),
                    "close": get_val(row['Close']),
                    # Indicadores
                    "ema9": get_val(row['EMA_9']),
                    "ema21": get_val(row['EMA_21']),
                    "sma100": get_val(row['SMA_100']),
                    "rsi": get_val(row['RSI'])
                }
                chart_data.append(candle)

            # --- INTELIGÊNCIA DO ORÁCULO (Mantida) ---
            last_price = get_val(df_chart.iloc[-1]['Close'])
            future_max = get_val(df_future['High'].max())
            future_min = get_val(df_future['Low'].min())
            future_close = get_val(df_future.iloc[-1]['Close'])

            upside = (future_max - last_price) / last_price * 100
            downside = (last_price - future_min) / last_price * 100
            final_move = (future_close - last_price) / last_price * 100

            if upside > 0.5 and final_move > 0:
                action = 'BUY'
                reason = f"Alta confirmada! Preço subiu {upside:.2f}%."
            elif downside > 0.5 and final_move < 0:
                action = 'SELL'
                reason = f"Baixa confirmada! Preço caiu {downside:.2f}%."
            else:
                action = 'WAIT'
                reason = f"Lateralidade. Variação de apenas {final_move:.2f}%."

            scenario = TradeScenario.objects.create(
                title=f"Setup Técnico {ticker}",
                description=f"Analise o cruzamento das médias (9, 21, 100) e o RSI.",
                difficulty='hard',
                chart_data=chart_data,
                correct_action=action,
                explanation=reason,
                cost_to_play=25,
                reward_xp=100
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Cenário PRO criado! ID: {scenario.id}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro: {e}"))
            import traceback
            traceback.print_exc()