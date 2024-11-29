document.addEventListener('DOMContentLoaded', async () => {
    const textInput = document.getElementById('textInput');  // ID 수정
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
    const uploadButton = document.getElementById('uploadButton');
    const textFileInput = document.getElementById('textFileInput');

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

    let currentFileId = null;  // 현재 선택된 파일의 ID

    // 파일 목록 업데이트 함수
    async function updateFileList() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/uploaded-files`);
            const result = await response.json();
            
            const fileListElement = document.getElementById('uploadedFiles');
            fileListElement.innerHTML = '';
            
            if (result.data && result.data.length > 0) {
                result.data.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                    fileItem.innerHTML = `
                        <span class="file-name">${file.filename}</span>
                        <button class="btn btn-sm btn-danger delete-file" data-file-id="${file.file_id}">
                            삭제
                        </button>
                    `;
                    fileListElement.appendChild(fileItem);

                    // 삭제 버튼에 이벤트 리스너 추가
                    const deleteButton = fileItem.querySelector('.delete-file');
                    deleteButton.addEventListener('click', () => {
                        if (confirm('정말 이 파일을 삭제하시겠습니까?')) {
                            handleDeleteFile(file.file_id);
                        }
                    });
                });
            } else {
                const emptyMessage = document.createElement('div');
                emptyMessage.className = 'list-group-item text-muted';
                emptyMessage.textContent = '업로드된 파일이 없습니다.';
                fileListElement.appendChild(emptyMessage);
            }
        } catch (error) {
            console.error('파일 목록 업데이트 중 오류:', error);
        }
    }

    // 파일 삭제 처리
    async function handleDeleteFile(fileId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/delete-file/${fileId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            // 파일 목록 업데이트
            await updateFileList();
        } catch (error) {
            console.error('파일 삭제 중 오류:', error);
            showError('파일 삭제 중 오류가 발생했습니다.');
        }
    }

    // 파일 선택 시 자동 업로드
    textFileInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        for (const file of files) {
            await handleFileUpload(file);
        }
        textFileInput.value = ''; // 파일 입력 초기화
    });

    // 워드클라우드 생성 버튼 클릭 이벤트
    async function generateWordCloud() {
        showLoading(true);
        try {
            const textInput = document.getElementById('textInput').value;
            let content = textInput;

            // 텍스트 입력이 없는 경우 업로드된 파일들의 내용을 사용
            if (!textInput.trim()) {
                const response = await fetch(`${API_BASE_URL}/api/all-files-content`);
                const result = await response.json();
                
                if (result.status === 'error') {
                    throw new Error(result.message);
                }
                
                if (!result.data.content) {
                    throw new Error('처리할 텍스트가 없습니다. 파일을 업로드하거나 텍스트를 입력해주세요.');
                }
                
                content = result.data.content;
            }

            const backgroundColor = document.getElementById('background-color').value;
            const fontFamily = document.getElementById('fontSelect').value;
            const maskType = document.getElementById('mask-type').value;
            const colorFunc = document.getElementById('color-func').value;

            const response = await fetch(`${API_BASE_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: content,
                    background_color: backgroundColor,
                    font: fontFamily,
                    mask_type: maskType,
                    color_func: colorFunc
                }),
            });

            const result = await response.json();
            
            if (result.success) {
                updateWordCloud(result.data);
                clearError();
            } else {
                showError(result.message || '워드클라우드 생성 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('워드클라우드 생성 중 오류가 발생했습니다.');
        } finally {
            showLoading(false);
        }
    }

    generateBtn.addEventListener('click', generateWordCloud);

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

    function updateWordCloud(data) {
        // 이미지 표시
        const wordcloudImage = document.getElementById('wordcloud-image');
        wordcloudImage.src = `data:image/png;base64,${data.image}`;
        wordcloudImage.style.display = 'block';
        
        // 다운로드 버튼 활성화
        const downloadBtn = document.getElementById('download-btn');
        downloadBtn.style.display = 'inline-block';
        if (data.words && data.words.length > 0) {
            const excelDownloadBtn = document.getElementById('excel-download-btn');
            excelDownloadBtn.style.display = 'inline-block';
        }
        
        // 단어 빈도수 테이블 업데이트
        if (data.words) {
            updateWordFrequencyTable(data.words);  // 단어 빈도수 데이터 업데이트
        }
    }

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

    // 초기 파일 목록 로드
    updateFileList();

    // 페이지 로드 시 초기화
    loadSystemFonts();
    updatePreview();
    showLoading(false);
    downloadBtn.style.display = 'none';
    excelDownloadBtn.style.display = 'none';

    // 파일 업로드 처리
    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/api/upload-file`, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            await updateFileList();
        } catch (error) {
            console.error('파일 업로드 중 오류:', error);
            showError('파일 업로드 중 오류가 발생했습니다.');
        }
    }
});
