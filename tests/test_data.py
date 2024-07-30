async def add_test_contacts(bitrix):
    res = await bitrix.call("crm.contact.add",
                            {
                                "FIELDS": {
                                    "NAME": "Иван",
                                    "LAST_NAME": "Петров",
                                    "EMAIL": [
                                        {
                                            "VALUE": "mail@example.com",
                                            "VALUE_TYPE": "WORK"
                                        }
                                    ],
                                    "PHONE": [
                                        {
                                            "VALUE": "555888",
                                            "VALUE_TYPE": "WORK"
                                        }
                                    ]
                                }
                            })

    res1 = await bitrix.call_batch(
        [
            {
                "method": "crm.contact.add",
                "params": {
                    "FIELDS": {
                        "NAME": "Иван1",
                        "LAST_NAME": "Петров1"
                    }
                }
            },
            {
                "method": "crm.contact.add",
                "params": {
                    "FIELDS": {
                        "NAME": "Иван2",
                        "LAST_NAME": "Петров2"
                    }
                }
            }
        ])

    arr = []
    for i in range(46):
        arr.append(
            {
                "method": "crm.contact.add",
                "params": {
                    "FIELDS": {
                        "NAME": f"Иван{i}",
                        "LAST_NAME": f"Петров{i}"
                    }
                }
            }
        )

    arr.insert(10,
               {
                   "method": "crm.contact.add",
                   "params": {
                       "FIELDS": "NAME"
                   }
               }
               )
    res2 = await bitrix.call_batch(arr, True)

    res3 = await bitrix.call("crm.contact.list")

    return {"res": res, "res1": res1, "res2": res2, "res3": res3}
