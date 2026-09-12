import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../lib/api'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    full_name: '',
    password: '',
    mode: 'personal',
  })
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/auth/register', form)
      toast.success('Akun berhasil dibuat! Silakan login.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registrasi gagal')
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
          <h2 className="text-xl font-semibold mb-5">Buat Akun</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Nama Lengkap</label>
              <input
                type="text"
                className="input"
                placeholder="Nama kamu"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
              />
            </div>
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
                placeholder="Min. 6 karakter"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="label">Tipe Pengguna</label>
              <select
                className="input"
                value={form.mode}
                onChange={(e) => setForm({ ...form, mode: e.target.value })}
              >
                <option value="personal">Pribadi / Mahasiswa</option>
                <option value="umkm">Pemilik UMKM</option>
              </select>
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Memproses…' : 'Daftar'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Sudah punya akun?{' '}
            <Link to="/login" className="text-brand-600 hover:underline font-medium">
              Masuk
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
