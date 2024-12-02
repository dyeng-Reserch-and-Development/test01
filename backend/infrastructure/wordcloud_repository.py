from typing import Dict, List, Optional
from datetime import datetime
import logging
import sqlite3
from backend.infrastructure.db_config import get_db_connection, init_db

class WordCloudRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        init_db()  # DB 초기화

    @staticmethod
    def create_wordcloud(name: str, word_data: List[tuple]) -> int:
        """
        새로운 워드 클라우드를 생성하고 단어별 데이터를 저장합니다.
        
        Args:
            name: 워드 클라우드 이름
            word_data: [(단어, 빈도수, 퍼센트), ...] 형식의 리스트
            
        Returns:
            생성된 워드 클라우드의 ID
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 워드 클라우드 기본 정보 저장
            cursor.execute('''
                INSERT INTO wordcloud_history (name)
                VALUES (?)
            ''', (name,))
            
            wordcloud_id = cursor.lastrowid
            
            # 단어별 데이터 저장
            word_freq_data = [
                (wordcloud_id, word, frequency, percentage)
                for word, frequency, percentage in word_data
            ]
            
            cursor.executemany('''
                INSERT INTO word_frequencies_original (wordcloud_id, word, frequency, percentage)
                VALUES (?, ?, ?, ?)
            ''', word_freq_data)
            
            conn.commit()
            return wordcloud_id
    
    @staticmethod
    def get_wordcloud(wordcloud_id: int) -> Optional[dict]:
        """
        워드 클라우드의 기본 정보와 단어별 데이터를 조회합니다.
        
        Args:
            wordcloud_id: 조회할 워드 클라우드 ID
            
        Returns:
            워드 클라우드 정보를 담은 딕셔너리 또는 None
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"조회하는 워드클라우드 ID: {wordcloud_id}")
        
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 기본 정보 조회
            cursor.execute('''
                SELECT id, name, created_at
                FROM wordcloud_history
                WHERE id = ?
            ''', (wordcloud_id,))
            
            wordcloud = cursor.fetchone()
            if not wordcloud:
                return None
                
            # 단어별 데이터 조회
            cursor.execute('''
                SELECT word, frequency, percentage
                FROM word_frequencies_original
                WHERE wordcloud_id = ?
                ORDER BY percentage DESC
            ''', (wordcloud_id,))
            
            word_data = [
                {
                    'word': row['word'],
                    'frequency': row['frequency'],
                    'percentage': row['percentage']
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'id': wordcloud['id'],
                'name': wordcloud['name'],
                'created_at': wordcloud['created_at'],
                'words': word_data
            }
    
    @staticmethod
    def get_all_wordclouds() -> List[dict]:
        """
        모든 워드 클라우드의 기본 정보를 조회합니다.
        
        Returns:
            워드 클라우드 정보 리스트
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, created_at
                FROM wordcloud_history
                ORDER BY created_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
