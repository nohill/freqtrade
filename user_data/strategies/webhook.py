# --- Импорты ---
from freqtrade.strategy import IStrategy  # Импорт интерфейса стратегии
from fastapi import FastAPI, HTTPException  # Для вебхуков
from pandas import DataFrame  # Для работы с данными
from typing import Optional  # Для опциональных аннотаций

# --- API для сигналов TradingView ---
app = FastAPI()

class WebhookStrategy(IStrategy):
    """
    Стратегия, полностью основанная на сигналах от TradingView через вебхук.
    """

    # Настройки стратегии
    timeframe = "5m"
    can_short = True
    minimal_roi = {"0": 0.01}  # ROI можно оставить минимальным, так как сигналы внешние
    stoploss = -0.10
    startup_candle_count = 0  # Не требует исторических данных

    # Переменные для хранения сигналов
    last_signal_action: Optional[str] = None
    last_signal_ticker: Optional[str] = None

    @staticmethod
    @app.post("/api/v1/tradingview")
    async def handle_signal(signal: dict):
        """
        Обработка сигналов от TradingView.
        """
        action = signal.get("action")
        ticker = signal.get("ticker")
        contracts = signal.get("contracts")

        if action not in ["enter_long", "enter_short", "exit_long", "exit_short"]:
            raise HTTPException(status_code=400, detail="Недопустимое действие")

        # Сохранение последнего сигнала
        WebhookStrategy.last_signal_action = action
        WebhookStrategy.last_signal_ticker = ticker

        print(f"Получен сигнал: action={action}, ticker={ticker}, contracts={contracts}")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Метод, обязателен для реализации, но в этой стратегии не используется.
        """
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика входа на основе последних сигналов.
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
        Логика выхода на основе последних сигналов.
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
