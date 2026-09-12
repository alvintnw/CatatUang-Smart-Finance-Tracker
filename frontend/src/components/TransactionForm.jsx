import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

const today = () => new Date().toISOString().split('T')[0]

export default function TransactionForm({ onSuccess, editTx = null, onCancel }) {
  const { user } = useAuth()
  const isUmkm = user?.mode === 'umkm'
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    amount: '',
    type: 'expense',
    description: '',
    date: today(),
    category_id: '',
    customer_name: '',
    payment_method: '',
  })

  useEffect(() => {
    api.get('/categories').then(({ data }) => setCategories(data))
  }, [])

  useEffect(() => {
    if (editTx) {
      setForm({
        amount: editTx.amount,
        type: editTx.type,
        description: editTx.description,
        date: editTx.date,
        category_id: editTx.category?.id || '',
        customer_name: editTx.customer_name || '',
        payment_method: editTx.payment_method || '',
      })
    }
  }, [editTx])

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = {
        amount: Number(form.amount),
        type: form.type,
        description: form.description,
        date: form.date,
        category_id: form.category_id ? Number(form.category_id) : null,
        customer_name: form.customer_name || null,
        payment_method: form.payment_method || null,
      }
      if (editTx) {
        await api.put(`/transactions/${editTx.id}`, payload)
        toast.success('Transaksi diperbarui')
      } else {
        await api.post('/transactions', payload)
        toast.success('Transaksi dicatat!')
      }
      onSuccess?.()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Gagal menyimpan transaksi')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Type toggle */}
      <div className="flex rounded-lg overflow-hidden border border-gray-300">
        {['expense', 'income'].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setForm({ ...form, type: t })}
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              form.type === t
                ? t === 'expense'
                  ? 'bg-red-500 text-white'
                  : 'bg-green-500 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            {t === 'expense' ? '📤 Pengeluaran' : '📥 Pemasukan'}
          </button>
        ))}
      </div>

      {/* Amount */}
      <div>
        <label className="label">Nominal (Rp)</label>
        <input
          type="number"
          className="input"
          placeholder="0"
          value={form.amount}
          onChange={set('amount')}
          required
          min={1}
        />
      </div>

      {/* Description */}
      <div>
        <label className="label">Deskripsi</label>
        <input
          type="text"
          className="input"
          placeholder='Contoh: "beli kopi starbucks 45rb" atau "bayar listrik"'
          value={form.description}
          onChange={set('description')}
          required
        />
        <p className="text-xs text-gray-400 mt-1">
          Kategori akan terisi otomatis dari deskripsi.
        </p>
      </div>

      {/* Date */}
      <div>
        <label className="label">Tanggal</label>
        <input
          type="date"
          className="input"
          value={form.date}
          onChange={set('date')}
          required
        />
      </div>

      {/* Category override */}
      <div>
        <label className="label">Kategori (opsional — override otomatis)</label>
        <select className="input" value={form.category_id} onChange={set('category_id')}>
          <option value="">— Otomatis dari deskripsi —</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* UMKM fields */}
      {isUmkm && (
        <>
          <div>
            <label className="label">Pelanggan / Supplier (opsional)</label>
            <input
              type="text"
              className="input"
              placeholder="Nama pelanggan atau supplier"
              value={form.customer_name}
              onChange={set('customer_name')}
            />
          </div>
          <div>
            <label className="label">Metode Pembayaran (opsional)</label>
            <select className="input" value={form.payment_method} onChange={set('payment_method')}>
              <option value="">— Pilih —</option>
              <option value="tunai">Tunai</option>
              <option value="qris">QRIS</option>
              <option value="transfer">Transfer</option>
            </select>
          </div>
        </>
      )}

      <div className="flex gap-2 pt-2">
        <button type="submit" className="btn-primary flex-1" disabled={loading}>
          {loading ? 'Menyimpan…' : editTx ? 'Simpan Perubahan' : 'Catat Transaksi'}
        </button>
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Batal
          </button>
        )}
      </div>
    </form>
  )
}
