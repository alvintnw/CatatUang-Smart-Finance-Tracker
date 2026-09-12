import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { formatRupiah, currentMonthYear, MONTHS_ID } from '../lib/utils'

export default function BudgetsPage() {
  const { month: curMonth, year: curYear } = currentMonthYear()
  const [month, setMonth] = useState(curMonth)
  const [year, setYear] = useState(curYear)
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ category_id: '', limit_amount: '', month: curMonth, year: curYear })
  const [submitting, setSubmitting] = useState(false)

  const fetchBudgets = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/budgets', { params: { month, year } })
      setBudgets(data)
    } catch {
      toast.error('Gagal memuat anggaran')
    } finally {
      setLoading(false)
    }
  }, [month, year])

  useEffect(() => { fetchBudgets() }, [fetchBudgets])
  useEffect(() => {
    api.get('/categories').then(({ data }) => setCategories(data))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/budgets', {
        category_id: Number(form.category_id),
        limit_amount: Number(form.limit_amount),
        month,
        year,
      })
      toast.success('Anggaran ditambahkan')
      setShowForm(false)
      fetchBudgets()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Gagal menyimpan anggaran')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Hapus anggaran ini?')) return
    try {
      await api.delete(`/budgets/${id}`)
      toast.success('Anggaran dihapus')
      fetchBudgets()
    } catch {
      toast.error('Gagal menghapus')
    }
  }

  const statusColor = {
    aman: 'bg-green-500',
    mendekati: 'bg-yellow-400',
    melewati: 'bg-red-500',
  }
  const statusLabel = {
    aman: '✅ Aman',
    mendekati: '⚠️ Mendekati',
    melewati: '🚨 Melewati',
  }

  return (
    <div className="pb-20 md:pb-0">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-gray-800">Anggaran</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Tambah
        </button>
      </div>

      {/* Month selector */}
      <div className="flex gap-2 mb-4">
        <select className="input w-auto" value={month} onChange={(e) => setMonth(Number(e.target.value))}>
          {MONTHS_ID.slice(1).map((m, i) => (
            <option key={i + 1} value={i + 1}>{m}</option>
          ))}
        </select>
        <select className="input w-auto" value={year} onChange={(e) => setYear(Number(e.target.value))}>
          {[curYear - 1, curYear, curYear + 1].map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {/* Add form */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-sm p-5 shadow-xl">
            <h2 className="text-lg font-semibold mb-4">Tambah Anggaran</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Kategori</label>
                <select
                  className="input"
                  value={form.category_id}
                  onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                  required
                >
                  <option value="">— Pilih kategori —</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Batas Anggaran (Rp)</label>
                <input
                  type="number"
                  className="input"
                  placeholder="0"
                  value={form.limit_amount}
                  onChange={(e) => setForm({ ...form, limit_amount: e.target.value })}
                  required
                  min={1}
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn-primary flex-1" disabled={submitting}>
                  {submitting ? 'Menyimpan…' : 'Simpan'}
                </button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                  Batal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-gray-400">Memuat…</div>
      ) : budgets.length === 0 ? (
        <div className="text-center py-10 text-gray-400">
          <p className="text-4xl mb-2">🎯</p>
          <p>Belum ada anggaran untuk bulan ini</p>
        </div>
      ) : (
        <div className="space-y-3">
          {budgets.map((b) => (
            <div key={b.id} className="card">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="font-semibold text-gray-800">{b.category.name}</p>
                  <p className="text-xs text-gray-400">
                    {formatRupiah(b.spent)} / {formatRupiah(b.limit_amount)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full text-white ${
                    b.status === 'aman' ? 'bg-green-500' :
                    b.status === 'mendekati' ? 'bg-yellow-400' : 'bg-red-500'
                  }`}>
                    {statusLabel[b.status]}
                  </span>
                  <button
                    onClick={() => handleDelete(b.id)}
                    className="text-gray-300 hover:text-red-400 transition-colors"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              {/* Progress bar */}
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${statusColor[b.status]}`}
                  style={{ width: `${Math.min(b.percentage, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1 text-right">{b.percentage}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
