import streamlit as st
import mysql.connector
import pandas as pd
import base64
import os
from datetime import date
import time

st.set_page_config(page_title="Liane's Library", page_icon="📚", layout="wide")

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_path = "/Users/elcintimurcakmak/dumps/image_5.png"

if "page" not in st.session_state:
    st.session_state.page = "Welcome"

choice = st.session_state.page

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
        .block-container {{ padding: 0rem; }}

        div.stButton > button {{
            position: fixed; bottom: 40px; right: 40px; width: auto !important;
            background-color: #d1c09d !important; color: #ffffff !important;
            border: 1px solid #ffffff !important; border-radius: 5px !important;
            padding: 12px 30px !important; font-size: 20px !important;
            font-weight: 600 !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
            z-index: 9999; transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{ transform: scale(1.1); background-color: #e8d0ab !important; }}
        </style>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #faf4e9; }
        [data-testid="stSidebar"] { background-color: #efdcbf; border-right: 1px solid rgba(0,0,0,0.1); }
        header, [data-testid="stHeader"] { background-color: transparent !important; }
        
        [data-testid="stSidebar"] div.stButton > button {
            display: flex !important; 
            justify-content: flex-start !important; 
            text-align: left !important; 
            padding-left: 15px !important;
            border: 2px solid #ffffff !important; 
            background-color: #d1c09d !important; 
            color: #ffffff !important; 
            margin-bottom: 10px; 
            border-radius: 8px !important; 
            width: 100% !important;
            transition: all 0.3s ease;
        }
        
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #d1c09d !important; 
            border-color: #d1c09d !important; 
            transform: translateX(5px);
        }

        .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.2); border-radius: 10px; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: rgba(255,255,255,0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=st.secrets["mysql"]["password"],
            database="lianes_library",
            autocommit=True
        )
        return conn
    except Exception as err:
        st.error(f"❌ DB Connection Error: {err}")
        return None

def log_activity(book_title, borrower_name, action, b_id=None, f_id=None):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO activity_log (book_title, borrower_name, action_type, book_id, friend_id) VALUES (%s,%s,%s,%s,%s)",
                (book_title, borrower_name, action, b_id, f_id)
            )
        conn.close()

if choice != "Welcome":
    with st.sidebar:
        st.title("📌 Navigation")
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"; st.rerun()
        if st.button("📚 Books Management", use_container_width=True):
            st.session_state.page = "Books Management"; st.rerun()
        if st.button("👥 Friends Management", use_container_width=True):
            st.session_state.page = "Friends Management"; st.rerun()
        if st.button("📤 Issue Loan", use_container_width=True):
            st.session_state.page = "Issue Loan"; st.rerun()
        if st.button("📥 Return Book", use_container_width=True):
            st.session_state.page = "Return Book"; st.rerun()
        if st.button("📜 Activity History", use_container_width=True):
            st.session_state.page = "Activity History"; st.rerun()
        st.write("---")
        if st.button("🏠 Homepage", use_container_width=True):
            st.session_state.page = "Welcome"; st.rerun()

# --- PAGES ---

if choice == "Welcome":
    if st.button("☕️ &nbsp; INTO THE LIBRARY"):
        st.session_state.page = "Dashboard"; st.rerun()

elif choice == "Dashboard":
    st.title(f"Liane's Personal Library — {choice}")
    conn = get_db_connection()
    if conn:
        query = """
            SELECT b.isbn AS ISBN, b.title AS TITLE, b.author AS AUTHOR, fr.name AS BORROWER, b.status AS STATUS
            FROM books b
            LEFT JOIN loans l ON b.id = l.book_id AND l.return_date IS NULL
            LEFT JOIN friends fr ON l.friend_id = fr.id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        df["BORROWER"] = df["BORROWER"].fillna("-")
        
        c1, c2, c3 = st.columns(3)
        
        card = """
        <div style="background-color: rgba(255,255,255,0.4); padding: 25px; border-radius: 15px; 
                    text-align: center; border-bottom: 8px solid {color}; box-shadow: 2px 4px 10px rgba(0,0,0,0.05);">
            <div style="font-size: 45px; margin-bottom: 5px;">{icon}</div>
            <div style="color: #444; font-size: 18px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">{label}</div>
            <div style="font-size: 32px; font-weight: 900; color: #333;">{val}</div>
        </div>
        """
        
        c1.markdown(card.format(icon="📚", label="Total Books", val=len(df), color="#6c63ff"), unsafe_allow_html=True)
        c2.markdown(card.format(icon="🤝", label="Borrowed Books", val=len(df[df["STATUS"]=="Borrowed"]), color="#ff4b4b"), unsafe_allow_html=True)
        c3.markdown(card.format(icon="🏠", label="Available Books", val=len(df[df["STATUS"]=="Available"]), color="#28a745"), unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        df["STATUS"] = df["STATUS"].apply(lambda x: "🏠 Available" if x == "Available" else "📤 Borrowed")
        st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == "Books Management":
    st.title(f"Liane's Personal Library — {choice}")
    tab1, tab2 = st.tabs(["📝 View & Edit", "➕ Add Book"])
    with tab2:
        with st.form("add_book_form", clear_on_submit=True):
            t, a, g, i = st.text_input("Title"), st.text_input("Author"), st.text_input("Genre"), st.text_input("ISBN")
            if st.form_submit_button("Add Book"):
                if t:
                    conn = get_db_connection()
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO books (title, author, genre, isbn) VALUES (%s,%s,%s,%s)", (t,a,g,i))
                    conn.close()
                    log_activity(t, "System", "BOOK_ADDED") 
                    st.success("Book added!"); time.sleep(1); st.rerun()
    with tab1:
        conn = get_db_connection()
        if conn:
            df_b = pd.read_sql("SELECT id, isbn, title, author, status FROM books", conn)
            df_b.insert(0, "Select", False)
            edited_df = st.data_editor(df_b, hide_index=True, key="book_editor", use_container_width=True, column_config={"id": None})
            if st.button("🗑️ Delete Selected Book"):
                to_delete = edited_df[edited_df["Select"] == True]
                if not to_delete.empty:
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            for _, row in to_delete.iterrows():
                                cur.execute("DELETE FROM loans WHERE book_id = %s", (int(row['id']),))
                                cur.execute("DELETE FROM books WHERE id = %s", (int(row['id']),))
                                log_activity(row['title'], "System", "BOOK_DELETED")
                    st.success("Deleted!"); time.sleep(1); st.rerun()
            conn.close()

elif choice == "Friends Management":
    st.title(f"Liane's Personal Library — {choice}")
    tab1, tab2 = st.tabs(["📝 View & Edit", "👤 Add Friend"])
    with tab2:
        with st.form("add_friend"):
            n, p, e = st.text_input("Name"), st.text_input("Phone"), st.text_input("Email")
            if st.form_submit_button("Register"):
                if n:
                    conn = get_db_connection()
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO friends (name, phone, email) VALUES (%s,%s,%s)", (n,p,e))
                    conn.close()
                    log_activity("-", n, "FRIEND_ADDED")
                    st.success("Friend added!"); time.sleep(1); st.rerun()
    with tab1:
        conn = get_db_connection()
        if conn:
            df_f = pd.read_sql("SELECT id, name, phone, email FROM friends", conn)
            df_f.insert(0, "Select", False)
            edited_f = st.data_editor(df_f, hide_index=True, key="friend_editor", use_container_width=True, column_config={"id": None})
            if st.button("🗑️ Delete Selected Friends"):
                to_del = edited_f[edited_f["Select"] == True]
                if not to_del.empty:
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            for _, row in to_del.iterrows():
                                cur.execute("DELETE FROM loans WHERE friend_id = %s", (int(row['id']),))
                                cur.execute("DELETE FROM friends WHERE id = %s", (int(row['id']),))
                                log_activity("-", row['name'], "FRIEND_DELETED") 
                    st.success("Friend deleted!"); time.sleep(1); st.rerun()
            conn.close()

elif choice == "Issue Loan":
    st.title(f"Liane's Personal Library — {choice}")
    conn = get_db_connection()
    if conn:
        books = pd.read_sql("SELECT id, title FROM books WHERE status='Available'", conn)
        friends = pd.read_sql("SELECT id, name FROM friends", conn)
        if not books.empty and not friends.empty:
            with st.form("loan_form"):
                b_title = st.selectbox("Book", books["title"])
                f_name = st.selectbox("Friend", friends["name"])
                if st.form_submit_button("Lend Book"):
                    bid = int(books[books["title"] == b_title]["id"].values[0])
                    fid = int(friends[friends["name"] == f_name]["id"].values[0])
                    with conn.cursor() as cur:
                        cur.execute("UPDATE books SET status='Borrowed' WHERE id=%s", (bid,))
                        cur.execute("INSERT INTO loans (book_id, friend_id, loan_date) VALUES (%s,%s,%s)", (bid, fid, date.today()))
                    log_activity(b_title, f_name, "LOAN_ISSUED", bid, fid)
                    st.success("Success!"); time.sleep(1); st.rerun()
        conn.close()

elif choice == "Return Book":
    st.title(f"Liane's Personal Library — {choice}")
    conn = get_db_connection()
    if conn:
        df_l = pd.read_sql("""SELECT l.id, b.title, fr.name as borrower, b.id as bid, fr.id as fid 
                              FROM loans l JOIN books b ON l.book_id = b.id JOIN friends fr ON l.friend_id = fr.id 
                              WHERE l.return_date IS NULL""", conn)
        if not df_l.empty:
            target = st.selectbox("Book to return", df_l["title"])
            if st.button("Mark as Returned"):
                row = df_l[df_l["title"]==target].iloc[0]
                with conn.cursor() as cur:
                    cur.execute("UPDATE loans SET return_date=%s WHERE id=%s", (date.today(), int(row['id'])))
                    cur.execute("UPDATE books SET status='Available' WHERE id=%s", (int(row['bid']),))
                log_activity(target, row['borrower'], "BOOK_RETURNED", int(row['bid']), int(row['fid']))
                st.success("Returned!"); time.sleep(1); st.rerun()
        conn.close()

elif choice == "Activity History":
    st.title(f"Liane's Personal Library — {choice}")
    conn = get_db_connection()
    if conn:
        df_h = pd.read_sql("SELECT action_type, book_title, borrower_name, action_date FROM activity_log ORDER BY action_date DESC", conn)
        action_map = {
            "BOOK_ADDED": "📥 Book Added", 
            "BOOK_DELETED": "🗑️ Book Deleted", 
            "FRIEND_ADDED": "👤 Friend Added", 
            "FRIEND_DELETED": "🗑️ Friend Deleted",
            "LOAN_ISSUED": "📤 Book Borrowed", 
            "BOOK_RETURNED": "📥 Book Returned"
        }
        df_h["action_type"] = df_h["action_type"].map(action_map).fillna(df_h["action_type"])
        st.dataframe(df_h, use_container_width=True, hide_index=True)
        conn.close()