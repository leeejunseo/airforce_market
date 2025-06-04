import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import sqlite3
import bcrypt
import os

# -------------------- DB 초기화 --------------------
def init_db():
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        description TEXT,
        seller_id INTEGER,
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    conn.commit()
    conn.close()

# -------------------- 사용자 등록 --------------------
def register():
    reg_win = tk.Toplevel(root)
    reg_win.title("회원가입")
    reg_win.attributes('-topmost', True)
    reg_win.grab_set()
    reg_win.focus_set()

    tk.Label(reg_win, text="사용자 이름:").pack()
    username_entry = tk.Entry(reg_win)
    username_entry.pack()

    tk.Label(reg_win, text="비밀번호:").pack()
    password_entry = tk.Entry(reg_win, show='*')
    password_entry.pack()

    def submit():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            try:
                conn = sqlite3.connect("airforce_market.db")
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
                conn.commit()
                conn.close()
                messagebox.showinfo("회원가입", "회원가입 성공!", parent=reg_win)
                reg_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("에러", "이미 존재하는 사용자입니다.", parent=reg_win)

    tk.Button(reg_win, text="가입하기", command=submit).pack(pady=5)

# -------------------- 로그인 --------------------
def login():
    login_win = tk.Toplevel(root)
    login_win.title("로그인")
    login_win.attributes('-topmost', True)
    login_win.grab_set()
    login_win.focus_set()

    tk.Label(login_win, text="사용자 이름:").pack()
    username_entry = tk.Entry(login_win)
    username_entry.pack()

    tk.Label(login_win, text="비밀번호:").pack()
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack()

    def submit():
        global current_user
        username = username_entry.get()
        password = password_entry.get()

        conn = sqlite3.connect("airforce_market.db")
        c = conn.cursor()
        c.execute("SELECT id, password, is_admin FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()

        if row and bcrypt.checkpw(password.encode(), row[1]):
            current_user = {'id': row[0], 'username': username, 'is_admin': row[2]}
            messagebox.showinfo("로그인", f"{username}님 환영합니다!", parent=login_win)
            login_win.destroy()
            refresh_home()
        else:
            messagebox.showerror("실패", "로그인 실패", parent=login_win)

    tk.Button(login_win, text="로그인", command=submit).pack(pady=5)

# -------------------- 로그아웃 --------------------
def logout():
    global current_user
    current_user = None
    messagebox.showinfo("로그아웃", "로그아웃 완료")
    refresh_home()

# -------------------- 상품 등록 --------------------
def add_product():
    if not current_user:
        messagebox.showerror("오류", "로그인 필요")
        return

    prod_win = tk.Toplevel(root)
    prod_win.title("상품 등록")
    prod_win.attributes('-topmost', True)
    prod_win.grab_set()
    prod_win.focus_set()

    tk.Label(prod_win, text="상품 이름:").pack()
    name_entry = tk.Entry(prod_win)
    name_entry.pack()

    tk.Label(prod_win, text="가격:").pack()
    price_entry = tk.Entry(prod_win)
    price_entry.pack()

    tk.Label(prod_win, text="설명:").pack()
    desc_entry = tk.Text(prod_win, height=5, width=40)
    desc_entry.pack()

    def submit():
        name = name_entry.get()
        try:
            price = int(price_entry.get())
        except:
            messagebox.showerror("오류", "가격은 숫자여야 합니다.")
            return
        description = desc_entry.get("1.0", "end").strip()

        if not name or not description:
            messagebox.showwarning("입력 오류", "모든 항목을 입력해야 합니다.")
            return

        conn = sqlite3.connect("airforce_market.db")
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, description, seller_id) VALUES (?, ?, ?, ?)",
                  (name, price, description, current_user['id']))
        conn.commit()
        conn.close()

        messagebox.showinfo("성공", "상품을 등록했습니다.")
        prod_win.destroy()
        refresh_home()

    tk.Button(prod_win, text="등록", command=submit).pack(pady=5)

# -------------------- 상품 목록 --------------------
def list_products():
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT p.id, p.name, p.price, u.username FROM products p JOIN users u ON p.seller_id = u.id")
    rows = c.fetchall()
    conn.close()
    product_list.delete(*product_list.get_children())
    for row in rows:
        product_list.insert("", "end", values=(row[0], row[1], f"{row[2]}원", row[3]))

# -------------------- 장바구니 --------------------
def add_to_cart():
    if not current_user:
        messagebox.showerror("오류", "로그인 필요")
        return
    selected = product_list.selection()
    if not selected:
        return
    product_id = product_list.item(selected[0])['values'][0]
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (current_user['id'], product_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("장바구니", "상품을 장바구니에 추가했습니다.")

def view_cart():
    if not current_user:
        messagebox.showerror("오류", "로그인 필요")
        return
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT p.name, p.price FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=?",
              (current_user['id'],))
    items = c.fetchall()
    conn.close()
    total = sum(price for _, price in items)
    item_str = "\n".join([f"{name} - {price}원" for name, price in items])
    messagebox.showinfo("장바구니", f"{item_str}\n\n총합: {total}원")

# -------------------- 상품 상세 보기 --------------------
def show_selected_product_detail():
    selected = product_list.selection()
    if not selected:
        return
    product_id = product_list.item(selected[0])['values'][0]

    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT name, price, description FROM products WHERE id=?", (product_id,))
    item = c.fetchone()
    conn.close()

    if item:
        detail_win = tk.Toplevel(root)
        detail_win.title("상품 상세 보기")
        detail_win.attributes('-topmost', True)
        detail_win.grab_set()
        detail_win.focus_set()

        tk.Label(detail_win, text=f"상품명: {item[0]}", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(detail_win, text=f"가격: {item[1]}원", font=("Arial", 12)).pack(pady=5)
        desc = item[2] if item[2] else "설명 없음"
        tk.Label(detail_win, text=f"설명:\n{desc}", wraplength=400, justify="left").pack(pady=10)

# -------------------- 관리자 기능 --------------------
def view_all_users():
    if not (current_user and current_user['is_admin']):
        messagebox.showerror("오류", "관리자만 접근 가능")
        return
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT id, username FROM users")
    rows = c.fetchall()
    conn.close()
    user_list = "\n".join([f"[{uid}] {uname}" for uid, uname in rows])
    messagebox.showinfo("모든 사용자", user_list)

# -------------------- 메인 GUI --------------------
current_user = None
init_db()

root = tk.Tk()
root.title("공군마켓 - AirForce Market")
root.geometry("1200x700")
root.configure(bg="#f0f4f8")

logo_frame = tk.Frame(root, bg="#f0f4f8")
logo_frame.pack(pady=10)
if os.path.exists("airforce_logo.png"):
    logo_img = Image.open("airforce_logo.png").resize((300, 230))
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(logo_frame, image=logo_photo, bg="#f0f4f8").pack()

top_frame = tk.Frame(root, bg="#f0f4f8")
top_frame.pack()
login_status = tk.Label(top_frame, text="로그인 필요", bg="#f0f4f8", font=("Arial", 12, "bold"))
login_status.pack(pady=5)

btn_frame = tk.Frame(root, bg="#f0f4f8")
btn_frame.pack()
btn_register = ttk.Button(btn_frame, text="회원가입", command=register)
btn_login = ttk.Button(btn_frame, text="로그인", command=login)
btn_logout = ttk.Button(btn_frame, text="로그아웃", command=logout)
btn_add = ttk.Button(btn_frame, text="상품등록", command=add_product)
btn_cart = ttk.Button(btn_frame, text="장바구니", command=view_cart)
btn_admin = ttk.Button(btn_frame, text="회원관리(관리자)", command=view_all_users)
btn_register.grid(row=0, column=0, padx=5)
btn_login.grid(row=0, column=1, padx=5)
btn_logout.grid(row=0, column=2, padx=5)
btn_add.grid(row=0, column=3, padx=5)
btn_cart.grid(row=0, column=4, padx=5)
btn_admin.grid(row=0, column=5, padx=5)

product_frame = ttk.LabelFrame(root, text="\ud83d\udce6 \uc0c1\ud488 \ubaa9\ub85d", padding=10)
product_frame.pack(fill="both", expand=True, padx=20, pady=20)
columns = ("ID", "상품명", "가격", "판매자")
product_list = ttk.Treeview(product_frame, columns=columns, show="headings", height=15)
for col in columns:
    product_list.heading(col, text=col)
    product_list.column(col, anchor="center")
product_list.pack(fill="both", expand=True)

ttk.Button(root, text="\ud83d\uded2 \uc7a5\ubc14\uadf8\ub2c8\uc5d0 \ub2f4\uae30", command=add_to_cart).pack(pady=5)
ttk.Button(root, text="\ud83d\udd0d \uc0c1\uc138\ubcf4\uae30", command=show_selected_product_detail).pack(pady=5)

def refresh_home():
    list_products()
    if current_user:
        login_status.config(text=f"현재 로그인: {current_user['username']}")
        btn_login.grid_remove()
        btn_register.grid_remove()
        btn_logout.grid()
    else:
        login_status.config(text="로그인 필요")
        btn_logout.grid_remove()
        btn_login.grid()
        btn_register.grid()

refresh_home()
root.mainloop()
