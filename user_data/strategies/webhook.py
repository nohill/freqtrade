from fastapi import APIRouter, HTTPException
from freqtrade.strategy import IStrategy
from pandas import DataFrame
from typing import Optional

# Создаем роутер
router = APIRouter()

class WebhookStrategy(IStrategy):
    """
    Стратегия, полностью основанная на сигналах от TradingView.
    """

    # Настройки стратегии
    timeframe = "5m"
    can_short = True
    minimal_roi = {"0": 0.01}
    stoploss = -0.10
    startup_candle_count = 0

    # Переменные для хранения сигналов
    last_signal_action: Optional[str] = None
    last_signal_ticker: Optional[str] = None

    @staticmethod
    @router.post("/tradingview")
    async def handle_signal(signal: dict):
        """
        Обработка сигналов от TradingView.
        """
        action = signal.get("action")
        ticker = signal.get("ticker")
        contracts = signal.get("contracts")

        if action not in ["enter_long", "enter_short", "exit_long", "exit_short"]:
            raise HTTPException(status_code=400, detail="Недопустимое действие")

        WebhookStrategy.last_signal_action = action
        WebhookStrategy.last_signal_ticker = ticker

        print(f"Получен сигнал: action={action}, ticker={ticker}, contracts={contracts}")
        return {"status": "success", "action": action, "ticker": ticker, "contracts": contracts}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Метод обязателен для реализации, но не используется.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика входа на основе сигналов.
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
        Логика выхода на основе сигналов.
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

    @classmethod
    def register_routes(cls, app):
        """
        Метод для регистрации маршрутов FastAPI.
        """
        app.include_router(router, prefix="/api/v1")
