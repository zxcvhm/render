import { useState } from 'react';

function SignUpPage() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        // form 태그를 전송할 때 새로고침 방지 
        e.preventDefault()
        // fastapi 서버에 로그인 기능 요청 
        // form 태그에서 입력 받은 값을 body에 넣어 http 요청 (post)
        try{
            const response = await fetch('http://localhost:8000/users', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({name, email, password}),

            });
            const data = await response.json()
            console.log("Signup response",data)
        }catch (error){
            console.log('Signup error', error)
        }
    }    

    return (
        <div>
            <h3>Signup</h3>
            {/* 버튼을 눌렀을 때 어디로 요청을 보낼 것인가를 처리하는 함수 */}
            <form onSubmit={handleSubmit}> 
                {/* 이름 */}
                <div>
                    <label>Name: </label>
                    <input type="text" 
                    value={name}
                    onChange={(e)=> setName(e.target.value)}
                    />
                </div>
                {/* 이메일 */}
                <div>
                    <label>Email: </label>
                    <input type="email" 
                    value={email}
                    onChange={(e)=> setEmail(e.target.value)}
                    />
                </div>
                {/* 비밀번호 */}
                <div>
                    <label>Password: </label>
                    <input type="password" 
                    value={password}
                    onChange={(e)=> setPassword(e.target.value)}
                    />
                </div>
                <button type='submit'>Signup</button>
            </form>
        </div>
    )
}

export default SignUpPage;
