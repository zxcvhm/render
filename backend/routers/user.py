from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    HTTPException,\
                    Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
import uuid
from datetime import datetime

router = APIRouter(prefix='/users')

# 임시 데이터 저장 (나중에 DB로 대체)
fake_users = {
    'admin': '1234',
    'jh': '1234'
}

# -> 사용자 이름, 아이디, 패스워드, 세션아이디, 로그인 시간, 만료시간
sessions = {} 

@router.post('/login')
def login(response: Response, 
          username: str, 
          password: str):
    # 1. db에서 사용자가 일치하는지 확인
    if username not in fake_users or fake_users[username] != password:
        # 아이디가 없거나 패스워드가 일치하지 않거나 
        raise HTTPException(status_code=401, detail="잘못된 사용자명 또는 비밀번호") # 401: 인증되지 않은 리소스
    
    # 2. 쿠키 설정 (로그인 성공했을 때)
    html_contents = "로그인 성공! <a href='/profile'>프로필 이동</a>"
    response = Response(html_contents, media_type='text/html')  # html 응답 
    response.set_cookie(
        key="user_id",
        value=username, 
        max_age=20,
        httponly=True,     # javascript에서 접근할 수 없도록 
        secure=False,      # https 요청만 쿠키 저장 (운영서버를 할때 True 사용)
        samesite='strict'  # 같은 도메인에서만 쿠키 저장, 가져오기 허용 
                           # lax: GET 요청일 때 쿠키 접근 가능     
                           # None: 모든 상황에서 가능 (외부 서비스를 이용할 때)
    )
    
    # 3. 일치하면 로그인 성공 메시지 또는 response 객체 
    return response 

@router.get('/profile', response_class=HTMLResponse)
def get_profile(request: Request):
    """로그인된 사용자만 접근 할 수 있는 프로필 페이지를 리턴"""
    
    # 1. request 객체에서 쿠키 정보 가지고 옴
    user_id=request.cookies.get('user_id') # user_id 키 값으로 user정보 가져오기 
    
    # 2. 쿠키 정보에 user_id가 있으면 로그인된 사용자 표시 
    if not user_id:
        # 2-1. 로그인이 필요하다 
        return """
        <html>
            <body>
                <h3>로그인이 필요합니다</h3>
                <a href="/">로그인 페이지로 이동</a>
            </body>
        </html>
        """
    # 2-2. 있으면 프로필 페이지 리턴 
    return f"""
            <html>
                <body>
                    <h1>안녕하세요, {user_id}님</h1>
                    <a href='/'>홈으로</a>
                    <a href='/users/logout'>로그아웃</a>
                </body>
            </html>
            """
            
@router.get('/session_profile', response_class=HTMLResponse)
def get_profile(request: Request):
    """로그인된 사용자만 접근 할 수 있는 프로필 페이지를 리턴"""
    
    # 1. request 객체에서 쿠키에 있는 session_id 가져옴 
    session_id = request.cookies.get('session_id', 'session_id')
    
    # 2. 쿠키 정보에 session_id가 있으면 로그인된 사용자 표시 
    if not session_id:
        # 2-1. 로그인이 필요하다 
        return """
        <html>
            <body>
                <h3>로그인이 필요합니다</h3>
                <a href="/">로그인 페이지로 이동</a>
            </body>
        </html>
        """
    
    # 데이터 베이스나 메모리에 있는 세션 id와 일치하는지 확인하고 
    # 사용자 정보 가져와서 표시  
    session_data = sessions.get(session_id) # username, login_time    
    
    # 만료되었는지 확인
    if not session_data: # 서버에서 세션 정보가 사라졌을 때 
        return """
        <html>
            <body>
                <h1>유효하지 않은 세션입니다.</h1>
            </body>
        </html>
        """
        
    # 2-2. 있으면 프로필 페이지 리턴 
    return f"""
            <html>
                <body>
                    <h1>안녕하세요, {session_data['username']}님</h1>
                    <h3>로그인 시간: {session_data['login_time']}</h3>
                    <a href='/'>홈으로</a>
                    <a href='/users/logout'>로그아웃</a>
                </body>
            </html>
            """            

           
@router.get('/logout', response_class=HTMLResponse)
def logout(response: Response):
    
    html_content = "로그 아웃! <a href='/'>홈으로</a>"
    response = Response(html_content, media_type='text/html')
    response.delete_cookie('user_id')

    return response

@router.post('/session_login', response_class=HTMLResponse)
def session_login(response: Response, 
                  username: str = Form(...),
                  password: str = Form(...)):
    # 1. 데이터 베이스 또는 메모리에 있는 사용자 정보를 확인 (인증)
    if username not in fake_users or fake_users[username] !=password:
        raise HTTPException(status_code=401, 
                            detail='등록되지 않은 사용자 또는 틀린 비밀번호 입니다')
    
    # 2. 인증에 성공하면 세션 ID 발급 
    session_id = str(uuid.uuid4()) # 바이너리 -> 문자열 
    
    # 3. 세션 ID를 데이터 베이스 또는 메모리에 저장 
    sessions[session_id] = {
        'username': username, 
        'login_time': datetime.now()
    }
    
    # 4. 세션 ID를 클라이언트에게 전송 (쿠키로 저장해서 전송)
    response = Response("로그인 성공! <a href='/users/session_profile'>프로필</a>", media_type='text/html')
    response.set_cookie(
        key='session_id',
        value=session_id,
        max_age=30*60,
        httponly=True,
        secure=False,
        samesite='strict'
    )
    
    return response



@router.post('')
def create_user(users: dict, 
                db: Session=Depends(get_db)):
    
    user = User(name = users['name'],
                email = users['email'],
                password = users['password'])
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user