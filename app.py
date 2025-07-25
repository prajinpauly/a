import streamlit as st
import requests
import datetime
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Finance Analytics", layout="wide")

# --- Custom CSS for blue/white theme and modern UI ---
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #f4f8fb !important;
        color: #1a237e !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .brand-bar {
        background: linear-gradient(90deg, #1976d2 0%, #64b5f6 100%);
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 16px rgba(25,118,210,0.08);
    }
    .brand-bar h1 {
        color: #fffde7;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 2px 8px #1976d2;
    }
    .dashboard-section {
        background: #e3f2fd;
        border-radius: 0.7rem;
        padding: 2rem;
        margin-bottom: 2rem;
        color: #1a237e;
    }
    .analytics-section {
        background: #fffde7;
        border-radius: 0.7rem;
        padding: 2rem;
        margin-bottom: 2rem;
        color: #1a237e;
    }
    .stButton>button {
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 0.4rem;
        padding: 0.5rem 1.5rem;
        background: #1976d2;
        color: #fff;
        border: none;
    }
    .sidebar-nav {
        border: 2px solid #1976d2;
        border-radius: 0.5rem;
        padding: 1rem;
        background: #e3f2fd;
        margin-bottom: 2rem;
    }
    .username-box {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    .avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #1976d2;
        color: #fffde7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-left: 1rem;
        box-shadow: 0 2px 8px rgba(25,118,210,0.18);
    }
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    input, textarea, select {
        background: #fff !important;
        color: #1a237e !important;
    }
    </style>
""", unsafe_allow_html=True)

def get_categories():
    resp = requests.get(f"{API_URL}/categories/")
    if resp.status_code == 200:
        return resp.json()
    return []

def get_subcategories(main_type):
    cats = get_categories()
    return [cat for cat in cats if cat["type"].lower() == main_type.lower()]

# --- Welcome Page with Brand Heading and Centered Icon ---
if "user_id" not in st.session_state:
    st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    auth_page = st.sidebar.radio("Choose", ["Login", "Sign Up"])
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="brand-bar"><h1>Finance Analytics</h1></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="centered">'
        '<img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="100" style="margin-bottom:1rem;">'
        '</div>', unsafe_allow_html=True
    )
    st.markdown('<div style="font-size:2rem;font-weight:700;color:#1976d2;margin-bottom:1em;text-align:center;">Track, Analyze, and Grow Your Wealth</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;">A modern, secure, and smart dashboard for your personal finance journey.</div>', unsafe_allow_html=True)

    if auth_page == "Sign Up":
        st.subheader("Sign Up")
        signup_name = st.text_input("Name")
        signup_email = st.text_input("Email")
        signup_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            resp = requests.post(f"{API_URL}/signup", json={
                "name": signup_name,
                "email": signup_email,
                "password": signup_password
            })
            if resp.status_code == 200:
                st.success("Sign up successful! Please log in.")
            else:
                try:
                    error_msg = resp.json().get("detail", "Sign up failed.")
                except Exception:
                    error_msg = resp.text
                st.error(f"Sign up failed: {error_msg}")

    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            resp = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                st.session_state.user_id = resp.json()["user_id"]
                st.session_state.username = email.split("@")[0].capitalize()
                st.success("Login successful!")
                st.rerun()
            else:
                try:
                    error_msg = resp.json().get("detail", "Login failed.")
                except Exception:
                    error_msg = resp.text
                st.error(f"Login failed: {error_msg}")

else:
    # --- Username and Avatar at the Top of Sidebar ---
    st.sidebar.markdown(
        f"""
        <div class="username-box">
            <div class="avatar">{st.session_state.get("username", "User")[0]}</div>
            <span style="font-size:1.1rem;font-weight:600;color:#1976d2;margin-left:0.7rem;">{st.session_state.get("username", "User")}</span>
        </div>
        """, unsafe_allow_html=True
    )
    st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    page = st.sidebar.radio("Go to", ["Dashboard", "Analytics", "Logout"])
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    user_id = st.session_state.user_id
    username = st.session_state.get("username", "User")

    if page == "Dashboard":
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align:center;color:#1976d2;font-weight:800;'>💸 Add Transaction</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='color:#1976d2;font-size:1.1rem;font-weight:600;margin-bottom:1em;text-align:center;'>"
            "Every dollar you track is a step closer to your financial goals! 🚀</div>",
            unsafe_allow_html=True
        )

        main_type = st.selectbox("Main Category", ["Income", "Expense"])
        subcategories = get_subcategories(main_type)
        if subcategories:
            subcat_names = [cat["name"] for cat in subcategories]
            subcat_name = st.selectbox("Subcategory", subcat_names, key=main_type)
            category_id = [cat["category_id"] for cat in subcategories if cat["name"] == subcat_name][0]
        else:
            st.warning(f"No subcategories found for {main_type}.")
            category_id = 1

        amount = st.number_input("Amount (AUD $)", min_value=0.0, step=0.01, format="%.2f")
        date = st.date_input("Date", value=datetime.date.today())
        note = st.text_input("Note (optional)")

        if st.button("Add Transaction"):
            data = {
                "user_id": user_id,
                "amount": float(amount),
                "date": str(date),
                "category_id": category_id,
                "note": note
            }
            resp = requests.post(f"{API_URL}/expenses/", json=data)
            if resp.status_code == 200:
                st.success("Transaction added successfully! Keep building your future! 💡")
                st.rerun()
            else:
                try:
                    error_msg = resp.json().get("detail", "Failed to add transaction.")
                except Exception:
                    error_msg = resp.text
                st.error(f"Failed to add transaction: {error_msg}")
        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Analytics":
        st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
        st.title("📊 Monthly Analytics")
        resp = requests.get(f"{API_URL}/expenses/{user_id}")
        if resp.status_code == 200:
            expenses = resp.json()
            if expenses:
                df = pd.DataFrame(expenses)
                df["Date"] = pd.to_datetime(df["date"])
                df["Month_dt"] = df["Date"].dt.to_period("M").dt.to_timestamp()
                df["Month"] = df["Month_dt"].dt.strftime("%b %Y")
                categories = get_categories()
                cat_map = {cat["category_id"]: (cat["type"], cat["name"]) for cat in categories}
                df["Main Category"] = df["category_id"].map(lambda x: cat_map.get(x, ("Other", "Other"))[0])
                df["Subcategory"] = df["category_id"].map(lambda x: cat_map.get(x, ("Other", "Other"))[1])

                st.subheader("Monthly Trend (Line Chart)")
                monthly = df.groupby(["Month_dt", "Month", "Main Category"])["amount"].sum().reset_index()
                monthly = monthly.sort_values("Month_dt")
                fig = px.line(
                    monthly, x="Month", y="amount", color="Main Category",
                    markers=True, line_shape="spline",
                    labels={"amount": "Amount (AUD $)"},
                    title="Monthly Income & Expense",
                    text="amount"
                )
                fig.update_traces(line=dict(width=3), textposition="top right", texttemplate="%{text:.2f}")
                fig.update_layout(
                    plot_bgcolor="#fffde7",
                    paper_bgcolor="#fffde7",
                    font_color="#1976d2",
                    legend_title_font_color="#1976d2"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Subcategory Breakdown (Pie Chart)")
                latest_month = monthly["Month_dt"].max()
                this_month = df[df["Month_dt"] == latest_month]
                if not this_month.empty:
                    pie = this_month.groupby("Subcategory")["amount"].sum().reset_index()
                    fig2 = px.pie(
                        pie, names="Subcategory", values="amount",
                        title="Subcategory Breakdown",
                        color_discrete_sequence=px.colors.sequential.Blues
                    )
                    fig2.update_traces(textinfo='percent+label', pull=[0.05]*len(pie))
                    fig2.update_layout(
                        plot_bgcolor="#fffde7",
                        paper_bgcolor="#fffde7",
                        font_color="#1976d2"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No transactions for this month.")
            else:
                st.info("No transactions found.")
        else:
            st.error(f"Failed to fetch analytics: {resp.text}")
        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Logout":
        del st.session_state.user_id
        st.success("Logged out successfully!")
        st.rerun()