from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

class WebhookStrategy(IStrategy):
    # ROI (Return on Investment) настройка
    minimal_roi = {
        "0": 0.1  # Take profit через 10%
    }

    # Стоп-лосс
    stoploss = -0.2  # Убыток максимум 20%

    # Таймфрейм
    timeframe = '5m'

    # Указываем, что стратегия будет работать только с вебхуками
    use_custom_stoploss = False
    process_only_new_candles = True

    # Пользовательские данные для сигналов
    custom_info = {}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Добавление индикаторов. Пусто, так как мы полагаемся на вебхуки.
        """
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика покупки на основе сигналов.
        """
        dataframe['buy'] = 0
        # Устанавливаем сигнал на покупку, если 'buy' передан через webhook
        if 'buy' in self.custom_info:
            dataframe.loc[dataframe.index[-1], 'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Логика продажи на основе сигналов.
        """
        dataframe['sell'] = 0
        # Устанавливаем сигнал на продажу, если 'sell' передан через webhook
        if 'sell' in self.custom_info:
            dataframe.loc[dataframe.index[-1], 'sell'] = 1
        return dataframe
