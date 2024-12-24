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

        # Проверяем доступность объекта dp
        if not hasattr(self, "dp") or not self.dp:
            raise ValueError("Объект 'dp' (DataProvider) не инициализирован. Проверьте конфигурацию Freqtrade.")

        # Получаем первую доступную пару из whitelist
        pair = self.dp.current_whitelist()[0]

        # Проверяем доступность объекта wallets
        if self.wallets is not None:
            available_balance = self.wallets.get_total_stake_amount()
        else:
            raise ValueError("Объект 'wallets' не инициализирован. Проверьте конфигурацию Freqtrade.")

        # Вычисляем размер сделки
        stake_amount = available_balance * contracts

        if action == "buy":
            print(f"Обработка сигнала BUY для пары {pair} с размером позиции: {stake_amount}")
            # Закрыть текущую шорт позицию
            self.close_positions(side="short")
            # Открыть новую лонг позицию
            self.enter_position(pair, stake_amount, side="long")

        elif action == "sell":
            print(f"Обработка сигнала SELL для пары {pair} с размером позиции: {stake_amount}")
            # Закрыть текущую лонг позицию
            self.close_positions(side="long")
            # Открыть новую шорт позицию
            self.enter_position(pair, stake_amount, side="short")

    def close_positions(self, side: str):
        """
        Закрывает все активные позиции указанного типа (long/short).
        """
        trades = Trade.get_open_trades()
        for trade in trades:
            if trade.is_short == (side == "short"):
                print(f"Закрытие позиции {side} для пары {trade.pair}")
                self.close_trade(trade)

    def enter_position(self, pair: str, stake_amount: float, side: str):
        """
        Открывает новую позицию указанного типа (long/short).
        """
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
        Добавляет условия для входа в сделку. Эта стратегия полагается на сигналы и не использует логику входа.
        """
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавляет условия для выхода из сделки. Эта стратегия полагается на сигналы и не использует логику выхода.
        """
        return dataframe
