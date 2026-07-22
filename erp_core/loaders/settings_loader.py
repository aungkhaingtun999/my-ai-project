from ..base_repo import db
from ..config import Tables


@

def get_setting(
    key: str,
    default=None
):

    """
    ERP Settings Reader
    """

    try:

        result = (
            db()
            .table(
                Tables.SETTINGS
            )
            .select("*")
            .eq(
                "key",
                key
            )
            .maybe_single()
            .execute()
        )


        if result.data:

            return result.data.get(
                "value",
                default
            )


    except Exception:

        pass


    return default
