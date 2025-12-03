import streamlit as st
from utils import supabase, get_user_role
import time

from student_view import show_student_view
from company_view import show_company_view

st.set_page_config(page_title="Internship Management System", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Global Theme */
    .stApp {
        background-color: #0F172A; /* Slate 900 */
        color: #F8FAFC; /* Slate 50 */
        font-family: 'Inter', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #38BDF8 !important; /* Sky 400 */
        font-weight: 700 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); /* Sky 500 to 600 */
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.3);
        background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1E293B; /* Slate 800 */
        color: #F8FAFC;
        border: 1px solid #334155; /* Slate 700 */
        border-radius: 8px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #38BDF8;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
    }
    
    /* Cards/Containers (Simulated with Expanders for now, or just general spacing) */
    .streamlit-expanderHeader {
        background-color: #1E293B;
        border-radius: 8px;
        color: #F8FAFC !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #020617; /* Slate 950 */
        border-right: 1px solid #1E293B;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38BDF8 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    st.title("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_btn"):
        try:
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"] = auth_response.user
            st.session_state["role"] = get_user_role(auth_response.user.id)
            st.success("Logged in successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")

def signup_page():
    st.title("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    full_name = st.text_input("Full Name", key="signup_name")
    role = st.selectbox("I am a...", ["student", "company"], key="signup_role")
    
    if st.button("Sign Up", key="signup_btn"):
        try:
            # Sign up with metadata
            auth_response = supabase.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": role
                    }
                }
            })
            st.success("Signup successful! Please check your email to confirm.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

def main():
    if "user" not in st.session_state:
        st.session_state["user"] = None
        st.session_state["role"] = None

    if st.session_state["user"]:
        st.sidebar.title(f"Welcome, {st.session_state['user'].email}")
        if st.sidebar.button("Logout"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.rerun()
        
        if st.session_state["role"] == "student":
            show_student_view(st.session_state["user"])
        elif st.session_state["role"] == "company":
            show_company_view(st.session_state["user"])
        else:
            st.error("Role not assigned. Please contact support.")
    else:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login_page()
        with tab2:
            signup_page()

if __name__ == "__main__":
    main()
