# ==============================================================================
# erp_core/services/audit_service.py
# ERP ENTERPRISE AUDIT SERVICE
# ==============================================================================


from typing import (
    Optional,
    Any
)


from ..config import (
    Tables
)


from ..base_repo import (
    validate_uuid
)





class AuditService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client





    def create_audit_log(
        self,
        action: str,
        details: str,
        user_id: Optional[str] = None

    ) -> bool:


        try:


            result = (

                self.client
                .table(
                    Tables.AUDIT_LOGS
                )
                .insert(

                    {

                        "action":

                            str(
                                action
                            ),



                        "details":

                            str(
                                details
                            ),



                        "user_id":

                            validate_uuid(
                                user_id
                            )

                    }

                )
                .execute()

            )



            return bool(
                result.data
            )



        except Exception:

            return False
