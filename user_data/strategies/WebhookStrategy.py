from freqtrade.strategy import IStrategy
from freqtrade.rpc.rpc_manager import RPC
from freqtrade.rpc.api_server.api_schemas import ForceEnterPayload
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
            if hasattr(self, "dp") and self.dp:
                ticker = self.dp.current_whitelist()[0]
            else:
                raise ValueError("Пара не указана в сигнале, и объект 'dp' не доступен.")

        # Получаем баланс через объект exchange
        available_balance = 100

        # Вычисляем размер сделки
        stake_amount = available_balance * contracts

       order_side = "long" if action == "buy" else "short"

        print(f"Обработка сигнала {action.upper()} для пары {ticker} с размером позиции: {stake_amount}")

        # Создаём payload для RPC
        payload = ForceEnterPayload(
            pair=ticker,
            price=None,  # Рыночный ордер
            side=order_side,
            ordertype="market",
            stakeamount=stake_amount,
            entry_tag="signal_entry",
            leverage=1,  # Укажите нужное плечо, если используется фьючерсная торговля
        )

        # Выполняем ордер через RPC
        rpc = RPC()
        trade = rpc._rpc_force_entry(
            payload.pair,
            payload.price,
            order_side=payload.side,
            order_type=payload.ordertype,
            stake_amount=payload.stakeamount,
            enter_tag=payload.entry_tag or "force_entry",
            leverage=payload.leverage,
        )

        if trade:
            print(f"Сделка успешно создана: {trade}")
        else:
            print(f"Ошибка при создании сделки для {ticker}.")

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
