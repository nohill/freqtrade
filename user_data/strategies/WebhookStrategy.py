from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade
from typing import Optional
from pandas import DataFrame


class WebhookStrategy(IStrategy):
    """
    Стратегия, основанная на сигналах TradingView.
    """

    stoploss = -0.99  # Неактивный стоп-лосс
    timeframe = "5m"
    minimal_roi = {
        "0": 100  # Неактивный ROI
    }

    def handle_signal(self, signal: dict):
        """
        Обрабатывает сигнал, переданный через API.
        Закрывает позиции и открывает новые на основе сигнала.
        """
        action = signal.get("action")
        contracts = float(signal.get("contracts", 0)) / 100

        if not action or contracts <= 0:
            print("Некорректный сигнал")
            return

        # Получение доступного баланса
        available_balance = self.wallet.get_available_stake_amount()

        # Вычисляем размер сделки
        stake_amount = available_balance * contracts

        if action == "buy":
            print(f"Обработка сигнала BUY с размером позиции: {stake_amount}")
            # Закрыть текущую шорт позицию
            self.close_positions(side="short")
            # Открыть новую лонг позицию
            self.enter_position(stake_amount, side="long")

        elif action == "sell":
            print(f"Обработка сигнала SELL с размером позиции: {stake_amount}")
            # Закрыть текущую лонг позицию
            self.close_positions(side="long")
            # Открыть новую шорт позицию
            self.enter_position(stake_amount, side="short")

    def close_positions(self, side: str):
        """
        Закрывает все активные позиции указанного типа (long/short).
        """
        trades = Trade.get_open_trades()
        for trade in trades:
            if trade.is_short == (side == "short"):
                print(f"Закрытие позиции {side} для пары {trade.pair}")
                self.close_trade(trade)

    def enter_position(self, stake_amount: float, side: str):
        """
        Открывает новую позицию указанного типа (long/short).
        """
        pair = self.dp.current_whitelist()[0]  # Берем первую доступную пару
        print(f"Открытие новой позиции {side} для пары {pair} с размером {stake_amount}")
        if side == "long":
            self.buy(pair=pair, stake_amount=stake_amount)
        elif side == "short":
            self.sell(pair=pair, stake_amount=stake_amount)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавляет индикаторы в DataFrame. В этой стратегии индикаторы не используются.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
