import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('username', form.email)
      params.append('password', form.password)
      const { data } = await api.post('/auth/login', params)
      login(
        { id: data.user_id, email: data.email, full_name: data.full_name, mode: data.mode },
        data.access_token
      )
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login gagal')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 to-blue-100 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brand-700">💰 CatatUang</h1>
          <p className="text-gray-500 mt-1 text-sm">Catat keuangan, raih tujuan</p>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold mb-5">Masuk</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                className="input"
                placeholder="email@kamu.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Memproses…' : 'Masuk'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Belum punya akun?{' '}
            <Link to="/register" className="text-brand-600 hover:underline font-medium">
              Daftar sekarang
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
