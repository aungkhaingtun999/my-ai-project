# ==============================================================================
# erp_core/services/accounting_service.py
# ERP ENTERPRISE ACCOUNTING SERVICE
# ==============================================================================


from typing import (
    List,
    Dict,
    Any
)


from ..base_repo import (
    money,
    serialize_json
)


from ..rpc_engine import (
    RPCEngine
)


from ..exceptions import (
    AccountingError
)





class AccountingLedgerService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client





    def post_journal_entry(
        self,
        tx_id: str,
        description: str,
        entries: List[Dict[str, Any]]

    ) -> Dict[str, Any]:


        debit = sum(

            money(
                item.get(
                    "debit",
                    0
                )
            )

            for item in entries

        )


        credit = sum(

            money(
                item.get(
                    "credit",
                    0
                )
            )

            for item in entries

        )



        if debit != credit:

            raise AccountingError(
                f"Debit {debit} != Credit {credit}"
            )



        return RPCEngine.execute(

            self.client,

            "post_journal_entry_rpc",

            {

                "p_transaction_id":
                    tx_id,


                "p_description":
                    description,


                "p_entries":
                    serialize_json(
                        entries
                    )

            }

        )
