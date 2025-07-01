import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

def get_db_connection():
    return sqlite3.connect("airforce_market.db")

def admin_panel(current_user):
    if not (current_user and current_user['is_admin'] == 1):
        messagebox.showerror("오류", "관리자만 접근 가능")
        return

    panel = tk.Toplevel()
    panel.title("👨‍✈️ 관리자 전용 메뉴")
    panel.geometry("400x320")
    panel.attributes('-topmost', True)
    panel.grab_set()

    tk.Label(panel, text="관리자 메뉴", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Button(panel, text="회원 목록 조회", width=25, command=view_all_users).pack(pady=5)
    ttk.Button(panel, text="사용자 삭제", width=25, command=lambda: delete_user(current_user)).pack(pady=5)
    ttk.Button(panel, text="상품 관리", width=25, command=manage_products).pack(pady=5)
    ttk.Button(panel, text="관리자 권한 부여", width=25, command=promote_user).pack(pady=5)

def view_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, is_admin FROM users")
    rows = c.fetchall()
    conn.close()

    win = tk.Toplevel()
    win.title("모든 사용자 보기")
    tree = ttk.Treeview(win, columns=("ID", "사용자명", "관리자 여부"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("사용자명", text="사용자명")
    tree.heading("관리자 여부", text="관리자 여부")
    for row in rows:
        is_admin = "✅" if row[2] else "❌"
        tree.insert("", "end", values=(row[0], row[1], is_admin))
    tree.pack(fill="both", expand=True)

def delete_user(current_user):
    user_id = simpledialog.askinteger("사용자 삭제", "삭제할 사용자 ID를 입력하세요:")
    if user_id is None:
        return
    if user_id == current_user['id']:
        messagebox.showerror("오류", "자기 자신은 삭제할 수 없습니다.")
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        messagebox.showerror("오류", "존재하지 않는 사용자입니다.")
        conn.close()
        return

    confirm = messagebox.askyesno("삭제 확인", f"{row[0]} 사용자를 정말 삭제하시겠습니까?")
    if confirm:
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        messagebox.showinfo("삭제 완료", "사용자가 삭제되었습니다.")
    conn.close()

def manage_products():
    win = tk.Toplevel()
    win.title("상품 관리")
    win.geometry("700x450")

    tree_frame = tk.Frame(win)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(tree_frame, columns=("ID", "상품명", "가격", "판매자 ID"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("상품명", text="상품명")
    tree.heading("가격", text="가격")
    tree.heading("판매자 ID", text="판매자 ID")

    tree.column("ID", width=50, anchor="center")
    tree.column("상품명", anchor="center")
    tree.column("가격", anchor="center")
    tree.column("판매자 ID", anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, seller_id FROM products")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("선택 없음", "삭제할 상품을 선택하세요.")
            return
        pid = tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("삭제 확인", f"상품 ID {pid}를 삭제하시겠습니까?")
        if confirm:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            tree.delete(selected[0])
            messagebox.showinfo("성공", "상품이 삭제되었습니다.")

    ttk.Button(win, text="선택 상품 삭제", command=delete_selected).pack(pady=5)

def promote_user():
    uid = simpledialog.askinteger("관리자 승격", "관리자로 만들 사용자 ID 입력:")
    if uid is None:
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin=1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    messagebox.showinfo("완료", f"사용자 {uid}가 관리자로 승격되었습니다.")
