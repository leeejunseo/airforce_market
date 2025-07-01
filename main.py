import tkinter as tk
import tkinter.ttk as ttk  # ✅ 핵심
from tkinter import messagebox, simpledialog  # ✅ OK
from PIL import Image, ImageTk
import sqlite3
import bcrypt
import os

from admin import admin_panel
from theme import apply_theme

current_user = None
is_dark_theme = False
price_sort_order = "ASC"  # 기본 정렬: 오름차순

root = tk.Tk()
apply_theme(root)  # 스타일 적용!
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
        is_admin INTEGER DEFAULT 0,
        point INTEGER DEFAULT 3
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
    reg_win.geometry("300x220")
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
    global current_user
    login_win = tk.Toplevel(root)
    login_win.title("로그인")
    login_win.geometry("300x200")
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

        print("입력한 사용자명:", username)
        print("입력한 비밀번호:", password)

        conn = sqlite3.connect("airforce_market.db")
        c = conn.cursor()
        c.execute("SELECT id, password, is_admin FROM users WHERE username=?", (username,))
        row = c.fetchone()
        print("DB에서 찾은 사용자 정보:", row)
        conn.close()

        if row and bcrypt.checkpw(password.encode(), row[1]):
            current_user = {'id': row[0], 'username': username, 'is_admin': row[2]}
            set_current_user(current_user)
            print("로그인 성공! current_user:", current_user)

            messagebox.showinfo("로그인", f"{username}님 환영합니다!", parent=login_win)
            login_win.destroy()
            refresh_home()
        else:
            print("로그인 실패")
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
        c.execute("UPDATE users SET point = point + 1 WHERE id = ?", (current_user['id'],))
        conn.commit()
        conn.close()


        messagebox.showinfo("성공", "상품을 등록했습니다.")
        prod_win.destroy()
        refresh_home()


    tk.Button(prod_win, text="등록", command=submit).pack(pady=5)


# -------------------- 상품 목록 --------------------
def list_products(order="ASC"):
    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    query = f"""
        SELECT p.id, p.name, p.price, u.username 
        FROM products p 
        JOIN users u ON p.seller_id = u.id 
        ORDER BY p.price {order}
    """
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    product_list.delete(*product_list.get_children())

    for i, column in enumerate(columns):
        if column == "가격":
            heading = "가격 ▼" if order == "DESC" else "가격 ▲"
        else:
            heading = column
        product_list.heading(column, text=heading)

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

    cart_win = tk.Toplevel(root)
    cart_win.title("🛒 장바구니")
    cart_win.geometry("500x500")
    cart_win.attributes('-topmost', True)
    cart_win.grab_set()
    cart_win.focus_set()

    columns = ("상품명", "가격")
    cart_tree = ttk.Treeview(cart_win, columns=columns, show="headings")
    cart_tree.heading("상품명", text="상품명")
    cart_tree.heading("가격", text="가격")
    cart_tree.column("상품명", anchor="center")
    cart_tree.column("가격", anchor="center")
    cart_tree.pack(fill="both", expand=True, padx=10, pady=10)

    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT p.id, p.name, p.price FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id=?",
              (current_user['id'],))
    items = c.fetchall()
    conn.close()

    total = 0
    for pid, name, price in items:
        cart_tree.insert("", "end", values=(name, f"{price}원"))
        total += price

    total_label = tk.Label(cart_win, text=f"총합: {total}원", font=("Arial", 12, "bold"))
    total_label.pack(pady=5)

    def purchase_items():
        conn = sqlite3.connect("airforce_market.db")
        c = conn.cursor()

        c.execute("SELECT product_id FROM cart WHERE user_id=?", (current_user['id'],))
        items = c.fetchall()
        count = len(items)

        c.execute("SELECT point FROM users WHERE id=?", (current_user['id'],))
        current_point = c.fetchone()[0]

        if count == 0:
            messagebox.showwarning("경고", "장바구니가 비어 있습니다.", parent=cart_win)
            conn.close()
            return
        if current_point < count:
            messagebox.showerror("포인트 부족", f"보유 포인트: {current_point} / 필요한 포인트: {count}", parent=cart_win)
            conn.close()
            return

        # 삭제: 장바구니 + 상품
        for pid in items:
            c.execute("DELETE FROM products WHERE id=?", (pid[0],))
        c.execute("DELETE FROM cart WHERE user_id=?", (current_user['id'],))
        c.execute("UPDATE users SET point = point - ? WHERE id=?", (count, current_user['id']))
        conn.commit()
        conn.close()

        messagebox.showinfo("구매 완료", f"{count}개의 상품을 구매했습니다.\n{count} 포인트 차감 및 상품 삭제 완료.", parent=cart_win)
        cart_win.destroy()
        refresh_home()

    tk.Button(cart_win, text="🛍 구매하기", command=purchase_items).pack(pady=5)


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



def refresh_home():
    list_products()
    if current_user:
        # 현재 포인트 가져오기
        conn = sqlite3.connect("airforce_market.db")
        c = conn.cursor()
        c.execute("SELECT point FROM users WHERE id=?", (current_user['id'],))
        pt = c.fetchone()[0]
        conn.close()

        # 로그인 상태 + 포인트 표시
        login_status.config(text=f"현재 로그인: {current_user['username']} (포인트: {pt})")

        btn_login.grid_remove()
        btn_register.grid_remove()
        btn_logout.grid()

        if current_user.get("is_admin") == 1:
            btn_admin_menu.grid()
        else:
            btn_admin_menu.grid_remove()
    else:
        login_status.config(text="로그인 필요")
        btn_logout.grid_remove()
        btn_login.grid()
        btn_register.grid()
        btn_admin_menu.grid_remove()



def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme

    if is_dark_theme:
        bg_color = "#2e2e2e"
        fg_color = "#ffffff"
    else:
        bg_color = "#f0f4f8"
        fg_color = "#000000"

    root.configure(bg=bg_color)
    top_frame.configure(bg=bg_color)
    logo_frame.configure(bg=bg_color)
    btn_frame.configure(bg=bg_color)
    login_status.configure(bg=bg_color, fg=fg_color)

    # 버튼도 재색칠하고 싶다면 Style 활용 가능


# -------------------- 상품 상세 보기 --------------------
def show_selected_product_detail():
    selected = product_list.selection()
    if not selected:
        return
    product_id = product_list.item(selected[0])['values'][0]

    conn = sqlite3.connect("airforce_market.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, description FROM products WHERE id=?", (product_id,))
    item = c.fetchone()
    conn.close()

    if item:
        detail_win = tk.Toplevel(root)
        detail_win.title("상품 상세 보기")
        detail_win.geometry("450x500")
        detail_win.attributes('-topmost', True)
        detail_win.grab_set()
        detail_win.focus_set()

        tk.Label(detail_win, text=f"상품명: {item[1]}", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(detail_win, text=f"가격: {item[2]}원", font=("Arial", 12)).pack(pady=5)
        desc = item[3] if item[3] else "설명 없음"
        tk.Label(detail_win, text=f"설명:\n{desc}", wraplength=400, justify="left").pack(pady=10)

        def add_from_detail():
            conn = sqlite3.connect("airforce_market.db")
            c = conn.cursor()
            c.execute("INSERT INTO cart (user_id, product_id) VALUES (?, ?)", (current_user['id'], item[0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("장바구니", "상품을 장바구니에 추가했습니다.", parent=detail_win)

        tk.Button(detail_win, text="🛒 장바구니 담기", command=add_from_detail).pack(pady=10)

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



root.title("공군마켓 - AirForce Market")
root.geometry("1000x700")
root.configure(bg="#f0f4f8")


logo_frame = tk.Frame(root, bg="#f0f4f8")
logo_frame.pack(pady=10)
if os.path.exists("airforce_logo.png"):
    logo_img = Image.open("airforce_logo.png")
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
# 기능 버튼
btn_register = ttk.Button(btn_frame, text="회원가입", style="Cool.TButton", command=register)
btn_login = ttk.Button(btn_frame, text="로그인", style="Cool.TButton", command=login)
btn_logout = ttk.Button(btn_frame, text="로그아웃", style="Cool.TButton", command=logout)
btn_add = ttk.Button(btn_frame, text="상품등록", style="Cool.TButton", command=add_product)
btn_cart = ttk.Button(btn_frame, text="장바구니", style="Cool.TButton", command=view_cart)
btn_refresh = ttk.Button(btn_frame, text="🔄 새로고침", style="Cool.TButton", command=refresh_home)
btn_theme = ttk.Button(btn_frame, text="🌓 테마 전환", style="Cool.TButton", command=toggle_theme)

# 관리자 메뉴
btn_admin_menu = ttk.Button(btn_frame, text="👨‍✈️ 관리자 메뉴", style="Cool.TButton", command=lambda: admin_panel(current_user))
btn_admin_menu.grid(row=0, column=6, padx=5)
btn_admin_menu.grid_remove()  # 기본 숨김


# 첫 번째 줄 버튼 배치
btn_register.grid(row=0, column=0, padx=5)
btn_login.grid(row=0, column=1, padx=5)
btn_logout.grid(row=0, column=2, padx=5)
btn_add.grid(row=0, column=3, padx=5)
btn_cart.grid(row=0, column=4, padx=5)
btn_admin_menu.grid(row=0, column=6, padx=5)
btn_refresh.grid(row=0, column=9, padx=5)

# 두 번째 줄
btn_theme.grid(row=1, column=0, padx=5, pady=5)

# 상품 목록 프레임
product_frame = ttk.LabelFrame(root, text="📦 상품 목록", padding=10)
product_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ⬇️ Treeview + Scrollbar 담을 프레임
tree_container = tk.Frame(product_frame)
tree_container.pack(fill="both", expand=True)

# Treeview 생성
columns = ("ID", "상품명", "가격", "판매자")
product_list = ttk.Treeview(tree_container, columns=columns, show="headings")

for col in columns:
    product_list.heading(col, text=col)
    product_list.column(col, anchor="center")
    
def on_treeview_header_click(event):
    global price_sort_order
    region = product_list.identify_region(event.x, event.y)
    col = product_list.identify_column(event.x)

    if region == "heading" and col == "#3":  # 가격 열
        price_sort_order = "DESC" if price_sort_order == "ASC" else "ASC"
        list_products(price_sort_order)

# ✅ Treeview 이벤트 바인딩 (헤더 클릭 감지)
product_list.bind("<Button-1>", on_treeview_header_click)
# ✅ 마우스 커서 바꾸기
product_list.bind("<Enter>", lambda e: product_list.config(cursor="hand2"))
product_list.bind("<Leave>", lambda e: product_list.config(cursor=""))
# ✅ 더블 클릭으로 상세보기 열기
product_list.bind("<Double-1>", lambda event: show_selected_product_detail())


# 스크롤바 추가
scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=product_list.yview)
product_list.configure(yscrollcommand=scrollbar.set)

# 배치
product_list.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")



refresh_home()
root.mainloop()
