st.title("👥 Customers")
data = supabase.table("customers").select("*").execute().data or []
st.dataframe(data)