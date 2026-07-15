import json
import os

def get_shop_info():
    # config.json ကိုဖတ်မယ်
    path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"shop_name": "MY POS SHOP", "address": "", "phone": ""}
