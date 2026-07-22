# ==============================================================================
# erp_core/rpc_engine.py
# ERP ENTERPRISE RPC GATEWAY ENGINE v30
# ==============================================================================


import json
import time

from typing import (
    Dict,
    Any
)


from postgrest.exceptions import APIError


from .config import log_error




# ==============================================================================
# RPC ENGINE
# ==============================================================================


class RPCEngine:


    SUCCESS_VALUES = [

        True,
        "true",
        "success",
        "completed",
        "ok",
        "done"

    ]


    MAX_RETRY = 3




    # ------------------------------------------------------------------
    # NORMALIZE RESPONSE
    # ------------------------------------------------------------------


    @staticmethod
    def normalize_response(
        raw
    ) -> Dict[str,Any]:


        """
        Convert all Supabase RPC responses
        into standard ERP format.

        Output:

        {
            success: bool,
            message: str,
            data: any
        }

        """



        if raw is None:


            return {

                "success":False,

                "message":
                    "Empty RPC response",

                "data":None

            }




        # --------------------------------------------------------------
        # JSON STRING RESPONSE
        # --------------------------------------------------------------


        if isinstance(
            raw,
            str
        ):


            try:

                raw=json.loads(
                    raw
                )


            except Exception:


                return {

                    "success":False,

                    "message":
                        raw,

                    "data":None

                }





        # --------------------------------------------------------------
        # Supabase sometimes returns list
        # --------------------------------------------------------------


        if isinstance(
            raw,
            list
        ):


            raw = (

                raw[0]
                if raw
                else {}

            )





        # --------------------------------------------------------------
        # response_json wrapper
        # --------------------------------------------------------------


        if (

            isinstance(
                raw,
                dict
            )

            and

            "response_json"
            in raw

        ):


            raw = raw[
                "response_json"
            ]






        # --------------------------------------------------------------
        # Dictionary response
        # --------------------------------------------------------------


        if isinstance(
            raw,
            dict
        ):


            status = (

                raw.get(
                    "success"
                )

                if

                raw.get(
                    "success"
                )
                is not None

                else

                raw.get(
                    "status"
                )

            )



            success = (

                str(
                    status
                )
                .lower()

                in

                [

                    str(x).lower()

                    for x
                    in

                    RPCEngine.SUCCESS_VALUES

                ]

            )



            return {


                "success":
                    success,


                "message":
                    raw.get(
                        "message",
                        "Operation completed"
                    ),


                "data":
                    raw.get(
                        "data",
                        raw
                    )


            }





        # --------------------------------------------------------------
        # Other datatype
        # --------------------------------------------------------------


        return {


            "success":
                True,


            "message":
                "Operation completed",


            "data":
                raw


        }





    # ------------------------------------------------------------------
    # EXECUTE RPC
    # ------------------------------------------------------------------


    @staticmethod
    def execute(
        client,
        rpc_name:str,
        payload:Dict[str,Any]
    ) -> Dict[str,Any]:



        last_error = None




        for attempt in range(
            RPCEngine.MAX_RETRY
        ):



            try:


                response = (

                    client
                    .rpc(
                        rpc_name,
                        payload
                    )
                    .execute()

                )



                return RPCEngine.normalize_response(

                    response.data

                )





            except (

                APIError,

                ConnectionError,

                TimeoutError

            ) as e:



                last_error=e




                if attempt < (

                    RPCEngine.MAX_RETRY - 1

                ):



                    time.sleep(

                        0.5 *
                        (
                            attempt + 1
                        )

                    )


                    continue



                break





            except Exception as e:



                last_error=e

                break





        # --------------------------------------------------------------
        # LOG FAILURE
        # --------------------------------------------------------------


        log_error(

            message=
                "RPC Execution Failed",

            rpc_name=
                rpc_name,

            payload=
                payload,

            exception=
                last_error

        )



        return {


            "success":
                False,


            "message":

                str(
                    last_error
                )

                if last_error

                else

                "RPC Failed",


            "data":
                None

                }
