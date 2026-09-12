/**
 * Format number as IDR currency string.
 * e.g. 45000 → "Rp 45.000"
 */
export function formatRupiah(amount) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format a date string to Indonesian display format.
 * e.g. "2024-06-01" → "1 Juni 2024"
 */
export function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(dateStr + 'T00:00:00'))
}

export const MONTHS_ID = [
  '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

export function currentMonthYear() {
  const d = new Date()
  return { month: d.getMonth() + 1, year: d.getFullYear() }
}

export const CATEGORY_COLORS = {
  makanan: '#f59e0b',
  transportasi: '#3b82f6',
  tagihan: '#8b5cf6',
  belanja: '#ec4899',
  hiburan: '#10b981',
  pendidikan: '#0ea5e9',
  kesehatan: '#ef4444',
  gaji: '#22c55e',
  'lain-lain': '#9ca3af',
}
