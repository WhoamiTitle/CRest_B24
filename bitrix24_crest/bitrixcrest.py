import os
import json
import functools
import logging
import requests
from bitrix24_crest.http_requests import send_http_post_request
import bitrix24_crest.settings as settings


# Настройка логирования
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ExceptionCallError(Exception):
    error: str

def error_catcher(name: str):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if "error" in result:
                    logger.error(f"Ошибка при выполнении декоратора error_catcher, name: {name}. Аргументы: {args}, Ключевые слова: {kwargs}, Результат: {result}")
                    raise ExceptionCallError(error=result["error"])
                return result
            except ExceptionCallError as error:
                raise error
            except Exception as error:
                logger.error(f"Ошибка при выполнении декоратора error_catcher, name: {name}. Аргументы: {args}, Ключевые слова: {kwargs}, Ошибка: {error}")
                raise ExceptionCallError(error="undefined")
        return inner
    return wrapper

def auto_refresh_token():
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if "error" in result and result["error"] == "expired_token":
                    # Вызов функции обновления токена
                    auth_result = func.__self__.get_new_auth(*args, **kwargs)
                    if "error" not in auth_result:
                        result = func(*args, **kwargs)
                    else:
                        raise ExceptionCallError(error="failed_to_refresh_token")
                return result
            except ExceptionCallError as error:
                raise error
            except Exception as error:
                logger.error(f"Ошибка при выполнении декоратора auto_refresh_token. Аргументы: {args}, Ключевые слова: {kwargs}, Ошибка: {error}")
                raise ExceptionCallError(error="undefined")
        return inner
    return wrapper

class BitrixCrest:
    BATCH_COUNT = 50
    TYPE_TRANSPORT = 'json'

    def __init__(self):
        self.C_REST_WEB_HOOK_URL = settings.C_REST_WEB_HOOK_URL
        self.C_REST_CLIENT_ID = settings.C_REST_CLIENT_ID
        self.C_REST_CLIENT_SECRET = settings.C_REST_CLIENT_SECRET
        self.settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')

    def get_app_settings(self):
        if self.C_REST_WEB_HOOK_URL:
            return {'client_endpoint': self.C_REST_WEB_HOOK_URL, 'is_web_hook': 'Y'}

        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
            return data if data else False
        return False

    def set_setting_data(self, app_settings):
        with open(self.settings_file, 'w') as f:
            json.dump(app_settings, f)
        return True

    def set_app_settings(self, app_settings, is_install=False):
        old_data = self.get_app_settings()
        if not is_install and old_data and isinstance(old_data, dict):
            app_settings.update(old_data)
        return self.set_setting_data(app_settings)

    @error_catcher("call")
    @auto_refresh_token()
    def call(self, method, params=None, this_auth=False):
        app_settings = self.get_app_settings()
        if not app_settings:
            logger.error('No application settings found.')
            return {'error': 'no_install_app', 'error_information': 'error install app, pls install local application'}

        if this_auth:
            url = 'https://oauth.bitrix.info/oauth/token/'
        else:
            url = f"{app_settings['client_endpoint']}{method}.{self.TYPE_TRANSPORT}"
            if not app_settings.get('is_web_hook') or app_settings['is_web_hook'] != 'Y':
                if params is None:
                    params = {}
                params['auth'] = app_settings['access_token']

        return send_http_post_request(url, params)

    @error_catcher("get_new_auth")
    @auto_refresh_token()
    def get_new_auth(self, method, params):
        app_settings = self.get_app_settings()
        if not app_settings:
            return {}

        auth_params = {
            'client_id': app_settings['C_REST_CLIENT_ID'],
            'grant_type': 'refresh_token',
            'client_secret': app_settings['C_REST_CLIENT_SECRET'],
            'refresh_token': app_settings['refresh_token']
        }
        new_data = self.call('', auth_params, this_auth=True)
        if self.set_app_settings(new_data):
            return self.call(method, params)
        return {}

    @error_catcher("call_batch")
    @auto_refresh_token()
    def call_batch(self, ar_data, halt=0):
        if isinstance(ar_data, dict):
            ar_data_rest = {'cmd': {}}
            i = 0
            for key, data in ar_data.items():
                if 'method' in data and i < self.BATCH_COUNT:
                    i += 1
                    ar_data_rest['cmd'][key] = data['method']
                    if 'params' in data:
                        ar_data_rest['cmd'][key] += '?' + requests.compat.urlencode(data['params'])
            if ar_data_rest['cmd']:
                ar_data_rest['halt'] = halt
                return self.call('batch', ar_data_rest)
        return {}
