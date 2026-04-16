import streamlit as st
import pandas as pd
import base64
import os
from datetime import date
import time


def load_data(file_name):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return pd.DataFrame()

def initialize_files():
    if not os.path.exists("books.csv"):
        df = pd.DataFrame(columns=["id", "title", "author", "genre", "isbn", "status", "rating"])
        save_data(df, "books.csv")
    
    if not os.path.exists("friends.csv"):
        df = pd.DataFrame(columns=["id", "name", "phone", "email"])
        save_data(df, "friends.csv")
    
    if not os.path.exists("loans.csv"):
        df = pd.DataFrame(columns=["id", "book_id", "friend_id", "loan_date", "return_date"])
        save_data(df, "loans.csv")
    
    if not os.path.exists("activity_log.csv"):
        df = pd.DataFrame(columns=["action_type", "book_title", "borrower_name", "action_date"])
        save_data(df, "activity_log.csv")

initialize_files()

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

st.set_page_config(page_title="Liane's Library", page_icon="📚", layout="wide")

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_path = "image_5.png"

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

def log_activity(book_title, borrower_name, action):
    df_h = load_data("activity_log.csv")
    new_log = {
        "action_type": action,
        "book_title": book_title,
        "borrower_name": borrower_name,
        "action_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df_h = pd.concat([df_h, pd.DataFrame([new_log])], ignore_index=True)
    save_data(df_h, "activity_log.csv")
    
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
    
    df_b = load_data("books.csv")
    df_f = load_data("friends.csv")
    df_l = load_data("loans.csv")

    if not df_b.empty:
        active_loans = df_l[df_l["return_date"].isna() | (df_l["return_date"] == "")]

        df = df_b.merge(active_loans[['book_id', 'friend_id']], left_on='id', right_on='book_id', how='left')
        df = df.merge(df_f[['id', 'name']], left_on='friend_id', right_on='id', how='left', suffixes=('', '_friend'))

        df = df[['isbn', 'title', 'author', 'name', 'status']]
        df.columns = ["ISBN", "TITLE", "AUTHOR", "BORROWER", "STATUS"]
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
    else:
        st.info("Your library is currently empty. Go to Books Management to add some books!")

elif choice == "Books Management":
    st.title(f"Liane's Personal Library — {choice}")
    tab1, tab2 = st.tabs(["📝 View & Edit", "➕ Add Book"])
    
    with tab2:
        with st.form("add_book_form", clear_on_submit=True):
            t, a, g, i = st.text_input("Title"), st.text_input("Author"), st.text_input("Genre"), st.text_input("ISBN")
            if st.form_submit_button("Add Book"):
                if t:
                    df_b = load_data("books.csv")
                    new_id = int(df_b["id"].max() + 1) if not df_b.empty else 1
                    new_book = pd.DataFrame([{
                        "id": new_id, 
                        "title": t, 
                        "author": a, 
                        "genre": g, 
                        "isbn": i, 
                        "status": "Available", 
                        "rating": 0.0
                    }])
                    df_b = pd.concat([df_b, new_book], ignore_index=True)
                    save_data(df_b, "books.csv")
                    log_activity(t, "System", "BOOK_ADDED") 
                    st.success(f"'{t}' added to library!"); time.sleep(1); st.rerun()

    with tab1:
        df_b = load_data("books.csv")
        if not df_b.empty:
            df_b.insert(0, "Select", False)
            edited_df = st.data_editor(df_b, hide_index=True, key="book_editor", use_container_width=True, column_config={"id": None})
            
            if st.button("🗑️ Delete Selected Book"):
                to_delete = edited_df[edited_df["Select"] == True]
                if not to_delete.empty:
                    df_b_new = edited_df[edited_df["Select"] == False].drop(columns=["Select"])
                    save_data(df_b_new, "books.csv")
                    for _, row in to_delete.iterrows():
                        log_activity(row['title'], "System", "BOOK_DELETED")
                    st.success("Deleted successfully!"); time.sleep(1); st.rerun()
        else:
            st.info("No books found.")

elif choice == "Friends Management":
    st.title(f"Liane's Personal Library — {choice}")
    tab1, tab2 = st.tabs(["📝 View & Edit", "👤 Add Friend"])
    with tab2:
        with st.form("add_friend"):
            n, p, e = st.text_input("Name"), st.text_input("Phone"), st.text_input("Email")
            if st.form_submit_button("Register"):
                if n:
                    df_f = load_data("friends.csv")
                    new_id = int(df_f["id"].max() + 1) if not df_f.empty else 1
                    new_friend = pd.DataFrame([{
                        "id": new_id, 
                        "name": n, 
                        "phone": p, 
                        "email": e
                    }])
                    df_f = pd.concat([df_f, new_friend], ignore_index=True)
                    save_data(df_f, "friends.csv")
                    log_activity("-", n, "FRIEND_ADDED")
                    st.success(f"Friend '{n}' added!"); time.sleep(1); st.rerun()
    with tab1:
        df_f = load_data("friends.csv")
        if not df_f.empty:
            df_f.insert(0, "Select", False)
            edited_f = st.data_editor(df_f, hide_index=True, key="friend_editor", use_container_width=True, column_config={"id": None})
            if st.button("🗑️ Delete Selected Friends"):
                to_del = edited_f[edited_f["Select"] == True]
                if not to_del.empty:
                    df_f_new = edited_f[edited_f["Select"] == False].drop(columns=["Select"])
                    save_data(df_f_new, "friends.csv")
                    for _, row in to_del.iterrows():
                        log_activity("-", row['name'], "FRIEND_DELETED")
                    st.success("Friend deleted!"); time.sleep(1); st.rerun()
        else:
            st.info("No friends registered yet.")

elif choice == "Issue Loan":
    st.title(f"Liane's Personal Library — {choice}")
    df_b = load_data("books.csv")
    df_f = load_data("friends.csv")
    df_l = load_data("loans.csv")

    if not df_b.empty and not df_f.empty:
        available_books = df_b[df_b["status"] == "Available"]
        if not available_books.empty:
            with st.form("loan_form"):
                b_title = st.selectbox("Book", available_books["title"])
                f_name = st.selectbox("Friend", df_f["name"])
                if st.form_submit_button("Lend Book"):
                    bid = df_b[df_b["title"] == b_title]["id"].values[0]
                    fid = df_f[df_f["name"] == f_name]["id"].values[0]
                    df_b.loc[df_b["id"] == bid, "status"] = "Borrowed"
                    save_data(df_b, "books.csv")
                    new_loan = pd.DataFrame([{
                        "id": int(df_l["id"].max() + 1) if not df_l.empty else 1,
                        "book_id": bid,
                        "friend_id": fid,
                        "loan_date": date.today(),
                        "return_date": None
                    }])
                    df_l = pd.concat([df_l, new_loan], ignore_index=True)
                    save_data(df_l, "loans.csv")
                    log_activity(b_title, f_name, "LOAN_ISSUED")
                    st.success(f"Success! '{b_title}' lent to {f_name}."); time.sleep(1); st.rerun()
        else:
            st.warning("No books are currently available.")
    else:
        st.error("Please add books and friends first.")

elif choice == "Return Book":
    st.title(f"Liane's Personal Library — {choice}")
    df_b = load_data("books.csv")
    df_l = load_data("loans.csv")
    df_f = load_data("friends.csv")

    if not df_l.empty:
        active_loans = df_l[df_l["return_date"].isna() | (df_l["return_date"] == "")]
        if not active_loans.empty:
            loan_display = active_loans.merge(df_b[['id', 'title']], left_on='book_id', right_on='id')
            loan_display = loan_display.merge(df_f[['id', 'name']], left_on='friend_id', right_on='id')
            target_title = st.selectbox("Book to return", loan_display["title"])
            if st.button("Mark as Returned"):
                selected_loan = loan_display[loan_display["title"] == target_title].iloc[0]
                df_l.loc[df_l["id"] == selected_loan["id_x"], "return_date"] = date.today()
                save_data(df_l, "loans.csv")
                df_b.loc[df_b["id"] == selected_loan["book_id"], "status"] = "Available"
                save_data(df_b, "books.csv")
                log_activity(target_title, selected_loan["name"], "BOOK_RETURNED")
                st.success(f"'{target_title}' is now back in the library!"); time.sleep(1); st.rerun()
        else:
            st.info("No books are currently borrowed.")

elif choice == "Activity History":
    st.title(f"Liane's Personal Library — {choice}")
    df_h = load_data("activity_log.csv")
    if not df_h.empty:
        action_map = {
            "BOOK_ADDED": "📥 Book Added", 
            "BOOK_DELETED": "🗑️ Book Deleted", 
            "FRIEND_ADDED": "👤 Friend Added", 
            "FRIEND_DELETED": "🗑️ Friend Deleted",
            "LOAN_ISSUED": "📤 Book Borrowed", 
            "BOOK_RETURNED": "📥 Book Returned"
        }
        df_h["action_type"] = df_h["action_type"].map(action_map).fillna(df_h["action_type"])
        df_display = df_h.sort_values("action_date", ascending=False)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")