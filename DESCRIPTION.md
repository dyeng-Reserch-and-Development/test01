# WordCloud Generator - 프로젝트 구조 설명

## 프로젝트 개요
이 프로젝트는 도메인 주도 설계(DDD) 패턴을 기반으로 한 워드클라우드 생성 애플리케이션입니다. Python 백엔드와 Electron 프론트엔드를 결합하여 데스크톱 애플리케이션으로 구현되었습니다.

## 디렉토리 구조
```
python_project/
├── backend/                # 백엔드 애플리케이션
│   ├── domain/            # 도메인 계층
│   │   └── wordcloud/     # 워드클라우드 도메인
│   │       ├── wordcloud_model.py    # 핵심 비즈니스 로직
│   │       └── wordcloud_service.py  # 서비스 계층
│   └── api/               # API 계층
│       └── routes.py      # FastAPI 라우트 정의
├── frontend/              # Electron 프론트엔드
│   ├── src/              # 프론트엔드 소스코드
│   │   ├── index.html    # 메인 HTML
│   │   ├── index.js      # 프론트엔드 로직
│   │   └── styles.css    # 스타일시트
│   ├── main.js           # Electron 메인 프로세스
│   └── package.json      # Node.js 의존성 정의
└── requirements.txt       # Python 의존성 정의
```

## 컴포넌트 상세 설명

### 1. 백엔드 (Backend)

#### 도메인 계층 (Domain Layer)
- **wordcloud_model.py**
  - 워드클라우드 생성의 핵심 비즈니스 로직 포함
  - WordCloudConfig: 워드클라우드 설정을 위한 데이터 클래스
  - WordCloudGenerator: 워드클라우드 이미지 생성 클래스
  - 텍스트 전처리 및 이미지 생성 기능 구현

- **wordcloud_service.py**
  - 모델과 API 계층 사이의 중간 계층
  - 이미지 변환 및 바이트 처리 담당
  - 비즈니스 로직 캡슐화

#### API 계층 (API Layer)
- **routes.py**
  - FastAPI 기반 REST API 엔드포인트
  - HTTP 요청/응답 처리
  - CORS 설정 및 에러 핸들링
  - 클라이언트-서버 통신 관리

### 2. 프론트엔드 (Frontend)

#### 소스 코드 (Source Code)
- **index.html**
  - 사용자 인터페이스 구조 정의
  - 텍스트 입력 필드와 버튼 구현
  - 워드클라우드 이미지 표시 영역

- **index.js**
  - 사용자 이벤트 처리 로직
  - 백엔드 API 통신
  - 에러 핸들링
  - UI 상태 관리 및 업데이트

- **styles.css**
  - UI 컴포넌트 스타일링
  - 반응형 디자인 구현
  - 시각적 피드백 스타일

#### Electron 설정
- **main.js**
  - Electron 애플리케이션 초기화
  - 메인 윈도우 생성 및 관리
  - IPC 통신 설정

- **package.json**
  - 프로젝트 메타데이터
  - npm 의존성 관리
  - 실행 스크립트 정의

### 3. 의존성 관리
- **requirements.txt**
  - Python 패키지 의존성 정의
  - 버전 관리
  - 필요한 라이브러리 목록

## 아키텍처 장점

1. **관심사의 분리**
   - 각 컴포넌트가 독립적인 역할 수행
   - 코드의 모듈화로 인한 개발 효율성 향상
   - 명확한 책임 분리

2. **유지보수성**
   - 모듈화된 구조로 코드 수정 용이
   - 독립적인 컴포넌트 업데이트 가능
   - 문제 발생 시 빠른 원인 파악

3. **확장성**
   - 새로운 기능 추가가 용이
   - 기존 코드 수정 없이 기능 확장 가능
   - 모듈 단위의 기능 개발

4. **테스트 용이성**
   - 각 계층별 독립적인 테스트 가능
   - 단위 테스트 작성 용이
   - 통합 테스트 구현 가능

## 기술 스택
- Backend: Python (FastAPI)
- Frontend: Electron, HTML, CSS, JavaScript
- 데이터 처리: WordCloud, NumPy
- 이미지 처리: Pillow

이 구조는 자바의 계층형 아키텍처와 유사하지만, Python의 특성을 살려 더 유연하게 구성되어 있습니다.
