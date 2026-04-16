import streamlit as st
import pandas as pd
import base64
import os
from datetime import date
import time

st.set_page_config(page_title="Liane's Library", page_icon="📚", layout="wide")

# ---------------- DATA PATH ----------------
DATA_DIR = "data"

# ---------------- SAFE LOAD/SAVE ----------------
def load_data(file):
    path = os.path.join(DATA_DIR, file)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_data(df, file):
    path = os.path.join(DATA_DIR, file)
    df.to_csv(path, index=False)

# ---------------- CLEAN COLUMNS (CRITICAL FIX) ----------------
def clean(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

# ---------------- ACTIVITY LOG ----------------
def log_activity(book_title, borrower_name, action, b_id=None, f_id=None):
    df = load_data("activity_log.csv")
    df = clean(df)

    new_row = pd.DataFrame([{
        "book_title": book_title,
        "borrower_name": borrower_name,
        "action_type": action,
        "book_id": b_id,
        "friend_id": f_id,
        "action_date": pd.Timestamp.now()
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df, "activity_log.csv")

# ---------------- IMAGE ----------------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

img_path = "image_5.png"

if "page" not in st.session_state:
    st.session_state.page = "Welcome"

choice = st.session_state.page

# ---------------- WELCOME STYLE ----------------
if choice == "Welcome":
    img_base64 = get_base64_of_bin_file(img_path)
    bg_style = f'background-image: url("data:image/png;base64,{img_base64}");' if img_base64 else "background-color: #0e1117;"

    st.markdown(f"""
        <style>
        .stApp {{
            {bg_style}
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        header {{visibility: hidden;}}
        [data-testid="stSidebar"] {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
if choice != "Welcome":
    with st.sidebar:
        st.title("📌 Navigation")
        if st.button("📊 Dashboard"): st.session_state.page="Dashboard"; st.rerun()
        if st.button("📚 Books Management"): st.session_state.page="Books Management"; st.rerun()
        if st.button("👥 Friends Management"): st.session_state.page="Friends Management"; st.rerun()
        if st.button("📤 Issue Loan"): st.session_state.page="Issue Loan"; st.rerun()
        if st.button("📥 Return Book"): st.session_state.page="Return Book"; st.rerun()
        if st.button("📜 Activity History"): st.session_state.page="Activity History"; st.rerun()
        if st.button("🏠 Homepage"): st.session_state.page="Welcome"; st.rerun()

# ---------------- WELCOME PAGE ----------------
if choice == "Welcome":
    if st.button("☕️ INTO THE LIBRARY"):
        st.session_state.page = "Dashboard"
        st.rerun()

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    st.title("Dashboard")

    books = clean(load_data("books.csv"))
    loans = clean(load_data("loans.csv"))
    friends = clean(load_data("friends.csv"))

    if "return_date" not in loans.columns:
        loans["return_date"] = pd.NA

    active_loans = loans[loans["return_date"].isna()] if not loans.empty else pd.DataFrame()

    if not books.empty:
        df = books.merge(active_loans, left_on="id", right_on="book_id", how="left")
        df = df.merge(friends, left_on="friend_id", right_on="id", how="left", suffixes=("", "_friend"))

        df["borrower"] = df["name"].fillna("-")

        df = df[["isbn", "title", "author", "borrower", "status"]]

        st.dataframe(df, use_container_width=True)

# ---------------- BOOKS ----------------
elif choice == "Books Management":
    st.title("Books Management")

    books = clean(load_data("books.csv"))

    tab1, tab2 = st.tabs(["View & Edit", "Add Book"])

    with tab2:
        with st.form("add"):
            t = st.text_input("Title")
            a = st.text_input("Author")
            g = st.text_input("Genre")
            i = st.text_input("ISBN")

            if st.form_submit_button("Add"):
                new_id = books["id"].max() + 1 if not books.empty else 1

                new = pd.DataFrame([{
                    "id": new_id,
                    "title": t,
                    "author": a,
                    "genre": g,
                    "isbn": i,
                    "status": "Available"
                }])

                books = pd.concat([books, new], ignore_index=True)
                save_data(books, "books.csv")
                log_activity(t, "System", "BOOK_ADDED")

                st.success("Added")
                st.rerun()

    with tab1:
        st.dataframe(books)

# ---------------- FRIENDS ----------------
elif choice == "Friends Management":
    st.title("Friends Management")

    friends = clean(load_data("friends.csv"))

    with st.form("friend"):
        n = st.text_input("Name")
        p = st.text_input("Phone")
        e = st.text_input("Email")

        if st.form_submit_button("Add"):
            new_id = friends["id"].max() + 1 if not friends.empty else 1

            new = pd.DataFrame([{
                "id": new_id,
                "name": n,
                "phone": p,
                "email": e
            }])

            friends = pd.concat([friends, new], ignore_index=True)
            save_data(friends, "friends.csv")
            log_activity("-", n, "FRIEND_ADDED")

            st.success("Added")
            st.rerun()

    st.dataframe(friends)

# ---------------- ISSUE LOAN ----------------
elif choice == "Issue Loan":
    st.title("Issue Loan")

    books = clean(load_data("books.csv"))
    friends = clean(load_data("friends.csv"))
    loans = clean(load_data("loans.csv"))

    if "return_date" not in loans.columns:
        loans["return_date"] = pd.NA

    available = books[books["status"] == "Available"]

    if not available.empty and not friends.empty:
        b = st.selectbox("Book", available["title"])
        f = st.selectbox("Friend", friends["name"])

        if st.button("Lend"):
            bid = int(available[available["title"] == b]["id"].values[0])
            fid = int(friends[friends["name"] == f]["id"].values[0])

            books.loc[books["id"] == bid, "status"] = "Borrowed"

            new = pd.DataFrame([{
                "id": loans["id"].max() + 1 if not loans.empty else 1,
                "book_id": bid,
                "friend_id": fid,
                "loan_date": date.today(),
                "return_date": pd.NA
            }])

            loans = pd.concat([loans, new], ignore_index=True)

            save_data(books, "books.csv")
            save_data(loans, "loans.csv")

            log_activity(b, f, "LOAN_ISSUED", bid, fid)

            st.success("Done")
            st.rerun()

# ---------------- RETURN ----------------
elif choice == "Return Book":
    st.title("Return Book")

    books = clean(load_data("books.csv"))
    loans = clean(load_data("loans.csv"))

    if "return_date" not in loans.columns:
        loans["return_date"] = pd.NA

    active = loans[loans["return_date"].isna()]

    if not active.empty:
        lid = st.selectbox("Loan ID", active["id"])

        if st.button("Return"):
            bid = int(active[active["id"] == lid]["book_id"].values[0])

            loans.loc[loans["id"] == lid, "return_date"] = date.today()
            books.loc[books["id"] == bid, "status"] = "Available"

            save_data(loans, "loans.csv")
            save_data(books, "books.csv")

            st.success("Returned")
            st.rerun()

# ---------------- HISTORY ----------------
elif choice == "Activity History":
    st.title("Activity History")

    df = clean(load_data("activity_log.csv"))
    st.dataframe(df)