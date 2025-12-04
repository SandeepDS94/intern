# Internship Management System

A Streamlit-based application for managing internships, connecting students and companies.

## Features
- **Student View**: Apply for internships, view status, update profile.
- **Company View**: Post internships, manage applications.
- **Authentication**: Secure login/signup using Supabase.

## Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SandeepDS94/intern.git
    cd intern
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## Deployment

### Recommended: Streamlit Cloud
This is the easiest and most reliable way to deploy Streamlit apps.

1.  Push your code to GitHub.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Connect your GitHub account.
4.  Click "New app".
5.  Select your repository (`SandeepDS94/intern`), branch (`main`), and main file path (`app.py`).
6.  **Secrets**:
    - Go to "Advanced settings" -> "Secrets".
    - Copy the contents of your local `.streamlit/secrets.toml` into the secrets area.
7.  Click "Deploy".

### Vercel (Not Recommended)
Vercel is designed for static and serverless apps. Streamlit requires a persistent server, which Vercel does not natively support. Deploying to Vercel often results in 404 errors or runtime failures because:
- Vercel looks for `index.html` or a serverless function handler, not a Streamlit server.
- Streamlit relies on WebSockets, which have limitations in Vercel's serverless environment.

If you see a **404: NOT_FOUND** error on Vercel, it is because Vercel doesn't know how to start the Streamlit server.
