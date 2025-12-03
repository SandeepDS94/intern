import streamlit as st
from utils import supabase
import pandas as pd
from datetime import datetime

def student_profile(user):
    # Fetch existing profile
    try:
        response = supabase.table("profiles_names").select("*").eq("id", user.id).single().execute()
        profile = response.data if response.data else {}
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        profile = {}

    st.markdown("## My Profile")

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        # Left Column: Profile Card
        st.markdown("""
        <div style="text-align: center;">
        """, unsafe_allow_html=True)
        
        # Dynamic Avatar
        avatar_url = f"https://api.dicebear.com/9.x/avataaars/svg?seed={user.email}"
        st.image(avatar_url, width=150)
        
        st.markdown(f"### {profile.get('full_name', 'Student')}")
        st.markdown(f"**{profile.get('role', 'Student').capitalize()}**")
        
        location = profile.get('location')
        if location:
            st.markdown(f"📍 {location}")
        
        st.divider()
        
        # Contact Info in Card
        if profile.get('email'):
            st.markdown(f"📧 {profile.get('email')}")
        if profile.get('phone'):
            st.markdown(f"📱 {profile.get('phone')}")
            
        st.divider()
        
        # Social Links
        if profile.get('resume_url'):
            st.link_button("📄 Resume", profile['resume_url'], use_container_width=True)
        if profile.get('portfolio_url'):
            st.link_button("🌐 Portfolio", profile['portfolio_url'], use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Right Column: Edit Form
        with st.container(border=True):
            st.subheader("Edit Details")
            with st.form("profile_form"):
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
                with row1_col2:
                    email = st.text_input("Email", value=profile.get("email", user.email))
                
                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
                    phone = st.text_input("Phone", value=profile.get("phone", ""))
                with row2_col2:
                    location = st.text_input("Address / Location", value=profile.get("location", ""))

                row3_col1, row3_col2 = st.columns(2)
                with row3_col1:
                    resume_url = st.text_input("Resume URL", value=profile.get("resume_url", ""))
                with row3_col2:
                    portfolio_url = st.text_input("Portfolio URL", value=profile.get("portfolio_url", ""))
                
                skills_str = st.text_area("Skills (comma separated)", value=", ".join(profile.get("skills", []) or []))
                
                submitted = st.form_submit_button("Save Changes", type="primary")
                if submitted:
                    skills = [s.strip() for s in skills_str.split(",") if s.strip()]
                    updates = {
                        "full_name": full_name,
                        "email": email,
                        "phone": phone,
                        "location": location,
                        "resume_url": resume_url,
                        "portfolio_url": portfolio_url,
                        "skills": skills
                    }
                    try:
                        supabase.table("profiles_names").update(updates).eq("id", user.id).execute()
                        st.success("Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating profile: {e}")

        # Skills Visualization (Mockup based on reference)
        st.subheader("Skills Proficiency")
        skills = profile.get("skills", [])
        if skills:
            for skill in skills:
                st.write(skill)
                st.progress(75) # Mock progress for now
        else:
            st.info("Add skills to see them here.")

def browse_internships(user):
    st.header("Browse Internships")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search by Title or Role")
    with col2:
        location_filter = st.text_input("Filter by Location")

    # Fetch Internships
    query = supabase.table("internships").select("*, profiles_names(company_name)").eq("status", "open")
    
    if search_term:
        query = query.ilike("title", f"%{search_term}%")
    if location_filter:
        query = query.ilike("location", f"%{location_filter}%")
        
    try:
        response = query.execute()
        internships = response.data
    except Exception as e:
        st.error(f"Error fetching internships: {e}")
        internships = []

    if not internships:
        st.info("No internships found.")
        return

    for internship in internships:
        with st.expander(f"{internship['title']} at {internship['profiles_names']['company_name']}"):
            st.write(f"**Role:** {internship['role']}")
            st.write(f"**Location:** {internship['location']}")
            st.write(f"**Stipend:** {internship['stipend']}")
            st.write(f"**Duration:** {internship['duration']}")
            st.write(f"**Description:** {internship['description']}")
            st.write(f"**Skills Required:** {', '.join(internship['skills_required'] or [])}")
            
            # Check if already applied
            try:
                app_check = supabase.table("applications").select("id").eq("internship_id", internship['id']).eq("student_id", user.id).execute()
                already_applied = len(app_check.data) > 0
            except:
                already_applied = False
            
            if already_applied:
                st.button("Applied", disabled=True, key=f"btn_{internship['id']}")
            else:
                if st.button("Apply Now", key=f"apply_{internship['id']}"):
                    apply_for_internship(user, internship['id'])

def apply_for_internship(user, internship_id):
    # Simple application for now, can be expanded to a modal or form
    try:
        supabase.table("applications").insert({
            "internship_id": internship_id,
            "student_id": user.id,
            "status": "pending"
        }).execute()
        st.success("Application submitted successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error submitting application: {e}")

def student_dashboard(user):
    st.header("My Dashboard")
    
    tab1, tab2 = st.tabs(["My Applications", "My Tasks"])
    
    with tab1:
        try:
            response = supabase.table("applications").select("*, internships(title, profiles_names(company_name))").eq("student_id", user.id).execute()
            applications = response.data
        except Exception as e:
            st.error(f"Error fetching applications: {e}")
            applications = []
            
        if applications:
            df = pd.DataFrame(applications)
            # Flatten data for display
            df['Internship'] = df['internships'].apply(lambda x: x['title'])
            df['Company'] = df['internships'].apply(lambda x: x['profiles_names']['company_name'])
            df['Applied At'] = pd.to_datetime(df['applied_at']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(df[['Internship', 'Company', 'status', 'Applied At']], use_container_width=True)
        else:
            st.info("You haven't applied to any internships yet.")

    with tab2:
        try:
            response = supabase.table("tasks").select("*, internships(title)").eq("student_id", user.id).execute()
            tasks = response.data
        except Exception as e:
            st.error(f"Error fetching tasks: {e}")
            tasks = []
            
        if tasks:
            for task in tasks:
                with st.expander(f"{task['title']} ({task['status']})"):
                    st.write(f"**Internship:** {task['internships']['title']}")
                    st.write(f"**Due Date:** {task['due_date']}")
                    st.write(f"**Description:** {task['description']}")
                    if task['feedback']:
                        st.info(f"**Feedback:** {task['feedback']}")
                    
                    if task['status'] != 'completed':
                        submission_link = st.text_input("Submission Link", key=f"sub_{task['id']}", value=task.get('submission_link', ''))
                        if st.button("Submit Task", key=f"btn_sub_{task['id']}"):
                            try:
                                supabase.table("tasks").update({
                                    "submission_link": submission_link,
                                    "status": "submitted"
                                }).eq("id", task['id']).execute()
                                st.success("Task submitted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error submitting task: {e}")
        else:
            st.info("No tasks assigned yet.")

def show_student_view(user):
    selected = st.sidebar.radio("Menu", ["Dashboard", "Browse Internships", "Profile"])
    
    if selected == "Dashboard":
        student_dashboard(user)
    elif selected == "Browse Internships":
        browse_internships(user)
    elif selected == "Profile":
        student_profile(user)
