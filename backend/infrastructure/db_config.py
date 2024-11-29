import sqlite3
import os
import sys
from contextlib import contextmanager

def get_db_directory():
    """데이터베이스 파일이 저장될 디렉토리 경로를 반환"""
    if getattr(sys, 'frozen', False):  # EXE로 실행될 때
        app_data = os.getenv('LOCALAPPDATA')
        db_dir = os.path.join(app_data, 'WordCloudApp')  # 앱 이름 지정
    else:  # 개발 모드로 실행될 때
        db_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    return db_dir

# 데이터베이스 파일 경로 설정
DATABASE_PATH = os.path.join(get_db_directory(), 'wordcloud.db')

@contextmanager
def get_db_connection():
    """데이터베이스 연결을 관리하는 컨텍스트 매니저"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
        yield conn
    finally:
        if conn:
            conn.close()

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 워드 클라우드 기본 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wordcloud_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 원본 단어 빈도수 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_frequencies_original (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wordcloud_id INTEGER,
                word TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                percentage REAL NOT NULL,
                FOREIGN KEY (wordcloud_id) REFERENCES wordcloud_history(id)
            )
        ''')
        
        # 편집 작업 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wordcloud_id INTEGER,
                edit_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (wordcloud_id) REFERENCES wordcloud_history(id)
            )
        ''')
        
        # 편집 작업 상세 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edit_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                edit_history_id INTEGER,
                word TEXT NOT NULL,
                target_word TEXT,
                FOREIGN KEY (edit_history_id) REFERENCES edit_history(id)
            )
        ''')
        
        conn.commit()

# 데이터베이스 초기화
if __name__ == '__main__':
    init_db()
