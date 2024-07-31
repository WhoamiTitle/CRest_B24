async def add_test_contacts(bitrix):
    num_contacts = 100
    contact_requests = {}

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
        contact_requests[str(i)]=contact_request


    
    batch_response = bitrix.call_batch(contact_requests, halt=True)
    listTemp =  bitrix.get_list("crm.contact.list")
    print(listTemp)
    return {"batch_response": batch_response}
   