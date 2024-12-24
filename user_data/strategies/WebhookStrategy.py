from freqtrade.strategy import IStrategy
from pandas import DataFrame

class WebhookStrategy(IStrategy):
    stoploss = -0.99
    timeframe = "5m"
    minimal_roi = {"0": 100}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
