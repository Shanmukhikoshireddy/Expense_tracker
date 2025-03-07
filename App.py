import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Set Streamlit theme
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
if 'salary' not in st.session_state:
    st.session_state.salary = 0
if 'savings' not in st.session_state:
    st.session_state.savings = 0
if 'budget_set' not in st.session_state:
    st.session_state.budget_set = False
if 'view' not in st.session_state:
    st.session_state.view = "add_expense"

# Title with styling
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>💰 Expense Tracker</h1>
    <hr style='border: 2px solid #4CAF50;'>
    """, unsafe_allow_html=True)

# Page navigation
if not st.session_state.budget_set:
    st.subheader("📅 Monthly Budget Setup")
    salary = st.number_input("💵 Enter your monthly salary:", min_value=0.0, format="%.2f")
    savings = st.number_input("🏦 Enter your savings goal for this month:", min_value=0.0, max_value=salary, format="%.2f")
    if st.button("Set Budget", help="Click to set your monthly budget"):
        st.session_state.salary = salary
        st.session_state.savings = savings
        st.session_state.budget_set = True
        st.success("✅ Budget set successfully!")
        st.rerun()
else:
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Expense"):
            st.session_state.view = "add_expense"
            st.rerun()
    with col2:
        if st.button("📜 Expense History"):
            st.session_state.view = "expense_history"
            st.rerun()
    with col3:
        if st.button("📊 Expense Summary"):
            st.session_state.view = "view_summary"
            st.rerun()

    # Calculate Remaining Budget
    def calculate_budget():
        spent = st.session_state.expenses["Amount"].sum() if not st.session_state.expenses.empty else 0
        remaining_budget = st.session_state.salary - st.session_state.savings - spent
        remaining_days = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.date.today()
        daily_budget = remaining_budget / remaining_days.days if remaining_days.days > 0 else 0
        return remaining_budget, daily_budget, spent

    remaining_budget, daily_budget, spent = calculate_budget()

    suggested_spending_limit = st.empty()
    suggested_spending_limit.info(f"💡 To stay within your budget, you should spend no more than **${daily_budget:.2f}** per day for the rest of the month.")

    # Expense Input Form
    if st.session_state.view == "add_expense":
        st.subheader("📝 Add a New Expense")
        with st.form("expense_form"):
            date = st.date_input("📅 Date")
            category = st.selectbox("📂 Category", ["Food", "Transport", "Entertainment", "Bills", "Others"])
            amount = st.number_input("💲 Amount", min_value=0.0, format="%.2f")
            description = st.text_input("📝 Description")
            submitted = st.form_submit_button("➕ Add Expense")
            
            if submitted:
                new_expense = pd.DataFrame([[date, category, amount, description]], columns=["Date", "Category", "Amount", "Description"])
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
                remaining_budget, daily_budget, spent = calculate_budget()
                st.success("✅ Expense added successfully! Budget updated.")
                
                # Update Suggested Spending Limit
                suggested_spending_limit.info(f"💡 To stay within your budget, you should spend no more than **${daily_budget:.2f}** per day for the rest of the month.")

    # Expense History
    elif st.session_state.view == "expense_history":
        st.subheader("📜 Expense History")
        st.dataframe(st.session_state.expenses.style.set_properties(**{'background-color': '#f9f9f9', 'border-color': 'black'}))

    # Expense Summary
    elif st.session_state.view == "view_summary":
        st.subheader("📊 Expense Summary")
        if not st.session_state.expenses.empty:
            summary = st.session_state.expenses.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(summary, names='Category', values='Amount', title='💡 Spending Distribution', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig)

        # Salary Spending Pie Chart
        st.subheader("💰 Salary Spending Overview")
        salary_data = pd.DataFrame({
            "Category": ["Spent", "Remaining"],
            "Amount": [spent, remaining_budget]
        })
        fig_salary = px.pie(salary_data, names='Category', values='Amount', title='💸 Salary Usage Breakdown', color_discrete_sequence=[ "#4CAF50","#D32F2F"])
        st.plotly_chart(fig_salary)
