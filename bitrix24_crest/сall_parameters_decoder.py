from fastapi import Request
import re
from urllib.parse import unquote
from typing import Union

def call_parameters_decoder(string: str) -> dict:
    """
    Декодирует строку параметров запроса в словарь.
    :param string: Строка параметров запроса
    :return: Словарь параметров
    """
    res = {}
    arr = string.split("&")
    

    for param in arr:
        key, value = map(unquote, param.split('='))
        keys = list(filter(bool, re.split("[\[\]]",key)))
        last_dict = res

        for i in range(len(keys)):
            if i == len(keys) - 1:
                last_dict[keys[i]] = value
            else:
                if keys[i] not in last_dict:
                    last_dict[keys[i]] = {}
                last_dict = last_dict[keys[i]]

    return res


async def decode_body_request(request: Request) -> Union[dict, None]:
    string = str(await request.body())[2:-1]
    if string:
        return call_parameters_decoder(string)
    else:
        return None


# Пример 
# query_string = "FIELDS[NAME]=Виктор&FIELDS[SECOND_NAME]=Петрович&FIELDS[LAST_NAME]=Нагиев"
# decoded_params = call_parameters_decoder(query_string)
# print(decoded_params)
