import streamlit as st
import pandas as pd
import base64
import os
from datetime import date
import time

st.set_page_config(page_title="Liane's Library", page_icon="📚", layout="wide")

# --- DATA LOADING FUNCTIONS ---
def load_data(file_name):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        if file_name == "books.csv":
            return pd.DataFrame(columns=["id", "title", "author", "genre", "isbn", "status", "rating"])
        elif file_name == "friends.csv":
            return pd.DataFrame(columns=["id", "name", "phone", "email"])
        elif file_name == "loans.csv":
            return pd.DataFrame(columns=["id", "book_id", "friend_id", "loan_date", "return_date"])
        elif file_name == "activity_log.csv":
            return pd.DataFrame(columns=["action_type", "book_title", "borrower_name", "action_date"])
    return pd.DataFrame()

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# --- IMAGE LOADING ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_path = "image_5.png"

# --- SESSION STATE & STYLE ---
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

choice = st.session_state.page

if choice == "Welcome":
    img_base64 = get_base64_of_bin_file(img_path)
    bg_style = f'background-image: url("data:image/png;base64,{img_base64}");' if img_base64 else "background-color: #0e1117;"
    st.markdown(f"<style>.stApp {{{bg_style} background-size: cover;}} header {{visibility: hidden;}}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp { background-color: #faf4e9; }</style>", unsafe_allow_html=True)

# --- ACTIVITY LOGGING (CSV VERSION) ---
def log_activity(book_title, borrower_name, action):
    df_h = load_data("activity_log.csv")
    new_log = pd.DataFrame([{
        "action_type": action,
        "book_title": book_title,
        "borrower_name": borrower_name,
        "action_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    df_h = pd.concat([df_h, new_log], ignore_index=True)
    save_data(df_h, "activity_log.csv")

# --- SIDEBAR ---
if choice != "Welcome":
    with st.sidebar:
        st.title("📌 Navigation")
        if st.button("📊 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"; st.rerun()
        if st.button("📚 Books Management", use_container_width=True): st.session_state.page = "Books Management"; st.rerun()
        if st.button("👥 Friends Management", use_container_width=True): st.session_state.page = "Friends Management"; st.rerun()
        if st.button("📤 Issue Loan", use_container_width=True): st.session_state.page = "Issue Loan"; st.rerun()
        if st.button("📥 Return Book", use_container_width=True): st.session_state.page = "Return Book"; st.rerun()
        if st.button("📜 Activity History", use_container_width=True): st.session_state.page = "Activity History"; st.rerun()
        st.write("---")
        if st.button("🏠 Homepage", use_container_width=True): st.session_state.page = "Welcome"; st.rerun()

# --- PAGES ---
if choice == "Welcome":
    if st.button("☕️ &nbsp; INTO THE LIBRARY"):
        st.session_state.page = "Dashboard"; st.rerun()

elif choice == "Dashboard":
    st.title(f"Liane's Personal Library — {choice}")
    df_b = load_data("books.csv")
    df_l = load_data("loans.csv")
    df_f = load_data("friends.csv")

    current_loans = df_l[df_l["return_date"].isna()]
    df_display = df_b.merge(current_loans[['book_id', 'friend_id']], left_on='id', right_on='book_id', how='left')
    df_display = df_display.merge(df_f[['id', 'name']], left_on='friend_id', right_on='id', how='left', suffixes=('', '_friend'))
    
    df_display = df_display[['isbn', 'title', 'author', 'name', 'status']]
    df_display.columns = ["ISBN", "TITLE", "AUTHOR", "BORROWER", "STATUS"]
    df_display["BORROWER"] = df_display["BORROWER"].fillna("-")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Books", len(df_b))
    c2.metric("Borrowed", len(df_b[df_b["status"] == "Borrowed"]))
    c3.metric("Available", len(df_b[df_b["status"] == "Available"]))
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

elif choice == "Books Management":
    st.title("📚 Books Management")
    tab1, tab2 = st.tabs(["📝 View & Edit", "➕ Add Book"])
    df_b = load_data("books.csv")

    with tab2:
        with st.form("add_book_form"):
            t = st.text_input("Title")
            a = st.text_input("Author")
            g = st.text_input("Genre")
            i = st.text_input("ISBN")
            if st.form_submit_button("Add Book"):
                new_id = int(df_b["id"].max() + 1) if not df_b.empty else 1
                new_book = pd.DataFrame([{"id": new_id, "title": t, "author": a, "genre": g, "isbn": i, "status": "Available", "rating": 0.0}])
                df_b = pd.concat([df_b, new_book], ignore_index=True)
                save_data(df_b, "books.csv")
                log_activity(t, "System", "BOOK_ADDED")
                st.success("Book added!"); st.rerun()

    with tab1:
        st.dataframe(df_b, use_container_width=True)

elif choice == "Friends Management":
    st.title("👥 Friends Management")
    df_f = load_data("friends.csv")
    st.dataframe(df_f, use_container_width=True)

elif choice == "Issue Loan":
    st.title("📤 Issue Loan")
    df_b = load_data("books.csv")
    df_f = load_data("friends.csv")
    df_l = load_data("loans.csv")

    available_books = df_b[df_b["status"] == "Available"]
    if not available_books.empty:
        with st.form("loan"):
            book_title = st.selectbox("Select Book", available_books["title"])
            friend_name = st.selectbox("Select Friend", df_f["name"])
            if st.form_submit_button("Lend"):
                # Kitap durumunu güncelle
                df_b.loc[df_b["title"] == book_title, "status"] = "Borrowed"
                # Loan kaydı ekle
                bid = df_b[df_b["title"] == book_title]["id"].values[0]
                fid = df_f[df_f["name"] == friend_name]["id"].values[0]
                new_loan = pd.DataFrame([{"id": len(df_l)+1, "book_id": bid, "friend_id": fid, "loan_date": date.today(), "return_date": None}])
                df_l = pd.concat([df_l, new_loan], ignore_index=True)
                
                save_data(df_b, "books.csv")
                save_data(df_l, "loans.csv")
                log_activity(book_title, friend_name, "LOAN_ISSUED")
                st.success("Success!"); st.rerun()

elif choice == "Activity History":
    st.title("📜 Activity History")
    df_h = load_data("activity_log.csv")
    st.dataframe(df_h.sort_values("action_date", ascending=False), use_container_width=True, hide_index=True)