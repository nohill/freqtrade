class WebhookStrategy(IStrategy):
    """
    Стратегия, основанная на сигналах TradingView.
    """

    # Переменные для хранения последнего сигнала
    last_signal_action: Optional[str] = None
    last_signal_ticker: Optional[str] = None
    last_signal_contracts: Optional[float] = None

    def handle_signal(self, action: str, ticker: str, contracts: float):
        """
        Обрабатывает сигнал, переданный через API.
        """
        self.last_signal_action = action
        self.last_signal_ticker = ticker
        self.last_signal_contracts = contracts
        print(f"Получен сигнал: {action}, {ticker}, {contracts}")

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Пример входа на основе сигнала.
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
        Пример выхода на основе сигнала.
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
