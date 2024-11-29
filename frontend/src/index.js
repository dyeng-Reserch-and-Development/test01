document.addEventListener('DOMContentLoaded', async () => {
    const textInput = document.getElementById('text-input');
    const generateBtn = document.getElementById('generate-btn');
    const wordcloudImage = document.getElementById('wordcloud-image');
    const downloadBtn = document.getElementById('download-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const backgroundColorSelect = document.getElementById('background-color');
    const colorFuncSelect = document.getElementById('color-func');
    const maskTypeSelect = document.getElementById('mask-type');
    const fontSelect = document.getElementById('fontSelect');
    const excelDownloadBtn = document.getElementById('excel-download-btn');

    // API 기본 URL 설정
    const API_BASE_URL = 'http://localhost:8000';

    // 로딩 상태 표시 함수
    function showLoading(show) {
        loadingSpinner.style.display = show ? 'block' : 'none';
        generateBtn.disabled = show;
    }

    // 에러 메시지 표시 함수
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    // 에러 메시지 초기화 함수
    function clearError() {
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }


    // 폰트 목록을 가져오는 함수
    async function loadSystemFonts() {
        try {
            console.log('폰트 목록 요청 시작');
            const response = await fetch(`${API_BASE_URL}/api/fonts`);
            console.log('폰트 목록 응답 받음:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('서버 응답 에러:', errorText);
                throw new Error(`폰트 목록을 가져오는데 실패했습니다. 상태 코드: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('받은 폰트 목록:', data);
            
            // 기존 옵션 제거
            fontSelect.innerHTML = '';
            
            // 폰트 목록 추가
            data.fonts.forEach(font => {
                const option = document.createElement('option');
                option.value = font.file_name;  // 파일 이름을 value로 사용
                
                // 한글 지원 여부에 따라 표시
                const koreanSupport = font.supports_korean ? '🇰🇷' : '';
                option.textContent = `${font.name} ${koreanSupport}`;
                
                // 한글 지원 여부를 데이터 속성으로 저장
                option.dataset.supportsKorean = font.supports_korean;
                
                fontSelect.appendChild(option);
            });
            
            console.log('폰트 목록 로딩 완료');
        } catch (error) {
            console.error('폰트 목록 로딩 실패:', error);
            showError(`폰트 목록을 가져오는데 실패했습니다: ${error.message}`);
        }
    }

    // 미리보기 업데이트 함수
    function updatePreview() {
        const backgroundColor = backgroundColorSelect.value;
        const colorFunc = colorFuncSelect.value;
        
        // 미리보기 스타일 업데이트
        const previewBox = document.getElementById('preview-box');
        if (previewBox) {
            previewBox.style.backgroundColor = backgroundColor;
            
            // 색상 함수에 따른 미리보기 텍스트 색상 설정
            let textColor;
            switch (colorFunc) {
                case 'single_color':
                    textColor = '#000000';
                    break;
                case 'random_color':
                    textColor = `hsl(${Math.random() * 360}, 70%, 50%)`;
                    break;
                case 'gradient_color':
                    previewBox.style.background = `linear-gradient(45deg, #ff0000, #00ff00)`;
                    textColor = '#ffffff';
                    break;
                default:
                    textColor = '#000000';
            }
            
            const previewText = previewBox.querySelector('.preview-text');
            if (previewText) {
                previewText.style.color = textColor;
            }
        }
    }

    // 워드클라우드 생성 이벤트 리스너
    generateBtn.addEventListener('click', async () => {
        console.log('Generate button clicked');
        const text = textInput.value.trim();
        
        if (!text) {
            showError('텍스트를 입력해주세요.');
            return;
        }
        
        try {
            clearError();
            showLoading(true);
            downloadBtn.style.display = 'none';
            excelDownloadBtn.style.display = 'none';
            
            const response = await fetch(`${API_BASE_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    font: fontSelect.value,
                    background_color: backgroundColorSelect.value,
                    color_func: colorFuncSelect.value,
                    mask_type: maskTypeSelect.value,
                    width: 800,
                    height: 400,
                    max_words: 200
                })
            });
            
            if (!response.ok) {
                throw new Error('워드클라우드 생성에 실패했습니다.');
            }
            
            // JSON 데이터 가져오기
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || '워드클라우드 생성에 실패했습니다.');
            }
            
            // 이미지 표시
            wordcloudImage.src = `data:image/png;base64,${data.data.image}`;
            wordcloudImage.style.display = 'block';
            
            // 다운로드 버튼 활성화
            downloadBtn.style.display = 'inline-block';
            if (data.data.words && data.data.words.length > 0) {
                excelDownloadBtn.style.display = 'inline-block';
            }
            
            // 단어 빈도수 테이블 업데이트
            updateWordFrequencyTable(data.data.words);
            
            // 엑셀 다운로드 버튼 이벤트 핸들러 설정
            excelDownloadBtn.addEventListener('click', async () => {
                try {
                    showLoading(true);
                    clearError();

                    // 현재 시간을 파일명에 포함
                    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                    
                    // 엑셀 파일 다운로드
                    const response = await fetch(`${API_BASE_URL}/api/download/${timestamp}`, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error('엑셀 파일 다운로드에 실패했습니다.');
                    }
                    
                    // Blob으로 변환
                    const blob = await response.blob();
                    
                    // 다운로드 링크 생성 및 클릭
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `wordcloud_frequency_${timestamp}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                } catch (error) {
                    console.error('엑셀 다운로드 실패:', error);
                    showError(`엑셀 다운로드 실패: ${error.message}`);
                } finally {
                    showLoading(false);
                }
            });
            
        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    });

    async function testB() {
        try{
            const response = await fetch(`${API_BASE_URL}/api/test`);
            console.log(typeof(response));
            console.log(response);
            const data = await response.json();
            console.log(data);
        } catch(err) {
            console.log(`에러 : ${err}`);
        }
        
    }

    // 다운로드 버튼 이벤트 리스너
    downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.download = 'wordcloud.png';
        link.href = wordcloudImage.src;
        link.click();
    });

    // 색상 및 스타일 변경 이벤트 리스너
    backgroundColorSelect.addEventListener('change', updatePreview);
    colorFuncSelect.addEventListener('change', updatePreview);

    let wordFrequencyData = [];

    function updateWordFrequencyTable(data) {
        wordFrequencyData = data;
        renderWordFrequencyTable();
    }

    function renderWordFrequencyTable() {
        const tbody = document.querySelector('#word-frequency-table tbody');
        const searchTerm = document.querySelector('#word-search').value.toLowerCase();
        const sortBy = document.querySelector('#sort-select').value;

        // 데이터 필터링 및 정렬
        let filteredData = wordFrequencyData.filter(item => 
            item.word.toLowerCase().includes(searchTerm)
        );

        // 정렬
        filteredData.sort((a, b) => {
            if (sortBy === 'frequency') {
                return b.frequency - a.frequency;
            } else {
                return a.word.localeCompare(b.word);
            }
        });

        // 테이블 업데이트
        tbody.innerHTML = '';
        filteredData.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.word}</td>
                <td>${item.frequency}회</td>
                <td>${item.percentage.toFixed(2)}%</td>
            `;
            tbody.appendChild(row);
        });
    }

    // 이벤트 리스너 추가
    document.querySelector('#word-search').addEventListener('input', renderWordFrequencyTable);
    document.querySelector('#sort-select').addEventListener('change', renderWordFrequencyTable);

    // 페이지 로드 시 초기화
    loadSystemFonts();
    updatePreview();
    showLoading(false);
    testB();
    downloadBtn.style.display = 'none';
    excelDownloadBtn.style.display = 'none';
});
