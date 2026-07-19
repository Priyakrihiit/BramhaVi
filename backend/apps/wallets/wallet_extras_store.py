import os
import json
import uuid
from datetime import datetime, date

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallet_extras.json")

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def get_initial_store():
    return {
        "soft_deleted_wallets": [],
        "subscriptions": {},
        "coupons": {},
        "invoices": {},
        "fine_grained_transactions": {}
    }

def read_store():
    if not os.path.exists(DATA_FILE_PATH):
        write_store(get_initial_store())
        return get_initial_store()
    try:
        with open(DATA_FILE_PATH, "r") as f:
            data = json.load(f)
            # Ensure all keys exist
            initial = get_initial_store()
            for key, val in initial.items():
                if key not in data:
                    data[key] = val
            return data
    except Exception:
        return get_initial_store()

def write_store(data):
    try:
        with open(DATA_FILE_PATH, "w") as f:
            json.dump(data, f, cls=DateTimeEncoder, indent=2)
    except Exception as e:
        print(f"Error writing to wallet_extras.json: {e}")

# Wallet Soft Delete API
def soft_delete_wallet_id(wallet_id: str) -> bool:
    store = read_store()
    w_id = str(wallet_id)
    if w_id not in store["soft_deleted_wallets"]:
        store["soft_deleted_wallets"].append(w_id)
        write_store(store)
        return True
    return False

def restore_wallet_id(wallet_id: str) -> bool:
    store = read_store()
    w_id = str(wallet_id)
    if w_id in store["soft_deleted_wallets"]:
        store["soft_deleted_wallets"].remove(w_id)
        write_store(store)
        return True
    return False

def is_wallet_id_soft_deleted(wallet_id: str) -> bool:
    store = read_store()
    return str(wallet_id) in store["soft_deleted_wallets"]

# Subscriptions API
def get_user_subscription(user_id: str) -> dict:
    store = read_store()
    u_id = str(user_id)
    return store["subscriptions"].get(u_id)

def set_user_subscription(user_id: str, plan_data: dict):
    store = read_store()
    u_id = str(user_id)
    store["subscriptions"][u_id] = plan_data
    write_store(store)

# Coupons API
def get_all_coupons() -> dict:
    store = read_store()
    return store["coupons"]

def get_coupon_by_code(code: str) -> dict:
    store = read_store()
    return store["coupons"].get(code.upper().strip())

def set_coupon(code: str, coupon_data: dict):
    store = read_store()
    store["coupons"][code.upper().strip()] = coupon_data
    write_store(store)

def delete_coupon_by_code(code: str) -> bool:
    store = read_store()
    c_code = code.upper().strip()
    if c_code in store["coupons"]:
        del store["coupons"][c_code]
        write_store(store)
        return True
    return False

# Invoices API
def get_all_invoices() -> dict:
    store = read_store()
    return store["invoices"]

def get_invoice_by_id(invoice_id: str) -> dict:
    store = read_store()
    return store["invoices"].get(str(invoice_id))

def set_invoice(invoice_id: str, invoice_data: dict):
    store = read_store()
    store["invoices"][str(invoice_id)] = invoice_data
    write_store(store)

# Fine grained transaction type mapping
def set_fine_grained_tx(tx_id: str, tx_type: str):
    store = read_store()
    store["fine_grained_transactions"][str(tx_id)] = tx_type
    write_store(store)

def get_fine_grained_tx(tx_id: str) -> str:
    store = read_store()
    return store["fine_grained_transactions"].get(str(tx_id), "UNKNOWN")
