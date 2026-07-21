# erp_core/rpc_engine.py
import json
import time
from typing import Dict, Any
from supabase import Client
try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception
from .config import log_error

class RPCEngine:
    SUCCESS_VALUES = [True, "true", "success", "completed", "ok", "done"]
    MAX_RETRY = 3

    @staticmethod
    def normalize_response(raw) -> Dict[str, Any]:
        if raw is None: return {"success": False, "message": "Empty RPC response", "data": None}
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: return {"success": False, "message": f"Malformed JSON: {raw}", "data": None}
        if isinstance(raw, list): raw = raw[0] if raw else {}
        if isinstance(raw, dict) and "response_json" in raw: raw = raw["response_json"]
        if isinstance(raw, dict):
            status_indicator = raw.get("success") if raw.get("success") is not None else raw.get("status")
            success = str(status_indicator).lower() in [str(v) for v in RPCEngine.SUCCESS_VALUES] or status_indicator is True
            return {"success": success, "message": raw.get("message", "Operation completed"), "data": raw.get("data", raw)}
        return {"success": True, "message": "Operation completed", "data": raw}

    @staticmethod
    def execute(client: Client, rpc_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        last_error = None
        for attempt in range(RPCEngine.MAX_RETRY):
            try:
                response = client.rpc(rpc_name, payload).execute()
                return RPCEngine.normalize_response(response.data)
            except (APIError, ConnectionError, TimeoutError) as e:
                last_error = e
                if attempt < RPCEngine.MAX_RETRY - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_error = e
                break
        log_error(message="RPC Execution Failed", rpc=rpc_name, payload=payload, exception=last_error)
        return {"success": False, "message": str(last_error) if last_error else "RPC Failed", "data": None}
