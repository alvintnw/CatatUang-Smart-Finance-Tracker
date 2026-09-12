import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const navItems = [
  { to: '/', label: 'Dashboard', emoji: '📊', end: true },
  { to: '/transactions', label: 'Transaksi', emoji: '📝' },
  { to: '/budgets', label: 'Anggaran', emoji: '🎯' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="font-bold text-brand-700 text-lg">💰 CatatUang</span>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500 hidden sm:block">
              Halo, <span className="font-medium text-gray-700">{user?.full_name}</span>
            </span>
            <button onClick={handleLogout} className="text-sm text-gray-400 hover:text-red-500 transition-colors">
              Keluar
            </button>
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 max-w-5xl mx-auto w-full px-4 py-6 gap-6">
        {/* Sidebar */}
        <aside className="hidden md:block w-48 shrink-0">
          <nav className="space-y-1">
            {navItems.map(({ to, label, emoji, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                <span>{emoji}</span> {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
      </div>

      {/* Bottom nav (mobile) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex">
        {navItems.map(({ to, label, emoji, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center py-3 text-xs font-medium transition-colors ${
                isActive ? 'text-brand-600' : 'text-gray-500'
              }`
            }
          >
            <span className="text-lg">{emoji}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
