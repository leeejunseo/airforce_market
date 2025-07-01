import sqlite3

# 샘플 상품 리스트
products = [
    ("전투식량 3종 세트", 15000, "야전에서 유용한 전투식량 3종 세트입니다."),
    ("전투화 세트 (265mm)", 45000, "공군 정품 전투화. 방수 및 통기성 우수."),
    ("PX 전용 칫솔세트", 3000, "칫솔, 치약, 컵 구성. PX 정품."),
    ("공군 야전 점퍼", 65000, "방한용 공군 야전 점퍼. 사이즈 M."),
    ("전술 배낭", 52000, "수납력 좋은 군용 배낭 (40L)"),
    ("전투용 손전등", 12000, "야간 작전용 고휘도 LED 손전등."),
    ("PX 신상 초코파이", 4500, "한정판 초코파이! 달콤하고 촉촉해요."),
    ("공군 부대 마스코트 인형", 9000, "공군 공식 마스코트 인형입니다."),
    ("전술 벨트", 8500, "튼튼한 전술 벨트. 길이 조절 가능."),
    ("야전용 보온 텀블러", 18000, "스테인리스 야전용 텀블러. 500ml."),
]

# DB 연결
conn = sqlite3.connect("airforce_market.db")
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON")  # 외래키 제약 활성화

# admin 계정의 ID 가져오기
c.execute("SELECT id FROM users WHERE username = 'admin'")
admin_row = c.fetchone()

if admin_row:
    seller_id = admin_row[0]  # 👉 실제 ID: 3
    for name, price, desc in products:
        c.execute("INSERT INTO products (name, price, description, seller_id) VALUES (?, ?, ?, ?)",
                  (name, price, desc, seller_id))
    conn.commit()
    print(f"✅ admin 계정(ID={seller_id})으로 샘플 상품 {len(products)}개 삽입 완료!")
else:
    print("❌ 'admin' 계정이 존재하지 않습니다.")

conn.close()
