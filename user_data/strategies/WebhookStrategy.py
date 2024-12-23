from freqtrade.strategy import IStrategy
from pandas import DataFrame
from typing import Optional

class WebhookStrategy(IStrategy):
    """
    Стратегия, основанная на сигналах TradingView.
    """

    stoploss = -0.99  # Неактивный стоп-лосс
    timeframe = "5m"
    minimal_roi = {
        "0": 100  # Неактивный ROI
    }

    # Переменные для хранения последнего сигнала
    last_signal_action: Optional[str] = None
    last_signal_contracts: Optional[float] = None

    def handle_signal(self, signal: dict):
        """
        Обрабатывает сигнал, переданный через API.
        """
        self.last_signal_action = signal.get("action")
        self.last_signal_contracts = float(signal.get("contracts", 0))
        print(f"Получен сигнал: {signal}")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавляет индикаторы в DataFrame. В этой стратегии индикаторы не используются.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика входа в сделку на основе сигнала.
        """
        # Если сигнал на покупку (buy)
        if self.last_signal_action == "buy":
            # Закрыть шорт и открыть лонг на указанный процент
            dataframe.loc[:, "exit_short"] = 1
            dataframe.loc[:, "enter_long"] = 1
            dataframe.loc[:, "stake_amount"] = (
                self.last_signal_contracts / 100 * self.wallet.available_balance
            )

        # Если сигнал на продажу (sell)
        if self.last_signal_action == "sell":
            # Закрыть лонг и открыть шорт на указанный процент
            dataframe.loc[:, "exit_long"] = 1
            dataframe.loc[:, "enter_short"] = 1
            dataframe.loc[:, "stake_amount"] = (
                self.last_signal_contracts / 100 * self.wallet.available_balance
            )

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика выхода из сделки на основе сигнала.
        """
        # Выход из шорта, если сигнал - "buy"
        if self.last_signal_action == "buy":
            dataframe.loc[:, "exit_short"] = 1

        # Выход из лонга, если сигнал - "sell"
        if self.last_signal_action == "sell":
            dataframe.loc[:, "exit_long"] = 1

        return dataframe
