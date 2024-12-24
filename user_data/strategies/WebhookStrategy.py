from freqtrade.strategy import IStrategy
from freqtrade.rpc.rpc_manager import RPC
from freqtrade.rpc.api_server.api_schemas import ForceEnterPayload
from typing import Optional
from pandas import DataFrame

class WebhookStrategy(IStrategy):
    stoploss = -0.99
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

        # Преобразуем buy/sell в long/short
        order_side = "long" if action == "buy" else "short"

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
        try:
            trade = RPC._rpc_force_entry(
                self,
                pair=payload.pair,
                price=payload.price,
                order_side=payload.side,
                order_type=payload.ordertype,
                stake_amount=payload.stakeamount,
                enter_tag=payload.entry_tag or "force_entry",
                leverage=payload.leverage,
            )
            print(f"Сделка успешно создана: {trade}")
        except Exception as e:
            print(f"Ошибка при создании сделки: {e}")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
