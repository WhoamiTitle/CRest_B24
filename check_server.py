from bitrix24_crest import settings
from logging_module.schemes import LogMessage, log_en
from logging_module.logging_utility import log

def check_settings():
    if settings.C_REST_WEB_HOOK_URL == "" and (settings.C_REST_CLIENT_ID == "" or settings.C_REST_CLIENT_SECRET == ""):
        error_message = "Недостаточные настройки: необходимо указать C_REST_WEB_HOOK_URL, C_REST_CLIENT_ID, C_REST_CLIENT_SECRET"
        log_message = LogMessage(
            time=None,
            level=log_en.ERROR,
            heder="Проверка настроек",
            heder_dict={"C_REST_WEB_HOOK_URL:": settings.C_REST_WEB_HOOK_URL,
                        "C_REST_CLIENT_ID:": settings.C_REST_CLIENT_ID,
                        "C_REST_CLIENT_SECRET:": settings.C_REST_CLIENT_SECRET},
            body={"error": error_message}
        )
        log(log_message)
        raise Exception(error_message)
