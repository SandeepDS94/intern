import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

def get_user_role(user_id):
    """Fetch user role from profiles table."""
    try:
        response = supabase.table("profiles_names").select("role").eq("id", user_id).single().execute()
        if response.data:
            return response.data["role"]
    except Exception as e:
        st.error(f"Error fetching role: {e}")
    return None
