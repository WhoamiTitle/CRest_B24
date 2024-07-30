async def add_test_contacts(bitrix):
    num_contacts = 46
    contact_requests = []

    for i in range(num_contacts):
        contact_request = {
            "method": "crm.contact.add",
            "params": {
                "FIELDS": {
                    "NAME": f"Vitalic{i}",
                    "LAST_NAME": f"Vitalevich{i}"
                }
            }
        }
        contact_requests.append(contact_request)

    incorrect_request_index = 10
    incorrect_request = {
        "method": "crm.contact.add",
        "params": {
            "FIELDS": "NAME"
        }
    }
    contact_requests.insert(incorrect_request_index, incorrect_request)

    
    batch_response = await bitrix.call_batch(contact_requests, halt=True)

    
    contact_list_response = await bitrix.get_list("crm.contact.list")

    return {"batch_response": batch_response, "contact_list_response": contact_list_response}
    # return {"batch_response": batch_response}
