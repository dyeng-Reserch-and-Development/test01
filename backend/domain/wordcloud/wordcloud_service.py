from .wordcloud_model import WordCloudGenerator, WordCloudRequest, WordCloudConfig
import logging
import re
import os
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from typing import Optional
import base64
from io import BytesIO
from backend.infrastructure.wordcloud_repository import WordCloudRepository
import sys
from bareunpy import Tagger


logger = logging.getLogger(__name__)

class WordCloudService:
    def __init__(self):
        self.generator = WordCloudGenerator()
        self.logger = logging.getLogger(__name__)
        self._last_word_frequency = None  # 마지막 단어 빈도수 데이터 저장
        self.repository = WordCloudRepository()
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 영어와 숫자 제거
        text = re.sub(r'[a-zA-Z0-9]+', '', text)
        # 특수문자 제거
        text = re.sub(r'[^\w\s]', '', text)

        return text

    def _get_font_path(self, font_name: str, text: str) -> str:
        """폰트 경로 반환"""
        # 기본 폰트 디렉토리
        font_dir = r"C:\Windows\Fonts"
        
        # 기본 한글 폰트 (폴백용)
        default_korean_font = os.path.join(font_dir, "malgun.ttf")
        
        self.logger.debug(f"요청된 폰트: {font_name}")
        
        # 폰트 파일 경로
        font_path = os.path.join(font_dir, font_name)
        
        # 폰트 파일이 존재하지 않으면 기본 폰트 사용
        if not os.path.exists(font_path):
            self.logger.warning(f"폰트 파일을 찾을 수 없음: {font_name}, 기본 폰트 사용")
            return default_korean_font
        
        return font_path

    def _create_mask(self, mask_type: str, width: int, height: int) -> np.ndarray:
        """마스크 생성"""
        import numpy as np
        from PIL import Image, ImageDraw

        # 마스크 이미지 생성
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)

        if mask_type == "circle":
            # 원형 마스크
            padding = 10
            diameter = min(width, height) - (2 * padding)
            x1 = (width - diameter) // 2
            y1 = (height - diameter) // 2
            x2 = x1 + diameter
            y2 = y1 + diameter
            draw.ellipse([x1, y1, x2, y2], fill=255)

        elif mask_type == "heart":
            # 하트 모양 마스크
            padding = 0  # 패딩 제거
            heart_width = min(width, height)
            heart_height = heart_width
            
            # 하트 중심점 계산
            center_x = width // 2
            center_y = height // 2
            
            # 하트 크기 조절 (크기 2배 증가)
            scale = heart_width / 30.0  # 스케일 값을 더 줄여서 크기 2배 증가
            
            # 하트 모양 좌표 (더 깊은 골을 가진 형태)
            heart_points = []
            for t in np.linspace(0, np.pi * 2, 200):
                x = 16 * np.sin(t) ** 3
                y = -(13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t))
                
                # 크기 조절 및 중앙 정렬
                x = center_x + int(x * scale)
                y = center_y + int(y * scale * 0.9)  # 세로 비율 약간 조정
                
                heart_points.append((x, y))
            
            # 하트 그리기
            draw.polygon(heart_points, fill=255)

        elif mask_type == "rectangle":
            # 직사각형 마스크
            padding = 10
            draw.rectangle([padding, padding, width-padding, height-padding], fill=255)

        else:
            # 기본값: 전체 영역
            draw.rectangle([0, 0, width, height], fill=255)

        # 마스크를 numpy 배열로 변환
        mask_array = np.array(mask)
        
        # 마스크 반전 (텍스트가 들어갈 영역을 0으로)
        mask_array = 255 - mask_array
        
        return mask_array

    def create_wordcloud(self, text: str, config: Optional[WordCloudConfig] = None):
        """
        워드클라우드를 생성하고 이미지와 단어 데이터를 반환합니다.
        
        Args:
            text: 워드클라우드를 생성할 텍스트
            config: 워드클라우드 생성 설정
            
        Returns:
            워드클라우드 정보를 담은 딕셔너리
        """
        try:
            self.logger.info("워드클라우드 생성 시작")
            self.logger.debug(f"입력 텍스트: {text[:100]}...")  # 처음 100자만 로깅
            
            # 기본 설정값 사용
            if config is None:
                config = WordCloudConfig(text=text)
                self.logger.debug("기본 설정값 사용")
            else:
                config.text = text  # 입력받은 텍스트로 설정
                self.logger.debug(f"사용자 설정값 사용: {config}")
            
            # 텍스트 전처리 (WordCloudGenerator에서 수행)
            if not text.strip():
                raise ValueError("텍스트가 비어있거나 유효하지 않습니다.")
            

            # 텍스트 전처리


            # 그냥 서비스단에서 심플 전처리
            processed_text = self._preprocess_text(text)

            self.logger.debug(f"전처리된 텍스트: {processed_text[:100]}...")
            
            if not processed_text.strip():
                raise ValueError("텍스트가 비어있거나 유효하지 않습니다.")
            
            # 단어 빈도수 계산


            API_KEY="koba-5E34BFY-27YUXYI-QW4U6KY-CCEEYIA" # <- 본인의 API KEY로 교체 

            # 방금 설치한 자신의 호스트에 접속합니다.
            tagger = Tagger(API_KEY, 'localhost',5757)
            # 결과를 가져옵니다.

            # words = processed_text.split()
            res = tagger.tags([text])
            words = res.nouns()
            word_counts = {}
            total_words = 0
            for word in words:
                if len(word) >= 1:  # 1글자 이상인 단어만 포함
                    word_counts[word] = word_counts.get(word, 0) + 1
                    total_words += 1
            
            # 빈도수 기준으로 정렬
            sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
            word_frequency = [
                {
                    "word": word,
                    "frequency": count,
                    "percentage": (count / total_words * 100) if total_words > 0 else 0
                }
                for word, count in sorted_words
            ]
            
            # 단어 빈도수 데이터 저장
            word_frequency_data = [
                {
                    "word": word,
                    "frequency": freq,
                    "percentage": round((freq / total_words) * 100, 2)
                }
                for word, freq in word_counts.items()
            ]
            
            # 데이터 저장
            self._last_word_frequency = word_frequency_data
            

            # 폰트 경로 가져오기
            font_path = self._get_font_path(config.font or "malgun.ttf", text)
            self.logger.debug(f"사용할 폰트 경로: {font_path}")
            config.font_path = font_path
            
            # 마스크 생성
            mask = self._create_mask(config.mask_type, config.width, config.height)
            self.logger.debug(f"마스크 생성 완료: 타입={config.mask_type}, 크기={mask.shape if mask is not None else 'None'}")
            config.mask = mask  # 마스크 설정
                
            # 워드클라우드 이미지 생성
            try:
                # 워드클라우드 이미지 생성
                image = self.generator.generate(config)
                self.logger.debug("워드클라우드 생성 완료")
                
                # 이미지를 base64로 변환
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                self.logger.info("워드클라우드 생성 및 변환 완료")
                self.logger.debug(f"Base64 이미지 길이: {len(img_base64)}")
                
                # Generator에서 단어 빈도수 가져오기
                word_counts = self.generator.get_last_word_counts()
                word_frequency = []

                if word_counts and len(word_counts) > 0:  
                    self.logger.info("단어 빈도수 계산 시작")
                    total_words = sum(word_counts.values())
                    word_frequency = [
                        {
                            "word": word,
                            "frequency": count,
                            "percentage": round((count / total_words * 100), 2)
                        }
                        for word, count in sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
                    ]
                    self._last_word_frequency = word_frequency
                    self.logger.info(f"단어 빈도수 계산 완료: {len(word_frequency)}개 단어")
                    
                    try:
                        # DB에 저장
                        self.logger.info("워드클라우드 데이터 DB 저장 시작")
                        self.logger.debug(f"저장할 단어 데이터: {word_frequency[:5]}...")
                        word_data = [(item["word"], item["frequency"], item["percentage"]) for item in word_frequency]
                        wordcloud_id = self.repository.create_wordcloud("워드클라우드", word_data)
                        self.logger.info(f"워드클라우드 데이터 DB 저장 완료 (ID: {wordcloud_id})")
                    except Exception as e:
                        self.logger.error(f"워드클라우드 데이터 DB 저장 실패: {str(e)}")
                        self.logger.exception("상세 에러:")
                        wordcloud_id = None  
                else:
                    self.logger.warning("단어 빈도수 데이터가 없습니다")
                    wordcloud_id = None
                
                if img_base64:
                    self.logger.info("워드클라우드 이미지 생성 성공")
                    return {
                        'success': True,
                        'message': '워드클라우드가 생성되었습니다.',
                        'data': {
                            'wordcloud_id': wordcloud_id,
                            'image': img_base64,
                            'word_frequency': word_frequency[:100]  
                        }
                    }
                else:
                    self.logger.error("워드클라우드 이미지 생성 실패: base64 변환 결과가 비어있습니다")
                    return {
                        'success': False,
                        'message': '워드클라우드 이미지 생성에 실패했습니다.',
                        'data': {
                            'wordcloud_id': wordcloud_id,
                            'word_frequency': word_frequency[:100]  
                        }
                    }
            except Exception as e:
                self.logger.error(f"워드클라우드 이미지 생성 중 오류 발생: {str(e)}")
                return {
                    'success': False,
                    'message': f'워드클라우드 생성 중 오류가 발생했습니다: {str(e)}',
                    'data': {
                        'wordcloud_id': None,
                        'word_frequency': word_frequency[:100]  
                    }
                }
            
        except Exception as e:
            self.logger.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_text_file(self, file) -> dict:
        """
        텍스트 파일을 처리하여 워드클라우드를 생성합니다.
        
        Args:
            file: 업로드된 텍스트 파일 객체
            
        Returns:
            워드클라우드 정보를 담은 딕셔너리
        """
        try:
            # 파일 확장자 검사
            if not file.filename.lower().endswith('.txt'):
                raise ValueError("Only .txt files are allowed")
            
            # 파일 내용 읽기
            content = file.read().decode('utf-8')
            
            # 워드클라우드 생성
            return self.create_wordcloud(content)
            
        except UnicodeDecodeError:
            raise ValueError("Invalid text file encoding. Please ensure the file is UTF-8 encoded.")
        except Exception as e:
            self.logger.error(f"Error processing text file: {str(e)}")
            raise

    def get_last_word_frequency(self):
        """마지막으로 생성된 워드클라우드의 단어 빈도수 데이터 반환"""
        return self._last_word_frequency