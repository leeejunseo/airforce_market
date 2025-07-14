# ✈️ 공군마켓 (AirForce Market)

공군사관학교 생도들을 위한 중고 물품 거래 플랫폼입니다.  
Tkinter GUI 기반으로, 사용자가 직접 물품을 등록하고 구매하며 포인트를 통해 거래할 수 있도록 설계되었습니다.

---

## 💡 주요 기능

### 👤 사용자 기능
- 회원가입 / 로그인 (비밀번호 bcrypt 암호화)
- 포인트 시스템: 가입 3포인트, 등록 1포인트, 구매 1포인트 차감
- 상품 등록 / 목록 보기 / 가격 정렬
- 상품 상세 보기 및 장바구니에 담기
- 장바구니에서 다중 상품 일괄 구매
- 테마 전환 (밝은/어두운 테마)

### 👨‍✈️ 관리자 기능
- 관리자 전용 계정 자동 생성 (`admin / admin123`)
- 관리자 로그인 시 관리자 메뉴 활성화
- 모든 사용자 목록 확인 기능 제공

---

## 🖥️ 기술 스택

- Python + Tkinter (GUI)
- SQLite3 (로컬 데이터베이스)
- bcrypt (비밀번호 보안 처리)
- PIL (이미지 처리)
- 모듈 분리: `admin.py`, `theme.py` 등

---

## 📦 DB 구조

| Table | 설명 |
|-------|------|
| users | 사용자 정보 (id, username, password, is_admin, point) |
| products | 상품 정보 (id, name, price, description, seller_id) |
| cart | 장바구니 (user_id, product_id) |

---

## 🛠️ 상품 삽입, 삭제 코드

### 🧩 샘플 상품 삽입 (admin 계정 기준)
```python
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
```

### 🧹 상품 전체 삭제
```python
import sqlite3

def delete_all_products():
    db_file = "airforce_market.db"

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 상품 전체 삭제
        cursor.execute("DELETE FROM products")
        conn.commit()

        print("✅ 모든 상품이 성공적으로 삭제되었습니다.")

    except sqlite3.Error as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    delete_all_products()
```

### 📌 관련 SQL 문
```sql
-- admin 계정 ID 확인
SELECT id FROM users WHERE username = 'admin';

-- 모든 상품 삭제
DELETE FROM products;
```
