import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import sqlite3
import bcrypt
import os
from admin import admin_panel, set_current_user

current_user = None

def set_current_user(user):
    global current_user
    current_user = user


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
    set_current_user(current_user)
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
            
            from admin import set_current_user
            set_current_user(current_user)
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


    # 새 창 생성
    cart_win = tk.Toplevel(root)
    cart_win.title("🛒 장바구니")
    cart_win.geometry("400x400")
    cart_win.attributes('-topmost', True)
    cart_win.grab_set()
    cart_win.focus_set()


    # Treeview 생성
    columns = ("상품명", "가격")
    cart_tree = ttk.Treeview(cart_win, columns=columns, show="headings")
    cart_tree.heading("상품명", text="상품명")
    cart_tree.heading("가격", text="가격")
    cart_tree.column("상품명", anchor="center")
    cart_tree.column("가격", anchor="center")
    cart_tree.pack(fill="both", expand=True, padx=10, pady=10)


    # 데이터 불러오기
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT p.name, p.price FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=?",
              (current_user['id'],))
    items = c.fetchall()
    conn.close()


    # 데이터 삽입
    total = 0
    for name, price in items:
        cart_tree.insert("", "end", values=(name, f"{price}원"))
        total += price


    # 총합 표시
    total_label = tk.Label(cart_win, text=f"총합: {total}원", font=("Arial", 12, "bold"))
    total_label.pack(pady=5)


def delete_product():
    if not current_user:
        messagebox.showerror("오류", "로그인 필요")
        return
    selected = product_list.selection()
    if not selected:
        messagebox.showwarning("선택 오류", "삭제할 상품을 선택하세요.")
        return


    product_id = product_list.item(selected[0])['values'][0]


    # 본인 상품인지 확인
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT seller_id FROM products WHERE id=?", (product_id,))
    row = c.fetchone()
    if not row:
        messagebox.showerror("오류", "상품을 찾을 수 없습니다.")
        conn.close()
        return
    if row[0] != current_user['id']:
        messagebox.showerror("오류", "본인의 상품만 삭제할 수 있습니다.")
        conn.close()
        return


    # 삭제 확인
    confirm = messagebox.askyesno("삭제 확인", "정말로 이 상품을 판매 완료(삭제)하시겠습니까?")
    if confirm:
        c.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        messagebox.showinfo("삭제 완료", "상품이 삭제되었습니다.")
    conn.close()
    refresh_home()






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
# main.py 안 어딘가 (init_db 밑에 바로)

def create_default_admin():
    import bcrypt
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if c.fetchone() is None:
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("admin", hashed_pw, 1))
        conn.commit()
        print("✅ 관리자 계정(admin / admin123) 생성됨")
    conn.close()

create_default_admin()


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


# 버튼 프레임 생성
btn_frame = tk.Frame(root, bg="#f0f4f8")
btn_frame.pack(pady=10)


# 버튼 선언
btn_register = ttk.Button(btn_frame, text="회원가입", command=register)
btn_login = ttk.Button(btn_frame, text="로그인", command=login)
btn_logout = ttk.Button(btn_frame, text="로그아웃", command=logout)
btn_add = ttk.Button(btn_frame, text="상품등록", command=add_product)
btn_cart = ttk.Button(btn_frame, text="장바구니", command=view_cart)
btn_sell = ttk.Button(btn_frame, text="✅ 판매 완료(삭제)", command=delete_product)
btn_add_cart = ttk.Button(btn_frame, text="🛒 장바구니에 담기", command=add_to_cart)
btn_detail = ttk.Button(btn_frame, text="🔍 상세보기", command=show_selected_product_detail)

#관리자메뉴
btn_admin_menu = ttk.Button(btn_frame, text="👨‍✈️ 관리자 메뉴", command=admin_panel)
btn_admin_menu.grid(row=1, column=0, padx=5)
btn_admin_menu.grid_remove()  # 기본은 숨김

# 버튼들을 모두 한 줄에 정렬
btn_register.grid(row=0, column=0, padx=5)
btn_login.grid(row=0, column=1, padx=5)
btn_logout.grid(row=0, column=2, padx=5)
btn_add.grid(row=0, column=3, padx=5)
btn_cart.grid(row=0, column=4, padx=5)
btn_sell.grid(row=0, column=5, padx=5)
btn_admin_menu.grid(row=0, column=6, padx=5)
btn_add_cart.grid(row=0, column=7, padx=5)
btn_detail.grid(row=0, column=8, padx=5)




product_frame = ttk.LabelFrame(root, text="\ud83d\udce6 \uc0c1\ud488 \ubaa9\ub85d", padding=10)
product_frame.pack(fill="both", expand=True, padx=20, pady=20)
columns = ("ID", "상품명", "가격", "판매자")
product_list = ttk.Treeview(product_frame, columns=columns, show="headings", height=15)
for col in columns:
    product_list.heading(col, text=col)
    product_list.column(col, anchor="center")
product_list.pack(fill="both", expand=True)


def refresh_home():
    list_products()
    if current_user:
        login_status.config(text=f"현재 로그인: {current_user['username']}")
        btn_login.grid_remove()
        btn_register.grid_remove()
        btn_logout.grid()
        btn_admin_menu.grid()
    else:
        login_status.config(text="로그인 필요")
        btn_logout.grid_remove()
        btn_login.grid()
        btn_register.grid()
        btn_admin_menu.grid_remove()


refresh_home()
root.mainloop()
