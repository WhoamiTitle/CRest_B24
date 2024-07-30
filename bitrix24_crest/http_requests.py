import requests
from requests.exceptions import HTTPError
from logging_module.logging_utility import log
from logging_module.schemes import LogMessage, log_en


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
    except requests.exceptions.HTTPError as error:
        log(LogMessage(
            time=None,
            heder=f"Ошибка выполнения запроса. {error.response.status_code}",
            heder_dict=error.args,
            body={
                "url": url,
                "json_data": json_data,
                "response": error.response.json() if error.response else "No response"
            },
            level=log_en.ERROR
        ))
        raise error
    except Exception as error:
        log(LogMessage(
            time=None,
            heder="Неизвестная ошибка.",
            heder_dict=error.args,
            body={
                "url": url,
                "json_data": json_data
            },
            level=log_en.ERROR
        ))
        raise error





# def send_http_post_request_url_builder(url: str, params: dict):
#     """
#     Отправляет POST-запрос с параметрами.
#     """
#     try:
#         response = requests.post(url, json=params)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         raise e
