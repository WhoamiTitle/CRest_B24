import requests
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

def send_http_post_request(url: str, json_data: dict):
    """
    Отправляет POST-запрос.
    """
    try:
        response = requests.post(url, json=json_data)
        if response.status_code == 302:
            new_url = response.headers['Location']
            response = requests.post(new_url, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка выполнения запроса: {e}")
        raise e

def send_http_post_request_url_builder(url: str, params: dict):
    """
    Отправляет POST-запрос с параметрами.
    """
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка выполнения запроса: {e}")
        raise e
