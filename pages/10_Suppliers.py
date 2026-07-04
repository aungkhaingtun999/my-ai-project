st.title("🏭 Suppliers")
data = supabase.table("suppliers").select("*").execute().data or []
st.dataframe(data)