import { useState, useEffect } from 'react'
import {API_BASE_URL} from '.api/config';
function App() {
  const [posts, setPosts] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingData, setEditingData] = useState({})


  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/posts`)
      const data = await response.json()
      setPosts(data)
    } catch (error) {
      console.error('Error fetching posts:', error)
    }
  }

  const createPost = async (e) => {
    e.preventDefault()
    // console.log('🚀 Create 버튼 클릭됨')
    // console.log('📤 전송할 데이터:', { title, content })
    // console.log('📡 요청 URL:', `${API_BASE_URL}/posts`)
    
    try {
      const response = await fetch(`${API_BASE_URL}/posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, content }),
      })
      
      // console.log('📨 응답 상태:', response.status)
      // console.log('📨 응답 OK?:', response.ok)
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ 성공 응답:', result)
        setTitle('')
        setContent('')
        fetchPosts()
      } else {
        const errorText = await response.text()
        console.error('❌ 응답 에러:', response.status, errorText)
      }
    } catch (error) {
      console.error('❌ 네트워크 에러:', error)
    }
  }

  const updatePost = async (id, updatedTitle, updatedContent) => {
    try {
      const response = await fetch(`${API_BASE_URL}/posts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: updatedTitle, content: updatedContent }),
      })
      if (response.ok) {
        setPosts(posts.map(post => 
          post.id === id 
            ? { ...post, title: updatedTitle, content: updatedContent }
            : post
        ))
        setEditingId(null)
        setEditingData({})
      }
    } catch (error) {
      console.error('Error updating post:', error)
    }
  }

  const deletePost = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/posts/${id}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        setPosts(posts.filter(post => post.id !== id))
      }
    } catch (error) {
      console.error('Error deleting post:', error)
    }
  }

  const startEdit = (post) => {
    setEditingId(post.id)
    setEditingData({
      title: post.title,
      content: post.content
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditingData({})
  }

  const handleEditSubmit = (e, id) => {
    e.preventDefault()
    updatePost(id, editingData.title, editingData.content)
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'flex-start',
      padding: '20px',
      boxSizing: 'border-box'
    }}>
      <div style={{ 
        maxWidth: '800px', 
        width: '100%'
      }}>
      <h1>Post CRUD App</h1>
      
      <form onSubmit={createPost} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h3>새 포스트 작성</h3>
        <div style={{ marginBottom: '10px', marginRight: '15px' }}>
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginBottom: '10px'}}
          />
        </div>
        <div style={{ marginBottom: '10px', marginRight: '15px' }}>
          <textarea
            placeholder="Content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', minHeight: '100px' }}
          />
        </div>
        <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
          Create
        </button>
      </form>

      <h2>Posts</h2>
      <div>
        {posts.map((post) => (
          <div key={post.id} style={{ 
            marginBottom: '20px', 
            padding: '20px', 
            border: '1px solid #ddd', 
            borderRadius: '8px',
            backgroundColor: editingId === post.id ? '#f8f9fa' : 'white'
          }}>
            {editingId === post.id ? (
              <form onSubmit={(e) => handleEditSubmit(e, post.id)}>
                <div style={{ marginBottom: '10px' }}>
                  <input
                    type="text"
                    value={editingData.title}
                    onChange={(e) => setEditingData({...editingData, title: e.target.value})}
                    required
                    style={{ width: '100%', padding: '8px', fontSize: '18px', fontWeight: 'bold' }}
                  />
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <textarea
                    value={editingData.content}
                    onChange={(e) => setEditingData({...editingData, content: e.target.value})}
                    required
                    style={{ width: '100%', padding: '8px', minHeight: '100px' }}
                  />
                </div>
                <div>
                  <button type="submit" style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#28a745', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px',
                    marginRight: '10px'
                  }}>
                    저장
                  </button>
                  <button type="button" onClick={cancelEdit} style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#6c757d', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px'
                  }}>
                    취소
                  </button>
                </div>
              </form>
            ) : (
              <>
                <h3 style={{ margin: '0 0 10px 0' }}>{post.title}</h3>
                <p style={{ margin: '0 0 15px 0', lineHeight: '1.5' }}>{post.content}</p>
                <div>
                  <button onClick={() => startEdit(post)} style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#007bff', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px',
                    marginRight: '10px'
                  }}>
                    수정
                  </button>
                  <button onClick={() => deletePost(post.id)} style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#dc3545', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px'
                  }}>
                    삭제
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
      </div>
    </div>
  )
}

export default App