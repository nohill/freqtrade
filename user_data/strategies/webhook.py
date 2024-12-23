from fastapi import APIRouter, Depends, HTTPException, Query
from freqtrade.strategy import IStrategy
from pandas import DataFrame
from typing import Optional

# Создаем роутеры
router_public = APIRouter()
router = APIRouter()

# Стратегия
class WebhookStrategy(IStrategy):
    """
    Стратегия для обработки сигналов от TradingView через вебхук.
    """

    # Настройки стратегии
    timeframe = "5m"
    can_short = True
    minimal_roi = {"0": 0.01}
    stoploss = -0.10
    startup_candle_count = 0

    # Переменные для хранения последнего сигнала
    last_signal_action: Optional[str] = None
    last_signal_ticker: Optional[str] = None

    @staticmethod
    @router.post("/api/v1/tradingview", tags=["signals"])
    async def handle_signal(action: str = Query(...), ticker: str = Query(...), contracts: int = Query(...)):
        """
        Обрабатывает сигнал от TradingView через запрос.
        """
        if action not in ["enter_long", "enter_short", "exit_long", "exit_short"]:
            raise HTTPException(status_code=400, detail="Недопустимое действие")

        WebhookStrategy.last_signal_action = action
        WebhookStrategy.last_signal_ticker = ticker

        print(f"Получен сигнал: action={action}, ticker={ticker}, contracts={contracts}")
        return {"status": "success", "action": action, "ticker": ticker, "contracts": contracts}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Метод обязателен для реализации, но не используется в этой стратегии.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Вход в позиции на основе сигнала.
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
        Выход из позиций на основе сигнала.
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
