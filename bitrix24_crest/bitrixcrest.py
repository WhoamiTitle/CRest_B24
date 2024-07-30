
import json
import functools
import requests



from .http_requests import send_http_post_request
from .settings import C_REST_WEB_HOOK_URL, C_REST_CLIENT_SECRET,C_REST_CLIENT_ID


from logging_module.logging_utility import log
from logging_module.schemes import LogMessage, log_en



class ExceptionCallError(Exception):
    error: str

def error_catcher(name: str):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if "error" in result:
                    error_message = f"Ошибка при выполнении декоратора error_catcher, name: {name}. Аргументы: {args}, Ключевые слова: {kwargs}, Результат: {result}"
                    log(LogMessage(
                        time=None,
                        heder="Ошибка при выполнении вызова",
                        heder_dict={"name": name, "args": args, "kwargs": kwargs},
                        body={"result": result},
                        level=log_en.ERROR
                    ))
                    raise ExceptionCallError(error=result["error"])
                return result   
            except ExceptionCallError as error:
                raise error      
            except Exception as error:
                error_message = f"Ошибка при выполнении декоратора error_catcher, name: {name}. Аргументы: {args}, Ключевые слова: {kwargs}, Ошибка: {error}"
                log(LogMessage(
                    time=None,
                    heder="Неизвестная ошибка при выполнении вызова",
                    heder_dict={"name": name, "args": args, "kwargs": kwargs},
                    body={"error": str(error)},
                    level=log_en.ERROR
                ))
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
            
            except requests.HTTPError as http_err:
                if http_err.response.status_code == 401:
                    log(LogMessage(
                        time=None,
                        heder="Получен статус 401, пытаемся обновить токен",
                        heder_dict={"args": args, "kwargs": kwargs},
                        body={"error": str(http_err)},
                        level=log_en.ERROR
                    ))                    
                    # Вызов функции обновления токена
                    auth_result = func.__self__.get_new_auth(*args, **kwargs)
                    if "error" not in auth_result:
                        result = func(*args, **kwargs)
                    else:
                        raise ExceptionCallError(error="failed_to_refresh_token")
                    return result
                else:
                    raise ExceptionCallError(error="undefined")
            
            except Exception as error:
                log(LogMessage(
                    time=None,
                    heder="Неизвестная ошибка при выполнении вызова",
                    heder_dict={"args": args, "kwargs": kwargs},
                    body={"error": str(error)},
                    level=log_en.ERROR
                ))
                raise ExceptionCallError(error="undefined")
        
        return inner
    
    return wrapper

class BitrixCrest:
    BATCH_COUNT = 50
    TYPE_TRANSPORT = 'json'

    def __init__(self):
        self.C_REST_WEB_HOOK_URL = C_REST_WEB_HOOK_URL
        self.C_REST_CLIENT_ID = C_REST_CLIENT_ID
        self.C_REST_CLIENT_SECRET = C_REST_CLIENT_SECRET
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
            error_message = 'No application settings found.'
            log(LogMessage(
                time=None,
                heder="Ошибка вызова",
                heder_dict={"method": method, "params": params, "this_auth": this_auth},
                body={"error": error_message},
                level=log_en.ERROR
            ))
            return {'error': 'no_install_app', 'error_information': 'error install app, pls install local application'}

        if this_auth:
            url = 'https://oauth.bitrix.info/oauth/token/'
        else:
            url = f"{app_settings['client_endpoint']}{method}.{self.TYPE_TRANSPORT}"
            if not app_settings.get('is_web_hook') or app_settings['is_web_hook'] != 'Y':
                if params is None:
                    params = {}
                params['auth'] = app_settings['access_token']
        try:
            result = send_http_post_request(url, params)
            log(LogMessage(
                time=None,
                heder="Успешный вызов метода",
                heder_dict={"method": method, "params": params, "url": url},
                body={"result": result},
                level=log_en.INFO
            ))
            return result
        except Exception as error:
            log(LogMessage(
                time=None,
                heder="Ошибка при вызове метода",
                heder_dict={"method": method, "params": params, "url": url},
                body={"error": str(error)},
                level=log_en.ERROR
            ))
            raise error

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
                log(LogMessage(
                    time=None,
                    heder="Вызов batch метода",
                    heder_dict={"ar_data_rest": ar_data_rest},
                    body=None,
                    level=log_en.INFO
                ))
                return self.call('batch', ar_data_rest)
        return {}
    
    async def get_list(self, method: str, params: dict = None) -> list:

        if params is None:
            params = {}

        # Установка по умолчанию 
        if "order" not in params:
            params["order"] = {"ID": "ASC"}
        else:
            if "ID" not in params["order"]:
                params["order"]["ID"] = "ASC"

        # Определение направления сортировки 
        is_id_order_normal = params["order"]["ID"] != "DESC"
        params["start"] = -1
        result = []
        last_id = None

        try:
            while True:
                params_copy = params.copy()
                if last_id:
                    filter_key = f"{'>' if is_id_order_normal else '<'}ID"
                    if "filter" in params_copy:
                        params_copy["filter"][filter_key] = str(last_id)
                    else:
                        params_copy["filter"] = {filter_key: str(last_id)}

                response = await self.call(method, params_copy)
                
                if 'error' in response:
                    log(LogMessage(
                        time=None,
                        heder="Ошибка при получении списка",
                        heder_dict={"method": method, "params": params_copy},
                        body={"error": response["error"]},
                        level=log_en.ERROR
                    ))
                    break

                result.extend(response["result"])

                if len(response["result"]) == 0:
                    break

                last_id = int(response["result"][-1]["ID"])

            log(LogMessage(
                time=None,
                heder="Успешное получение списка",
                heder_dict={"method": method, "params": params},
                body={"result": result},
                level=log_en.INFO
            ))
            
        except Exception as e:
            log(LogMessage(
                time=None,
                heder="Ошибка при вызове метода get_list",
                heder_dict={"method": method, "params": params},
                body={"error": str(e)},
                level=log_en.ERROR
            ))
            raise e

        return result
