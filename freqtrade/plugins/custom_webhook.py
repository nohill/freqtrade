from fastapi import APIRouter, HTTPException

def setup() -> None:
    """
    Метод `setup` вызывается автоматически при запуске бота.
    """
    router = APIRouter()

    @router.post("/tradingview")
    async def handle_signal(signal: dict):
        action = signal.get("action")
        ticker = signal.get("ticker")
        contracts = signal.get("contracts")

        if action not in ["enter_long", "enter_short", "exit_long", "exit_short"]:
            raise HTTPException(status_code=400, detail="Недопустимое действие")

        print(f"Получен сигнал: action={action}, ticker={ticker}, contracts={contracts}")
        return {"status": "success", "action": action, "ticker": ticker, "contracts": contracts}

    # Регистрируем маршрут в основном приложении FastAPI
    from freqtrade.rpc.api_server import api
    api.include_router(router)
