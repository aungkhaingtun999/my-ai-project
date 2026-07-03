from database import supabase

def add_product(data):
    return supabase.table("products").insert(data).execute()

def get_products():
    return supabase.table("products").select("*").execute()