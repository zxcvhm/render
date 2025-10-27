from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import os
import uuid
from models import PostImage
from PIL import Image # 이미지를 읽어와서 이미지 처리를 하게 도와주는 클래스
import io # 입출력 처리를 도와주는 모듈
import cv2
import numpy as np

router = APIRouter(prefix = '/post', tags=['포스트'])

# 파일을 DB에 저장할 때는 파일 경로를 저장 
# 실제 파일은 서버의 파일 시스템 또는 클라우드 파일 시스템에 저장

# 왜 따로 저장하나요? 

# 파일 저장 경로 설정
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True) # exist_ok: 이미 폴더가 있으면 오류를 내지 않음

# 처리 시간이 길것으로 예상되고 일정하지 않는 처리 시간 일 때 -> 비동기 처리 함수
@router.post('/upload/image')
async def upload_image(file: UploadFile = File(...),  # ... -> 필수값
                       db: Session=Depends(get_db)):
    
    # 1. 파일 형식 검증 (MIME 타입 체크) -> 메타 데이터를 확인하여 진짜 이미지 인가 확인
    if not file.content_type.startswith('image/'): # 이미지 파일 
        print(type(file.content_type))
        raise HTTPException(status_code=400, detail='이미지 파일만 업로드 가능')
    
    # 2. 파일 내용 읽기
    # 고정된 시간의 읽기 불가능 하기 때문에 읽기 처리는 비동기로 한다
    file_content = await file.read() 
    
    # 3. 파일 크기 검증 
    max_size = 5 * 1024 * 1024 # -> 5MB  1000Byte -> 1KB 1000KB -> 1MB
    
    if len(file_content) > max_size: # Byte 길이로 읽음  
        raise HTTPException(status_code=400, detail="파일 크기는 5MB 이하여야 합니다.")
    
    # 4. 이미지 정보 확인 및 필터링 (원하는 이미지 필터링 하기 위해서)
    # 파일 넓이, 높이가 어떤지, rgb 값은 뭘 가지고 있는지 파일이 흑백, 컬러
    try: 
        image = Image.open(io.BytesIO(file_content)) # 파일 경로, 파일 객체
        width, height= image.size
        mode = image.mode #  RGB, RGA, L(흑백 이미지)
        extrema = image.getextrema()  # 최소, 최대 픽셀값을 리턴 / R, G, B 
        
        # 사이즈가 너무작으면 받지 않도록  (100px x 100px)
        is_valid_size = width >= 100 and height >= 100  
        if not is_valid_size: 
            raise HTTPException(status_code=400, detail='가로 세로 길이가 모두 100px 이상이어야 합니다.')
        
        # 흑백 이미지면 받지 않도록 
        if mode == 'L':
            raise HTTPException(status_code=400, detail='컬러 이미지여야 합니다.')

        # if len(extrema) == 3: 
        #     if extrema[0] == extrema[1] == extrema[2]:
        #         # RGB 이미지 인데 흑백인 경우를 필터링 
        #         raise HTTPException(status_code=400, detail='컬러 이미지여야 합니다.')
    
        # AI 사람 필터링 
        
        # 바이트 데이터를 opencv를 활용하여 연산하기 위해 numpy 형식으로 바꿔야 함 
        # AI 입력값이 벡터 
        nparray = np.frombuffer(file_content, np.uint8) # 타입은 동일하게 지정  0 ~ 255
        # 배열 -> opencv 이미지 
        image = cv2.imdecode(nparray, cv2.IMREAD_COLOR) # opencv 컬러 이미지로 변환
        # 얼굴 인식 할 때 조금 더 잘 감지하기 위해서 흑백 이미지로 변환 
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # RGB -> Grayscale / BGR
        
        # 얼굴 인식 모델 불러오기 
        face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # 얼굴 인식 모델로 얼굴 감지하기 
        faces = face_detection.detectMultiScale(gray_image, 1.1, 10) # 이미지 벡터 데이터, 감지 방식에 대한 속성값 
        
        # 얼굴 인식 결과를 보고 사람이 있으면 아래 저장 진행 / 아니면 에러를 내도록 
        faces_count = len(faces)
        if faces_count == 0:
            raise HTTPException(status_code=400, detail='사람이 포함된 이미지여야 합니다.')
        print(faces) 
        print(type(faces))
        
        # 5. 고유한 파일 이름 생성 (파일 덮어쓰기 방지 및 중복제거)
        # 확장자 가져오기 
        file_extension = file.filename.split('.')[-1] # xxxx.png xxx.jpg
        # 고유한 값 
        unique_filename = f"{uuid.uuid4()}.{file_extension}" 
        # 실제 저장될 파일 경로 
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 6. 파일 저장 
        # 6-1. 파일시스템에 저장 
        with open(file_path, 'wb') as f: # 파일 경로, 모드, encoding 방식 
            f.write(file_content)
            
        # 6-2. DB에 저장 
        post_image = PostImage(
            file_path = file_path,
            stored_filename = unique_filename, 
            original_filename = file.filename,
            file_size = len(file_content)
        )
        db.add(post_image)
        db.commit()
        db.refresh(post_image)
        
        # 응답
        return {
            "message": "이미지가 업로드 되었습니다",
            "result": post_image
        }
        
    except HTTPException: 
        raise 
    except Exception as e:
        print(f"예상치 못한 에러: {e}")    
