import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import json
from bitrix24_crest.bitrixcrest import BitrixCrest

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
