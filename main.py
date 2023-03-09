"""Telegram Bot Api."""
import logging
import os
import random
import sys
import time, datetime


import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)

DEBUG = False


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

UTC = 3
UTC = datetime.timedelta(hours=UTC)

RETRY_PERIOD_KOEF = 60
PERIOD_FROM_MINS = 30
PERIOD_TO_MINS = 90

URL_CAT = 'https://api.thecatapi.com/v1/images/search'
URL_DOG = 'https://api.thedogapi.com/v1/images/search'
CAPIBARA_URL = 'https://api.capy.lol/v1/capybara?json=true' 

MORNING_MESSAGE = 'Привет! Посмотри, каких красавцев я тебе сегодня подобрал!'
CAPTION_MESSAGE = 'готов тебя порадовать!'


class Animal:
    def __init__(self, name, url, parse_key) -> None:
        self.name = name
        self.url = url
        self.parse_key = parse_key

    def __str__(self) -> str:
        return self.name

def check_tokens():
    """Проверка токенов."""
    tokens = [TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    logger.debug('Проверяем токены')
    return all(tokens)

def is_day():
    current_time_utc = datetime.datetime.utcnow()
    current_time_local = current_time_utc + UTC
    current_hour_local = current_time_local.hour
    print(f'сейчас {current_hour_local} часов')

    return current_hour_local < 22 and current_hour_local > 9


def get_new_response(animal):
    """Отправка запроса и получение ответа от эндпоинтов."""
    current_url = animal.url

    try:
        response = requests.get(current_url)
        response = response.json()
        image_animal = response[animal.parse_key].get('url')
        logger.debug('Фото получено!')
        return image_animal
    
    except Exception:
        logger.error('URL - недоступен')
        raise Exception(f'{animal} пока спит!')


def send_message(bot, message, caption=None):
    """Отправка сообщения ботом."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message, caption)
        logger.debug(f'Отправленно сообщение: {message}')
    except Exception:
        logger.error('Сбой в отправке сообщения!')
        raise Exception('Сбой в отправке сообщения!')


def send_photo(bot, image_animal, caption=None):
    """Отправка Фотографии ботом."""
    try:
        bot.send_photo(TELEGRAM_CHAT_ID, image_animal, caption)
        logger.debug(f'Отправленно фото: {image_animal}')
        logger.debug(f'Отправленн коммент: {caption}')

    except Exception:
        logger.error('Сбой в отправке фото!')
        raise Exception('Сбой в отправке фото!')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Нет переменных окружения!')
        raise SystemExit('Программа принудительно остановлена.')
    
    cat = Animal('Котик', URL_CAT, 0)
    dog = Animal('Пёсик', URL_DOG, 0)
    capibara = Animal('Капибара', CAPIBARA_URL, 'data')

    animal_choices = [cat, dog, capibara]

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Запускаем бота')
    count_message = 0

    while True:
        try:
            if is_day():
                if count_message == 0:
                    send_message(bot, MORNING_MESSAGE)  # Утреннее сообщение
                animal = random.choice(animal_choices)
                logger.debug(f'Наш зверек это - {animal}')

                image_animal = get_new_response(animal)
                if image_animal:
                    send_photo(bot, image_animal, caption=animal.name + ' ' + CAPTION_MESSAGE)
                    count_message += 1
            else:
                count_message = 0

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            retry_period = RETRY_PERIOD_KOEF * random.randint(
                PERIOD_FROM_MINS,
                PERIOD_TO_MINS
            )
            new_time = datetime.datetime.utcnow()
            period = datetime.timedelta(seconds=retry_period)
            new_time = new_time + period + UTC
            logger.debug(f'Ждать {retry_period/60} минут,'
                         f' новое сообщение в {new_time}'
                         )
            time.sleep(retry_period)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(
        logging.Formatter('%(asctime)s, [%(levelname)s], %(message)s')
    )
    logger.addHandler(handler)
    main()