from freqtrade.strategy import IStrategy
from pandas import DataFrame
from typing import Optional

# Создаем роутер

class WebhookStrategy(IStrategy):
    """
    Стратегия, основанная на сигналах TradingView.
    """

    stoploss = -0.99 # inactive
    timeframe = "5m"
    minimal_roi = {
        "0": 100 # inactive
    }


    # Метод обязателен, даже если не используется
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавляет индикаторы в DataFrame. В этой стратегии индикаторы не используются.
        """
        return dataframe

    # Переменные для хранения последнего сигнала
    last_signal_action: Optional[str] = None
    last_signal_ticker: Optional[str] = None
    last_signal_contracts: Optional[float] = None

    def handle_signal(self, signal: dict):
        """
        Обрабатывает сигнал, переданный через API.
        """
        print(f"Получен сигнал: {signal}")

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Пример входа на основе сигнала.
        """
        if (
            self.last_signal_action == "enter_long"
            and metadata["pair"] == self.last_signal_ticker
        ):
            dataframe["enter_long"] = 1

        if (
            self.last_signal_action == "enter_short"
            and metadata["pair"] == self.last_signal_ticker
        ):
            dataframe["enter_short"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Пример выхода на основе сигнала.
        """
        if (
            self.last_signal_action == "exit_long"
            and metadata["pair"] == self.last_signal_ticker
        ):
            dataframe["exit_long"] = 1

        if (
            self.last_signal_action == "exit_short"
            and metadata["pair"] == self.last_signal_ticker
        ):
            dataframe["exit_short"] = 1

        return dataframe
