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
        ticker = signal.get("ticker")

        if not action or contracts <= 0:
            print("Некорректный сигнал")
            return

        # Проверяем доступность пары
        if not ticker:
            # Если пара не передана, используем первую пару из whitelist
            if hasattr(self, "dp") and self.dp:
                ticker = self.dp.current_whitelist()[0]
            else:
                raise ValueError("Пара не указана в сигнале, и объект 'dp' не доступен.")

        # Получаем баланс через объект exchange
        available_balance = 100

        # Вычисляем размер сделки
        stake_amount = available_balance * contracts

        if action == "buy":
            print(f"Обработка сигнала BUY для пары {ticker} с размером позиции: {stake_amount}")
            # Закрыть текущую шорт позицию
            self.close_positions(side="sell", pair=ticker)
            # Открыть новую лонг позицию
            self.create_trade(pair=ticker, stake_amount=stake_amount, side="buy")

        elif action == "sell":
            print(f"Обработка сигнала SELL для пары {ticker} с размером позиции: {stake_amount}")
            # Закрыть текущую лонг позицию
            self.close_positions(side="buy", pair=ticker)
            # Открыть новую шорт позицию
            self.create_trade(pair=ticker, stake_amount=stake_amount, side="sell")

    def close_positions(self, side: str, pair: str):
        """
        Закрывает все активные позиции указанного типа (long/short) для конкретной пары.
        """
        trades = Trade.get_open_trades()
        for trade in trades:
            if trade.is_short == (side == "sell"):
                print(f"Закрытие позиции {side} для пары {trade.pair}")
                self.close_trade(trade)

    def create_trade(self, pair: str, stake_amount: float, side: str):
        """
        Создает новую сделку (long/short) через биржу.
        """
        order_type = "market"  # or "limit"

        print(f"Создание сделки {side} для пары {pair} с размером {stake_amount}")

        self.confirm_trade_entry(
            pair=pair,
            order_type=order_type,
            side=side,
            amount=stake_amount,
            rate=100,
            entry_tag=None,
            time_in_force="gtc",
            current_time=datetime.now(timezone.utc),
        )

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
