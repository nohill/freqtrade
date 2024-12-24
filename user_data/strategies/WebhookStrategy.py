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

        # Преобразуем buy/sell в соответствующую сторону ордера
        order_side = "buy" if action == "buy" else "sell"

        # Проверяем доступность пары
        if not ticker:
            if hasattr(self, "dp") and self.dp:
                ticker = self.dp.current_whitelist()[0]
            else:
                raise ValueError("Пара не указана в сигнале, и объект 'dp' не доступен.")

        # Получаем баланс через объект exchange
        available_balance = 100

        # Вычисляем размер сделки
        stake_amount = available_balance * contracts

        print(f"Обработка сигнала {action.upper()} для пары {ticker} с размером позиции: {stake_amount}")

        # Закрытие открытых сделок
        self.close_open_positions(ticker, order_side)

        # Создание нового ордера
        try:
            order = self.exchange.create_order(
                pair=ticker,
                order_type="market",
                side=order_side,
                amount=stake_amount,
            )
            print(f"Ордер успешно создан: {order}")
        except Exception as e:
            print(f"Ошибка при создании ордера: {e}")

    def close_open_positions(self, ticker: str, order_side: str):
        """
        Закрывает все открытые позиции по указанной паре, создавая противоположные ордера.
        """
        trades = Trade.get_open_trades(pair=ticker)
        for trade in trades:
            side_to_close = "sell" if order_side == "buy" else "buy"
            print(f"Закрытие позиции для {ticker} с ордером {side_to_close}")
            try:
                self.exchange.create_order(
                    pair=ticker,
                    order_type="market",
                    side=side_to_close,
                    amount=trade.amount,
                )
                print(f"Позиция закрыта: {trade}")
            except Exception as e:
                print(f"Ошибка при закрытии позиции: {e}")

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
