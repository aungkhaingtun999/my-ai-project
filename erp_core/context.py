# erp_core/context.py
import uuid
import streamlit as st
from dataclasses import dataclass, field

def generate_tx_id(prefix="TX"): return f"{prefix}-{uuid.uuid4().hex.upper()}"
generate_transaction_id = generate_tx_id

@dataclass
class ERPContext:
    current_user: Optional_user = None if "Optional" in globals() else None
    current_branch_id: int = 1
    current_warehouse_id: int = 1
    current_counter_id: int = 1
    current_currency: str = "MMK"
    fiscal_year: str = "2026"
    language: str = "en"
    current_transaction_id: str = field(default_factory=generate_transaction_id)

    @property
    def transaction_id(self) -> str: return self.current_transaction_id
    @property
    def warehouse_id(self) -> int: return self.current_warehouse_id

    @classmethod
    def get_current(cls):
        if "erp_context" not in st.session_state: st.session_state.erp_context = cls()
        return st.session_state.erp_context

    def rotate_transaction(self): self.current_transaction_id = generate_transaction_id()
    def new_transaction(self): self.rotate_transaction()
    def set_user(self, user): self.current_user = user
    def set_warehouse(self, warehouse_id): self.current_warehouse_id = int(warehouse_id)
    def clear_user(self): self.current_user = None

class CacheManager:
    @staticmethod
    def bump_version(key: str = "inventory_version"):
        if "cache_versions" not in st.session_state: st.session_state.cache_versions = {}
        st.session_state.cache_versions[key] = st.session_state.cache_versions.get(key, 0) + 1

    @staticmethod
    def get_version(key: str = "inventory_version"):
        if "cache_versions" not in st.session_state: st.session_state.cache_versions = {}
        return st.session_state.cache_versions.get(key, 0)
