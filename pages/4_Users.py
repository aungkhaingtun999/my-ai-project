# ==============================================================================
# pages/4_Users.py
# ERP ENTERPRISE USER MANAGEMENT v5.0
# Compatible:
# public.users
# roles
# ==============================================================================

import streamlit as st
from database import get_supabase
import hashlib
from datetime import datetime


supabase = get_supabase()


st.set_page_config(
    page_title="User Management",
    layout="wide"
)


st.title("👥 User Management (Admin Panel)")
st.caption("Control users, roles and access rights")


# ==================================================
# PASSWORD HASH
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()



# ==================================================
# LOAD ROLES
# ==================================================

roles_resp = (
    supabase
    .table("roles")
    .select("*")
    .execute()
)


roles = roles_resp.data or []


if not roles:

    st.error(
        "Roles table is empty. Please create roles first."
    )

    st.stop()



role_map = {

    r["name"]: r["id"]

    for r in roles

}


role_names = list(role_map.keys())



# ==================================================
# LOAD USERS
# ==================================================

users_resp = (
    supabase
    .table("users")
    .select(
        """
        id,
        username,
        full_name,
        role_id,
        is_active
        """
    )
    .execute()
)


users = users_resp.data or []



# ==================================================
# SEARCH
# ==================================================

search = st.text_input(
    "🔍 Search User"
)


if search:

    search = search.lower()


    users = [

        u for u in users

        if

        search in str(
            u.get("username","")
        ).lower()

        or

        search in str(
            u.get("full_name","")
        ).lower()

    ]



# ==================================================
# CREATE USER
# ==================================================

st.subheader(
    "➕ Create New User"
)



with st.form(
    "create_user_form"
):


    username = st.text_input(
        "Username"
    )


    full_name = st.text_input(
        "Full Name"
    )


    password = st.text_input(
        "Password",
        type="password"
    )


    selected_role = st.selectbox(
        "Role",
        role_names
    )


    active = st.checkbox(
        "Active",
        value=True
    )


    submit = st.form_submit_button(
        "Create User"
    )



    if submit:


        if not username or not password:

            st.error(
                "Username and password required"
            )


        else:


            try:


                result = (

                    supabase
                    .table("users")
                    .insert({

                        "username":
                            username,

                        "full_name":
                            full_name,

                        "password_hash":
                            hash_password(password),

                        "role_id":
                            role_map[selected_role],

                        "is_active":
                            active

                    })
                    .execute()

                )


                if result.data:


                    st.success(
                        "User created successfully"
                    )

                    st.rerun()


                else:

                    st.error(
                        "Create user failed"
                    )



            except Exception as e:


                st.error(
                    str(e)
                )




st.divider()



# ==================================================
# USER LIST
# ==================================================

st.subheader(
    "📋 Users"
)



if not users:

    st.info(
        "No users found"
    )

else:


    for u in users:


        role_name = next(

            (
                r["name"]
                for r in roles
                if r["id"] == u["role_id"]
            ),

            "Unknown"

        )



        c1,c2,c3,c4,c5 = st.columns(
            [2,3,2,2,1]
        )


        with c1:

            st.write(
                "👤",
                u.get(
                    "username",
                    "-"
                )
            )



        with c2:

            st.write(
                u.get(
                    "full_name",
                    "-"
                )
            )



        with c3:

            st.write(
                "🛡",
                role_name
            )



        with c4:


            new_role = st.selectbox(

                "Role",

                role_names,

                index=role_names.index(role_name)
                if role_name in role_names
                else 0,

                key=f"role_{u['id']}"

            )



            if new_role != role_name:


                supabase.table(
                    "users"
                ).update({

                    "role_id":
                    role_map[new_role]

                }).eq(
                    "id",
                    u["id"]
                ).execute()


                st.success(
                    "Role updated"
                )

                st.rerun()



        with c5:


            if st.button(
                "🗑",
                key=f"delete_{u['id']}"
            ):


                supabase.table(
                    "users"
                ).delete().eq(
                    "id",
                    u["id"]
                ).execute()


                st.warning(
                    "User deleted"
                )

                st.rerun()



st.divider()



# ==================================================
# DASHBOARD
# ==================================================

st.subheader(
    "📊 System Summary"
)


total = len(users)


active = len(

    [
        u for u in users
        if u.get("is_active")
    ]

)


inactive = total - active



c1,c2,c3 = st.columns(3)


c1.metric(
    "👥 Total Users",
    total
)


c2.metric(
    "✅ Active",
    active
)


c3.metric(
    "⛔ Disabled",
    inactive
)



st.success(
    "✔ Enterprise User Management Active"
)
