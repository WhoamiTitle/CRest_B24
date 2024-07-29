import os
import sys
import json

# Получаем путь к корневой директории проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from bitrix24_crest import BitrixCrest

def main():
    crest = BitrixCrest()
    
    # Данные для нового контакта
    new_contact_data = {
        'FIELDS': {
            "NAME": "Илья",
            "LAST_NAME": "Петров",
            "PHONE": [
                {
                    "VALUE": "555888",
                    "VALUE_TYPE": "WORK"
                }
            ],
            "EMAIL": [
                {
                    "VALUE": "in78sdfv123@example.com",
                    "VALUE_TYPE": "WORK"
                }
            ]
        }
    }

    # Запрос на добавление нового контакта
    add_contact_result = crest.call('crm.contact.add', new_contact_data)
    print('Add Contact Result:')
    print(json.dumps(add_contact_result, indent=4))

    if 'result' in add_contact_result:
        new_contact_id = add_contact_result['result']
        
        # Запрос для получения данных о добавленном контакте
        batch_data = {
            'get_contact': {
                'method': 'crm.contact.get',
                'params': {"id": new_contact_id}
            }
        }
        batch_result = crest.call_batch(batch_data)
        print('Batch Result:')
        print(json.dumps(batch_result, indent=4))
    else:
        print('Failed to add contact.')

if __name__ == '__main__':
    main()
