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

## 🛠️ 실행 방법

```bash
python main.py
