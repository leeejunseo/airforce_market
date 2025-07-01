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
