from tkinter import ttk

def apply_theme(root):
    style = ttk.Style()
    style.theme_use("clam")  # 기본 테마 설정

    # Cool.TButton 스타일 정의
    style.configure("Cool.TButton",
                    font=("맑은 고딕", 10, "bold"),
                    foreground="#ffffff",
                    background="#007acc",
                    padding=6,
                    relief="flat",
                    borderwidth=1,
                    highlightthickness=0)

    style.map("Cool.TButton",
              background=[("active", "#228be6"), ("pressed", "#1c7ed6")],
              foreground=[("active", "#ffffff")])

    # Treeview 스타일 (상품 리스트)
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#212529",
                    rowheight=28,
                    fieldbackground="#ffffff",
                    font=("맑은 고딕", 10))
    style.map("Treeview",
              background=[("selected", "#339af0")],
              foreground=[("selected", "#ffffff")])

    # Treeview Heading 스타일
    style.configure("Treeview.Heading",
                    font=("맑은 고딕", 10, "bold"),
                    background="#e9ecef",
                    foreground="#343a40")

    # Entry 위젯 스타일
    style.configure("TEntry",
                    padding=5,
                    relief="flat",
                    font=("맑은 고딕", 10))

    # Label 스타일
    style.configure("TLabel",
                    font=("맑은 고딕", 10),
                    background="#f1f3f5",
                    foreground="#212529")

    # Text 위젯은 ttk에서 지원하지 않으므로 tkinter 직접 설정 필요

    # LabelFrame 스타일 (상품 목록 상자 등)
    style.configure("TLabelframe",
                    background="#f1f3f5",
                    borderwidth=1,
                    relief="solid")
    style.configure("TLabelframe.Label",
                    font=("맑은 고딕", 11, "bold"),
                    background="#f1f3f5",
                    foreground="#343a40")

    # 전체 배경 색 설정
    root.configure(bg="#f0f4f8")
