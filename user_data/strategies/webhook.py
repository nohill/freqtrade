from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from freqtrade.strategy.interface import IStrategy
from freqtrade.persistence import Trade
from pandas import DataFrame
from typing import Dict
import json

app = FastAPI()

# Модель данных для вебхука
class TradingViewSignal(BaseModel):
    action: str
    contracts: float
    ticker: str
    position_size: float

class WebhookStrategy(IStrategy):
    """
    Webhook-based strategy for Freqtrade.
    """

    # ROI (Return on Investment) настройка
    minimal_roi = {
        "0": 0.1  # Take profit через 10%
    }

    # Стоп-лосс
    stoploss = -0.2  # Убыток максимум 20%

    # Таймфрейм
    timeframe = '5m'

    # Пользовательские данные для сигналов
    custom_info = {}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавление индикаторов. Пусто, так как мы полагаемся на вебхуки.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика покупки на основе сигналов (прокси для совместимости).
        """
        dataframe['buy'] = 0
        if 'action' in self.custom_info and self.custom_info['action'] == 'buy':
            dataframe.loc[dataframe.index[-1], 'buy'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика продажи на основе сигналов (прокси для совместимости).
        """
        dataframe['sell'] = 0
        if 'action' in self.custom_info and self.custom_info['action'] == 'sell':
            dataframe.loc[dataframe.index[-1], 'sell'] = 1
        return dataframe

    def process_signal(self, signal: Dict):
        """
        Обработка вебхука для управления ботом.
        :param signal: JSON-пакет, отправленный через вебхук.
        """
        try:
            action = signal.get("action")
            ticker = signal.get("ticker")
            contracts = float(signal.get("contracts", 0))

            if action not in ["buy", "sell"]:
                self.logger.warning(f"Некорректное действие: {action}")
                return

            # Получение текущей позиции для тикера
            trade = Trade.get_open_trade_by_pair(ticker, self.dp.exchange.id)

            if action == "buy":
                if trade and trade.is_short:
                    # Закрытие шорта
                    self.close_trade(trade, sell_reason="webhook")
                # Открытие лонга
                self.enter_trade(ticker, contracts, direction="long")

            elif action == "sell":
                if trade and trade.is_long:
                    # Закрытие лонга
                    self.close_trade(trade, sell_reason="webhook")
                # Открытие шорта
                self.enter_trade(ticker, contracts, direction="short")

        except Exception as e:
            self.logger.error(f"Ошибка обработки вебхука: {str(e)}")

    def enter_trade(self, ticker: str, contracts: float, direction: str):
        """
        Открытие новой позиции.
        :param ticker: Пара для торговли.
        :param contracts: Количество контрактов.
        :param direction: Направление сделки ("long" или "short").
        """
        try:
            if direction == "long":
                self.custom_info = {"action": "buy", "ticker": ticker, "contracts": contracts}
            elif direction == "short":
                self.custom_info = {"action": "sell", "ticker": ticker, "contracts": contracts}
            self.logger.info(f"Открытие {direction} позиции на {ticker} с количеством {contracts}.")
        except Exception as e:
            self.logger.error(f"Ошибка при открытии позиции: {str(e)}")

    def close_trade(self, trade: Trade, sell_reason: str):
        """
        Закрытие текущей позиции.
        :param trade: Объект сделки для закрытия.
        :param sell_reason: Причина закрытия сделки.
        """
        try:
            self.dp.close_trade(trade)
            self.logger.info(f"Закрытие позиции для {trade.pair} по причине: {sell_reason}.")
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии позиции: {str(e)}")

@app.post("/api/v1/tradingview")
async def tradingview_signal(signal: TradingViewSignal):
    try:
        strategy = WebhookStrategy()
        strategy.process_signal(signal.dict())
        return {"status": "success", "data": signal.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки сигнала: {str(e)}")
