import os
import pytz
import requests
import telebot
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_TOKEN = ""
OPENWEATHERMAP_TOKEN = ""
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={OPENWEATHERMAP_TOKEN}&units=metric&lang=ru"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Список для хранения ID чатов
chat_ids = []

def get_weather(days: int = 1) -> str:
    response = requests.get(WEATHER_URL)
    weather_data = response.json()

    city = weather_data["name"]
    weather_string = f"Прогноз погоды в {city}:\n\n"

    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        date_string = date.strftime("%d.%m.%Y")

        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={OPENWEATHERMAP_TOKEN}&units=metric&lang=ru")
        weather_data = response.json()

        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        weather_string += f"{date_string}: {description.capitalize()}, температура {temp}°C.\n"

    return weather_string

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in chat_ids:
        chat_ids.append(message.chat.id)
    send_weather_button(message)

def send_weather_button(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    current_weather_button = KeyboardButton("Получить текущий прогноз погоды")
    next_two_days_button = KeyboardButton("Получить прогноз погоды на 3 дня")
    next_week_button = KeyboardButton("Получить прогноз погоды на неделю")
    keyboard.add(current_weather_button, next_two_days_button, next_week_button)
    bot.send_message(chat_id=message.chat.id, text="Выберите, что вы хотите узнать о погоде:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Получить текущий прогноз погоды")
def on_today_weather_button_click(message):
    send_weather(message, days=1)

@bot.message_handler(func=lambda message: message.text == "Получить прогноз погоды на 3 дня")
def on_next_two_days_weather_button_click(message):
    send_weather(message, days=3)

@bot.message_handler(func=lambda message: message.text == "Получить прогноз погоды на неделю")
def on_next_week_weather_button_click(message):
    send_weather(message, days=7)

def send_weather(message, days=1):
    weather_text = get_weather(days)
    if message is not None:
        bot.send_message(chat_id=message.chat.id, text=weather_text)
    else:
        # Отправка погоды всем сохраненным пользователям
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=weather_text)

def schedule_weather() -> None:
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(send_weather, "cron", hour=14, minute=27, second=0, args=(None,))
    scheduler.start()

if __name__ == "__main__":
    schedule_weather()
    bot.polling(none_stop=True)
