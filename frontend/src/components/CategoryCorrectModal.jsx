import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'

export default function CategoryCorrectModal({ transaction, onClose, onSuccess }) {
  const [categories, setCategories] = useState([])
  const [selectedId, setSelectedId] = useState(transaction.category?.id || '')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/categories').then(({ data }) => setCategories(data))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!selectedId) return
    setLoading(true)
    try {
      await api.post(`/transactions/${transaction.id}/correct-category`, {
        transaction_id: transaction.id,
        corrected_category_id: Number(selectedId),
      })
      toast.success('Kategori diperbarui dan disimpan sebagai data latih')
      onSuccess()
    } catch {
      toast.error('Gagal memperbarui kategori')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-sm p-5 shadow-xl">
        <h2 className="text-lg font-semibold mb-1">Koreksi Kategori</h2>
        <p className="text-sm text-gray-500 mb-4 truncate">"{transaction.description}"</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Kategori yang benar</label>
            <select
              className="input"
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              required
            >
              <option value="">— Pilih kategori —</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <p className="text-xs text-blue-600 bg-blue-50 rounded p-2">
            💡 Koreksi ini disimpan sebagai data latih untuk meningkatkan akurasi kategorisasi otomatis.
          </p>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1" disabled={loading}>
              {loading ? 'Menyimpan…' : 'Simpan'}
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Batal
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
