import streamlit as st
from utils import supabase
import pandas as pd
from datetime import datetime

def post_internship(user):
    st.header("Post New Internship")
    
    # Fetch current company details
    try:
        profile_response = supabase.table("profiles_names").select("company_name").eq("id", user.id).single().execute()
        current_company_name = profile_response.data.get("company_name", "") if profile_response.data else ""
    except:
        current_company_name = ""

    with st.form("post_internship_form"):
        company_name = st.text_input("Company Name", value=current_company_name)
        title = st.text_input("Internship Title")
        role = st.text_input("Role (e.g., Frontend Developer)")
        description = st.text_area("Description")
        location = st.text_input("Location (e.g., Remote, New York)")
        duration = st.text_input("Duration (e.g., 3 months)")
        stipend = st.text_input("Stipend (e.g., $1000/month)")
        skills_str = st.text_area("Skills Required (comma separated)")
        
        submitted = st.form_submit_button("Post Internship")
        if submitted:
            if not title or not role or not description or not company_name:
                st.error("Please fill in all required fields (Company Name, Title, Role, Description).")
            else:
                skills = [s.strip() for s in skills_str.split(",") if s.strip()]
                try:
                    # Update company name in profile if changed
                    if company_name != current_company_name:
                        supabase.table("profiles_names").update({"company_name": company_name}).eq("id", user.id).execute()
                    
                    # Insert internship
                    supabase.table("internships").insert({
                        "company_id": user.id,
                        "title": title,
                        "role": role,
                        "description": description,
                        "location": location,
                        "duration": duration,
                        "stipend": stipend,
                        "skills_required": skills,
                        "status": "open"
                    }).execute()
                    st.success("Internship posted successfully!")
                except Exception as e:
                    st.error(f"Error posting internship: {e}")

def manage_applications(user):
    st.header("Manage Applications")
    
    # Fetch applications for this company's internships
    try:
        response = supabase.table("applications").select("*, internships(title), profiles_names(full_name, email, resume_url, portfolio_url)").execute()
        # RLS policies ensure companies only see their own applications
        applications = response.data
    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        applications = []
        
    if not applications:
        st.info("No applications received yet.")
        return

    for app in applications:
        with st.expander(f"{app['profiles_names']['full_name']} for {app['internships']['title']} ({app['status']})"):
            st.write(f"**Email:** {app['profiles_names']['email']}")
            st.write(f"**Resume:** {app['profiles_names']['resume_url']}")
            st.write(f"**Portfolio:** {app['profiles_names']['portfolio_url']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Accept", key=f"accept_{app['id']}"):
                    update_application_status(app['id'], "accepted")
            with col2:
                if st.button("Reject", key=f"reject_{app['id']}"):
                    update_application_status(app['id'], "rejected")

def update_application_status(app_id, status):
    try:
        supabase.table("applications").update({"status": status}).eq("id", app_id).execute()
        st.success(f"Application {status}!")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating status: {e}")

def assign_tasks(user):
    st.header("Assign Tasks")
    
    # Get accepted students
    try:
        response = supabase.table("applications").select("*, internships(title), profiles_names(id, full_name)").eq("status", "accepted").execute()
        accepted_apps = response.data
    except Exception as e:
        st.error(f"Error fetching accepted students: {e}")
        accepted_apps = []
        
    if not accepted_apps:
        st.info("No active interns found.")
        return
        
    student_options = {f"{app['profiles_names']['full_name']} ({app['internships']['title']})": app for app in accepted_apps}
    selected_student_key = st.selectbox("Select Intern", list(student_options.keys()))
    
    if selected_student_key:
        selected_app = student_options[selected_student_key]
        
        with st.form("task_form"):
            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            due_date = st.date_input("Due Date")
            
            submitted = st.form_submit_button("Assign Task")
            if submitted:
                try:
                    supabase.table("tasks").insert({
                        "internship_id": selected_app['internship_id'],
                        "student_id": selected_app['profiles_names']['id'],
                        "title": title,
                        "description": description,
                        "due_date": due_date.isoformat(),
                        "status": "pending"
                    }).execute()
                    st.success("Task assigned successfully!")
                except Exception as e:
                    st.error(f"Error assigning task: {e}")

def company_dashboard(user):
    st.header("Company Dashboard")
    
    # Fetch stats
    try:
        # Internships
        internships = supabase.table("internships").select("id", count="exact").eq("company_id", user.id).execute()
        internship_count = internships.count
        
        # Applications (Pending)
        # We need to filter applications by internships owned by this company. 
        # Since we can't easily do deep joins with count in one go without a view, we'll fetch pending ones.
        # A more efficient way would be RPC or a View, but for now let's fetch and filter (MVP).
        my_internships = supabase.table("internships").select("id").eq("company_id", user.id).execute()
        my_internship_ids = [i['id'] for i in my_internships.data]
        
        if my_internship_ids:
            pending_apps = supabase.table("applications").select("id", count="exact").in_("internship_id", my_internship_ids).eq("status", "pending").execute()
            pending_count = pending_apps.count
            
            active_tasks = supabase.table("tasks").select("id", count="exact").in_("internship_id", my_internship_ids).eq("status", "pending").execute()
            task_count = active_tasks.count
        else:
            pending_count = 0
            task_count = 0

    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        internship_count = 0
        pending_count = 0
        task_count = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Posted Internships", internship_count)
    with col2:
        st.metric("Pending Applications", pending_count)
    with col3:
        st.metric("Active Tasks", task_count)
        
    st.divider()
    st.subheader("Quick Actions")
    st.write("Use the sidebar menu to manage your internships and applications.")

def show_company_view(user):
    selected = st.sidebar.radio("Menu", ["Dashboard", "Post Internship", "Manage Applications", "Assign Tasks"])
    
    if selected == "Dashboard":
        company_dashboard(user)
    elif selected == "Post Internship":
        post_internship(user)
    elif selected == "Manage Applications":
        manage_applications(user)
    elif selected == "Assign Tasks":
        assign_tasks(user)
