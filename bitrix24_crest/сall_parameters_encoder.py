from urllib.parse import quote


def call_parameters_encoder(params: dict) -> str:

    list_params = []
    for key, value in params.items():
        if (type(value)==list or type(value)==dict):
            list_params.extend([f"{key}{for_value}" for for_value in call_parameters_encoder_recursion(value)])
        else:
            list_params.append(f"{key}={quote(str(value))}")

    return "&".join(list_params)

def call_parameters_encoder_recursion(params) -> list:

    list_params = []
    if isinstance(params, dict):        
        for key, value in params.items():
            if isinstance(value, (list,dict)):
                list_params.extend([f"[{str(key)}]{for_value}" for for_value in call_parameters_encoder_recursion(value)])
            else:
                list_params.append(f"[{key}]={quote(str(value))}")
    else:
        for key, value in enumerate(params):
            if isinstance(value, (list,dict)):
                list_params.extend([f"[{str(key)}]{for_value}" for for_value in call_parameters_encoder_recursion(value)])
            else:
                list_params.append(f"[{key}]={quote(str(value))}")
    return list_params


