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

logger = logging.getLogger(__name__)

class WordCloudService:
    def __init__(self):
        self.generator = WordCloudGenerator()
        self.logger = logging.getLogger(__name__)
    
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
            
            # 텍스트 전처리
            text = self._preprocess_text(text)
            self.logger.debug(f"전처리된 텍스트: {text[:100]}...")
            
            if not text.strip():
                raise ValueError("텍스트가 비어있거나 유효하지 않습니다.")
            
            # 폰트 경로 가져오기
            font_path = self._get_font_path(config.font or "malgun.ttf", text)
            self.logger.debug(f"사용할 폰트 경로: {font_path}")
            config.font_path = font_path
            
            # 마스크 생성
            mask = self._create_mask(config.mask_type, config.width, config.height)
            self.logger.debug(f"마스크 생성 완료: 타입={config.mask_type}, 크기={mask.shape if mask is not None else 'None'}")
            config.mask = mask  # 마스크 설정
                
            # 워드클라우드 생성
            image = self.generator.generate(config)
            self.logger.debug("워드클라우드 생성 완료")
            
            # 이미지를 base64로 변환
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            self.logger.info("워드클라우드 생성 및 변환 완료")
            
            return {
                'image': img_str,
                'words': []  # 단어 데이터는 나중에 추가
            }
            
        except Exception as e:
            self.logger.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
            raise
