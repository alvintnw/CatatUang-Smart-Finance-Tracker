import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import TransactionForm from '../components/TransactionForm'
import CategoryCorrectModal from '../components/CategoryCorrectModal'
import { formatRupiah, formatDate, currentMonthYear, MONTHS_ID } from '../lib/utils'

export default function TransactionsPage() {
  const { month: curMonth, year: curYear } = currentMonthYear()
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editTx, setEditTx] = useState(null)
  const [correctTx, setCorrectTx] = useState(null)
  const [filters, setFilters] = useState({ month: curMonth, year: curYear, type: '' })

  const fetchTransactions = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.month) params.month = filters.month
      if (filters.year) params.year = filters.year
      if (filters.type) params.type = filters.type
      const { data } = await api.get('/transactions', { params })
      setTransactions(data)
    } catch {
      toast.error('Gagal memuat transaksi')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetchTransactions() }, [fetchTransactions])

  async function handleDelete(id) {
    if (!confirm('Hapus transaksi ini?')) return
    try {
      await api.delete(`/transactions/${id}`)
      toast.success('Transaksi dihapus')
      fetchTransactions()
    } catch {
      toast.error('Gagal menghapus')
    }
  }

  return (
    <div className="pb-20 md:pb-0">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-gray-800">Transaksi</h1>
        <button
          className="btn-primary"
          onClick={() => { setEditTx(null); setShowForm(true) }}
        >
          + Catat
        </button>
      </div>

      {/* Form modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-md max-h-[90vh] overflow-y-auto p-5 shadow-xl">
            <h2 className="text-lg font-semibold mb-4">
              {editTx ? 'Edit Transaksi' : 'Catat Transaksi Baru'}
            </h2>
            <TransactionForm
              editTx={editTx}
              onSuccess={() => { setShowForm(false); fetchTransactions() }}
              onCancel={() => setShowForm(false)}
            />
          </div>
        </div>
      )}

      {/* Correct category modal */}
      {correctTx && (
        <CategoryCorrectModal
          transaction={correctTx}
          onClose={() => setCorrectTx(null)}
          onSuccess={() => { setCorrectTx(null); fetchTransactions() }}
        />
      )}

      {/* Filters */}
      <div className="card mb-4">
        <div className="flex flex-wrap gap-3">
          <select
            className="input w-auto"
            value={filters.month}
            onChange={(e) => setFilters({ ...filters, month: Number(e.target.value) })}
          >
            {MONTHS_ID.slice(1).map((m, i) => (
              <option key={i + 1} value={i + 1}>{m}</option>
            ))}
          </select>
          <select
            className="input w-auto"
            value={filters.year}
            onChange={(e) => setFilters({ ...filters, year: Number(e.target.value) })}
          >
            {[curYear - 1, curYear, curYear + 1].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select
            className="input w-auto"
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          >
            <option value="">Semua tipe</option>
            <option value="expense">Pengeluaran</option>
            <option value="income">Pemasukan</option>
          </select>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="text-center py-10 text-gray-400">Memuat…</div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-10 text-gray-400">
          <p className="text-4xl mb-2">📭</p>
          <p>Belum ada transaksi</p>
        </div>
      ) : (
        <div className="space-y-2">
          {transactions.map((tx) => (
            <div key={tx.id} className="card flex items-center gap-3">
              {/* Type indicator */}
              <span className={`text-2xl ${tx.type === 'income' ? 'text-green-500' : 'text-red-400'}`}>
                {tx.type === 'income' ? '📥' : '📤'}
              </span>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{tx.description}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-gray-400">{formatDate(tx.date)}</span>
                  {tx.category && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                      {tx.category.name}
                      {tx.corrected_by_user && ' ✓'}
                    </span>
                  )}
                </div>
              </div>

              {/* Amount */}
              <span className={`font-semibold text-sm ${tx.type === 'income' ? 'text-green-600' : 'text-red-500'}`}>
                {tx.type === 'income' ? '+' : '-'}{formatRupiah(tx.amount)}
              </span>

              {/* Actions */}
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => setCorrectTx(tx)}
                  title="Koreksi kategori"
                  className="text-gray-400 hover:text-blue-500 p-1 transition-colors"
                >
                  🏷️
                </button>
                <button
                  onClick={() => { setEditTx(tx); setShowForm(true) }}
                  title="Edit"
                  className="text-gray-400 hover:text-blue-500 p-1 transition-colors"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(tx.id)}
                  title="Hapus"
                  className="text-gray-400 hover:text-red-500 p-1 transition-colors"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
