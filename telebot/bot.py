import datetime
import matplotlib.pyplot as plt
import requests
from config import TOKEN, APIData
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar
from logger import logger
import telebot
from telebot import types

bot = telebot.TeleBot(TOKEN)

api_data = APIData()


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Национальный банк", "Альфа банк", "Беларусбанк")

    bot.send_message(
        message.chat.id,
        "Привет, чтобы воспользоваться функционалом "
        "бота сперва выберите банк из меню снизу.",
        reply_markup=markup,
    )


@bot.message_handler(
    func=lambda message: message.text
                         in ("Национальный банк", "Альфа банк", "Беларусбанк")
)
def choose_bank(message):
    api_data.bank = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if api_data.bank == 'Альфа банк':
        markup.add('USD', 'EUR', 'RUB')
    elif api_data.bank == 'Беларусбанк':
        markup.add('USD', 'EUR', 'CNY', 'RUB')
    else:
        markup.add('USD', 'EUR', 'GBP', 'JPY')

    bot.send_message(message.chat.id, f"Ты выбрал {message.text}."
                                      " Теперь выбери нужную тебе валюту ниже.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in (
        'USD', 'EUR', 'GBP', 'JPY', 'RUB', 'CNY', 'Национальный банк', 'Альфа банк', 'Беларусбанк'))
def choose_currency(message):
    if len(message.text) <= 4:
        api_data.currency = message.text
    else:
        api_data.bank = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if api_data.bank == "Альфа банк":
        markup.add(
            "Курс на текущий день", "Выбрать другой банк", "Выбрать другую валюту"
        )
    elif api_data.bank == "Беларусбанк":
        markup.add(
            "Курс на текущий день",
            "Курс на выбранный день",
            "Выбрать другой банк",
            "Выбрать другую валюту",
        )
    else:
        markup.add(
            "Курс на текущий день",
            "Курс на выбранный день",
            "Собрать статистику",
            "Выбрать другой банк",
            "Выбрать другую валюту",
        )

    if api_data.bank is None:
        bot.send_message(message.chat.id, "Выберите банк")
        bot.register_next_step_handler(message, choose_bank)
    else:
        bot.send_message(
            message.chat.id,
            f"Выбранная валюта: {api_data.currency}." f"  Выбранный банк: {api_data.bank}.",
            reply_markup=markup,
        )


@bot.message_handler(func=lambda message: message.text == "Курс на текущий день")
def choose_currency_for_now(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if api_data.bank == "Альфа банк":
        markup.add(
            "Курс на текущий день", "Выбрать другой банк", "Выбрать другую валюту"
        )
        data = requests.get(
            f'http://127.0.0.1:8000/alfabank/{api_data.currency}/')
        bot.send_message(message.chat.id,
                         f"{api_data.bank} - {api_data.currency} на {str(datetime.datetime.now())[:10]}")
        if len(data.json()) > 0:
            try:
                data.json()['sellRate']
            except:
                bot.send_message(
                    message.chat.id,
                    f"Нет такой валюты",
                    reply_markup=markup,
                )
            else:
                bot.send_message(
                    message.chat.id, f"Курс продажи: {data.json()['sellRate']}"
                )
                bot.send_message(
                    message.chat.id,
                    f"Курс покупки: {data.json()['buyRate']}",
                    reply_markup=markup,
                )
        else:
            bot.send_message(
                message.chat.id, f"Нет данных на данный момент", reply_markup=markup
            )
    elif api_data.bank == "Беларуcбанк":
        markup.add(
            "Курс на текущий день",
            "Курс на выбранный день",
            "Выбрать другой банк",
            "Выбрать другую валюту",
        )
    else:
        markup.add(
            "Курс на текущий день",
            "Курс на выбранный день",
            "Собрать статистику",
            "Выбрать другой банк",
            "Выбрать другую валюту",
        )

    if api_data.bank == "Национальный банк":
        data = requests.get(
            f'http://127.0.0.1:8000/national_bank/{api_data.currency}/{str(datetime.datetime.now())[:10]}')
        bot.send_message(message.chat.id,
                         f"{api_data.bank} - {api_data.currency} на {str(datetime.datetime.now())[:10]}")

        if api_data.currency not in ('USD', 'EUR', 'GBP', 'JPY'):
            bot.send_message(message.chat.id, f"Нет такой валюты", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Курс: {data.json()['exchange']}", reply_markup=markup)

    elif api_data.bank == 'Беларусбанк':
        data = requests.get(
            f'http://127.0.0.1:8000/belarus_bank/{api_data.currency}/{str(datetime.datetime.now())[:10]}')
        bot.send_message(message.chat.id,
                         f"{api_data.bank} - {api_data.currency} на {str(datetime.datetime.now())[:10]}")
        if api_data.currency not in ('USD', 'EUR', 'CNY', 'RUB'):
            bot.send_message(message.chat.id, f"Нет такой валюты", reply_markup=markup)
        elif len(data.json()) > 0:
            bot.send_message(message.chat.id, f"Курс продажи: {data.json()[0][api_data.currency + 'CARD_in']}")
            bot.send_message(message.chat.id, f"Курс покупки: {data.json()[0][api_data.currency + 'CARD_out']}",
                             reply_markup=markup)
        else:
            bot.send_message(
                message.chat.id, f"Нет данных на данный момент", reply_markup=markup
            )


@bot.message_handler(func=lambda message: message.text == "Выбрать другой банк")
def choose_another_bank(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Национальный банк', 'Альфа банк', 'Беларусбанк')
    bot.send_message(message.chat.id, f"Выберите банк из меню снизу.", reply_markup=markup)
    bot.register_next_step_handler(message, choose_currency)


@bot.message_handler(func=lambda message: message.text == "Выбрать другую валюту")
def choose_another_currency(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if api_data.bank == 'Альфа банк':
        markup.add('USD', 'EUR', 'RUB')
    elif api_data.bank == 'Беларусбанк':
        markup.add('USD', 'EUR', 'CNY', 'RUB')
    else:
        markup.add('USD', 'EUR', 'GBP', 'JPY')
    bot.send_message(message.chat.id, f"Выберите нужную валюту снизу.", reply_markup=markup)
    bot.register_next_step_handler(message, choose_currency)


@bot.message_handler(func=lambda message: message.text == "Курс на выбранный день")
def choose_date_from_calendar(message):
    bot.send_message(message.chat.id, f"Должен быть календарь")
    calendar, step = DetailedTelegramCalendar(max_date=datetime.date.today()).build()
    bot.send_message(message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar(
        max_date=datetime.date.today()
    ).process(c.data)
    if not result and key:
        bot.edit_message_text(
            f"Select {LSTEP[step]}",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=key,
        )
    elif result:
        api_data.date = result
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if api_data.bank == "Беларуcбанк":
            markup.add(
                "Курс на текущий день",
                "Курс на выбранный день",
                "Выбрать другой банк",
                "Выбрать другую валюту",
            )
        else:
            markup.add(
                "Курс на текущий день",
                "Курс на выбранный день",
                "Собрать статистику",
                "Выбрать другой банк",
                "Выбрать другую валюту",
            )

        if api_data.bank == "Национальный банк":
            data = requests.get(
                f'http://127.0.0.1:8000/national_bank/{api_data.currency}/{api_data.date}')
            bot.send_message(c.message.chat.id,
                             f"{api_data.bank} - {api_data.currency} на {api_data.date}")
            if api_data.currency not in ('USD', 'EUR', 'GBP', 'JPY'):
                bot.send_message(c.message.chat.id, f"Нет такой валюты", reply_markup=markup)
            else:
                bot.send_message(c.message.chat.id, f"Курс: {data.json()['exchange']}", reply_markup=markup)
        elif api_data.bank == 'Беларусбанк':
            data = requests.get(
                f'http://127.0.0.1:8000/belarus_bank/{api_data.currency}/{api_data.date}')
            bot.send_message(c.message.chat.id,
                             f"{api_data.bank} - {api_data.currency} на {api_data.date}")

            if api_data.currency not in ('USD', 'EUR', 'CNY', 'RUB'):
                bot.send_message(c.message.chat.id, f"Нет такой валюты", reply_markup=markup)
            elif len(data.json()) > 0:
                bot.send_message(c.message.chat.id, f"Курс продажи: {data.json()[0][api_data.currency + 'CARD_in']}")
                bot.send_message(c.message.chat.id, f"Курс покупки: {data.json()[0][api_data.currency + 'CARD_out']}",
                                 reply_markup=markup)
            else:
                bot.send_message(c.message.chat.id, f"Нет данных на данный момент", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Собрать статистику")
def choose_data(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        'Курс на текущий день',
        'Курс на выбранный день',
        'Собрать статистику',
        'Выбрать другой банк',
        'Выбрать другую валюту')
    data = requests.get(
        f'http://127.0.0.1:8000/statistic/{api_data.currency}')
    plt.plot([i for i in range(1, 33)], data.json()['cur_officialrate_list'], color='purple', marker='o', markersize=7)
    plt.xlabel('Дни')
    plt.ylabel(f'Курс {api_data.currency}')
    plt.title(f'Статистика за последние 30 дней')

    plt.savefig("foo.png")
    photo = open(f'{message.chat.id}.png', 'rb')
    bot.send_photo(message.chat.id, photo, reply_markup=markup)
    bot.register_next_step_handler(message, choose_currency_for_now)


@bot.message_handler(func=lambda message: message.text not in (
        'USD', 'EUR', 'GBP', 'JPY', 'RUB', 'CNY', 'Национальный банк', 'Альфа банк', 'Беларусбанк'))
def everything(message):
    bot.send_message(message.chat.id, f" Что это? "
                                      f"Следуйте по шагам.")
    logger.debug(f"don't correct choose. Your choose is {message.text} -CHAT.ID{message.chat.id}")
