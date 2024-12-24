from freqtrade.strategy import IStrategy
from freqtrade.rpc.rpc_manager import RPC
from freqtrade.rpc.api_server.api_schemas import ForceEnterPayload
from pandas import DataFrame

import asyncio
import json
import logging
import re
from collections.abc import Callable, Coroutine
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import partial, wraps
from html import escape
from itertools import chain
from math import isnan
from threading import Thread
from typing import Any, Literal, Optional

from tabulate import tabulate
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.helpers import escape_markdown

from freqtrade.__init__ import __version__
from freqtrade.constants import DUST_PER_COIN, Config
from freqtrade.enums import MarketDirection, RPCMessageType, SignalDirection, TradingMode
from freqtrade.exceptions import OperationalException
from freqtrade.misc import chunks, plural
from freqtrade.persistence import Trade
from freqtrade.rpc import RPC, RPCException, RPCHandler
from freqtrade.rpc.rpc_types import RPCEntryMsg, RPCExitMsg, RPCOrderMsg, RPCSendMsg
from freqtrade.util import (
    dt_from_ts,
    dt_humanize_delta,
    fmt_coin,
    fmt_coin2,
    format_date,
    round_value,
)


class WebhookStrategy(IStrategy):
    def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._rpc = RPC()

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
            trade = self._rpc._rpc_force_entry(
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
