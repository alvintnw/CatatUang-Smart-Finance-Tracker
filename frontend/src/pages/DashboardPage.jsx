import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Legend,
} from 'recharts'
import api from '../lib/api'
import { formatRupiah, currentMonthYear, MONTHS_ID, CATEGORY_COLORS } from '../lib/utils'
import TransactionForm from '../components/TransactionForm'
import ExportButtons from '../components/ExportButtons'

export default function DashboardPage() {
  const { month: curMonth, year: curYear } = currentMonthYear()
  const [month, setMonth] = useState(curMonth)
  const [year, setYear] = useState(curYear)
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  async function fetchData() {
    setLoading(true)
    try {
      const [{ data: s }, { data: t }] = await Promise.all([
        api.get('/dashboard/summary', { params: { month, year } }),
        api.get('/dashboard/trend', { params: { months: 6 } }),
      ])
      setSummary(s)
      setTrend(t)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [month, year])

  const pieData = summary?.breakdown?.map((b) => ({
    name: b.category,
    slug: b.slug,
    value: Number(b.total),
  })) || []

  const trendData = trend.map((p) => ({
    name: p.label,
    Pemasukan: Number(p.total_income),
    Pengeluaran: Number(p.total_expense),
  }))

  return (
    <div className="pb-20 md:pb-0 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">Dashboard</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Catat
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-md max-h-[90vh] overflow-y-auto p-5 shadow-xl">
            <h2 className="text-lg font-semibold mb-4">Catat Transaksi Baru</h2>
            <TransactionForm
              onSuccess={() => { setShowForm(false); fetchData() }}
              onCancel={() => setShowForm(false)}
            />
          </div>
        </div>
      )}

      {/* Month selector */}
      <div className="flex gap-2">
        <select
          className="input w-auto"
          value={month}
          onChange={(e) => setMonth(Number(e.target.value))}
        >
          {MONTHS_ID.slice(1).map((m, i) => (
            <option key={i + 1} value={i + 1}>{m}</option>
          ))}
        </select>
        <select
          className="input w-auto"
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
        >
          {[curYear - 1, curYear, curYear + 1].map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-16 text-gray-400">Memuat…</div>
      ) : (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-3 gap-3">
            <SummaryCard
              label="Pemasukan"
              amount={summary?.total_income || 0}
              color="text-green-600"
              bg="bg-green-50"
              emoji="📥"
            />
            <SummaryCard
              label="Pengeluaran"
              amount={summary?.total_expense || 0}
              color="text-red-500"
              bg="bg-red-50"
              emoji="📤"
            />
            <SummaryCard
              label="Saldo"
              amount={summary?.balance || 0}
              color={Number(summary?.balance) >= 0 ? 'text-brand-600' : 'text-red-600'}
              bg={Number(summary?.balance) >= 0 ? 'bg-brand-50' : 'bg-red-50'}
              emoji="💰"
            />
          </div>

          {/* Insights */}
          {summary?.insights?.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-gray-700 mb-3">💡 Insight Otomatis</h2>
              <ul className="space-y-2">
                {summary.insights.map((insight, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-600">
                    <span className="text-blue-400 mt-0.5">▸</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Pie chart */}
          {pieData.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-gray-700 mb-4">
                Breakdown Pengeluaran — {MONTHS_ID[month]} {year}
              </h2>
              <div className="flex flex-col sm:flex-row items-center gap-4">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) =>
                        percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : ''
                      }
                      labelLine={false}
                    >
                      {pieData.map((entry) => (
                        <Cell
                          key={entry.slug}
                          fill={CATEGORY_COLORS[entry.slug] || '#9ca3af'}
                        />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => formatRupiah(v)} />
                  </PieChart>
                </ResponsiveContainer>
                {/* Legend */}
                <div className="space-y-1 w-full sm:w-auto shrink-0">
                  {pieData.map((entry) => (
                    <div key={entry.slug} className="flex items-center gap-2 text-sm">
                      <span
                        className="w-3 h-3 rounded-full shrink-0"
                        style={{ backgroundColor: CATEGORY_COLORS[entry.slug] || '#9ca3af' }}
                      />
                      <span className="text-gray-600 flex-1">{entry.name}</span>
                      <span className="font-medium text-gray-700">{formatRupiah(entry.value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Trend chart */}
          {trendData.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-gray-700 mb-4">Tren 6 Bulan Terakhir</h2>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis
                    tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip formatter={(v) => formatRupiah(v)} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="Pemasukan"
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Pengeluaran"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Export */}
          <ExportButtons month={month} year={year} />
        </>
      )}
    </div>
  )
}

function SummaryCard({ label, amount, color, bg, emoji }) {
  return (
    <div className={`rounded-xl p-3 ${bg} text-center`}>
      <p className="text-base mb-1">{emoji}</p>
      <p className={`font-bold text-sm sm:text-base ${color}`}>
        {formatRupiah(Math.abs(amount))}
      </p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
    </div>
  )
}
