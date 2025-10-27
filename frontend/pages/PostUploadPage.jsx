import {useState} from 'react';

// 함수 

function PostUploadPage(){
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null); 

    const handleFileChange = (e) => {
        // 파일을 저장하고 있기 
        setFile(e.target.files[0]);
        setResult(null); // 새로운 결과를 받기 위해 초기화 

    }

    const handleUpload = async () => {
        // 파일을 전송하기 

        // 1. 파일이 있는지 확인 
        if (!file){
            setError('파일을 선택하세요!');
            return;
        }
        // 파일 업로드 시작 
        try{
            setLoading(true);  // 업로드 시작 loading 변수에 true
            setError(null); // 업로드 시작할 때 에러 초기화 

            // 2. 파일을 body에 담을 수 있게 준비하기 
            const formData = new FormData();

            // 첫번째 인자: file fastapi 서버에서 전달 받는 키값 -> 매개변수 이름
            // 두번째 인자: 실제 파일 
            formData.append('file', file);
            
            // 3. fetch 함수로 fastapi 서버에 파일 전송하기
            const response = await fetch('http://127.0.0.1:8000/post/upload/image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // response 변수에 결과가 없으면 에러를 내도록 
            // 서버에서 보낸 에러 메시지를 사용하는데 
            // 서버 에러가 없으면 뒤에 있는 메시지 전달
            if (!response.ok){
                throw new Error(data.detail || '업로드 실패');
            }
            setResult(data);
            setError(null); // 성공했으니 새로운 에러를 담을 준비 
        }catch (error) {
            setError(error.message); // 에러 메시지 설정 
            setResult(null); // 에러가 났을 때 새로운 결과를 받을 준비 
        }finally{
            setLoading(false); // 업로드 완료 (성공, 실패 상관없음)
        }
    }
    
    return (
        <div>
            <h3>파일 업로드</h3>
            <input type="file" 
            accept="image/*"
            onChange={handleFileChange}
            disabled={loading}
            />
            <button onClick={handleUpload} disabled={loading}>
                {/* 삼항 연산자 ? | 물음표 앞에 있는 변수가 true 앞 false 뒤 */}
                {loading ? "업로드 중..": "업로드"}  
            </button>

            {loading && (
                <p>업로드 중....</p>
            )}

            {error && (
                <div>
                    <p>업로드에 실패하였습니다.</p> <br></br>
                    <p>{error}</p>
                </div>
            )}

            {result && (
                <div>
                    <h5>{result.message}</h5>
                    <ul>
                        <li>저장된 파일명: {result.result.stored_filename}</li>
                        <li>원본 파일명: {result.result.original_filename}</li>
                        <li>크기: {result.result.file_size}</li>
                    </ul>
                    <img src={`http://127.0.0.1:8000/uploads/${result.result.stored_filename}`} alt="업로드한 이미지" style={{width: "300px"}}/>
                </div>
            )}

            
        </div>
    )
}

export default PostUploadPage;

