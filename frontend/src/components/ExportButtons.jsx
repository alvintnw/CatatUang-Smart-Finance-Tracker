import toast from 'react-hot-toast'
import api from '../lib/api'

export default function ExportButtons({ month, year }) {
  async function handleExport(format) {
    try {
      const params = new URLSearchParams({ month, year })
      const url = `/api/export/${format}?${params}`
      // Trigger browser download
      const link = document.createElement('a')
      link.href = url
      // Auth header handled by token in request — use fetch approach
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      })
      if (!response.ok) throw new Error()
      const blob = await response.blob()
      const objectUrl = URL.createObjectURL(blob)
      link.href = objectUrl
      link.download = `transaksi_${month}_${year}.${format === 'excel' ? 'xlsx' : 'csv'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(objectUrl)
    } catch {
      toast.error('Gagal mengekspor data')
    }
  }

  return (
    <div className="card">
      <h2 className="font-semibold text-gray-700 mb-3">📥 Ekspor Data</h2>
      <p className="text-sm text-gray-500 mb-3">
        Unduh riwayat transaksi bulan ini sebagai file laporan.
      </p>
      <div className="flex gap-2">
        <button
          onClick={() => handleExport('csv')}
          className="btn-secondary flex-1"
        >
          📄 CSV
        </button>
        <button
          onClick={() => handleExport('excel')}
          className="btn-secondary flex-1"
        >
          📊 Excel (.xlsx)
        </button>
      </div>
    </div>
  )
}
