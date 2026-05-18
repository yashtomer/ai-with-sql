import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  Database, 
  History, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  ChevronRight,
  Sun,
  Moon,
  Search,
  Bell,
  User
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';

const SidebarItem = ({ icon: Icon, label, path, active, collapsed }) => (
  <Link to={path}>
    <motion.div
      whileHover={{ x: 4 }}
      className={`flex items-center gap-4 px-4 py-3 rounded-lg transition-all duration-200 group cursor-pointer
        ${active 
          ? 'bg-brand text-white shadow-[0_0_20px_rgba(198,32,8,0.25)]' 
          : 'text-[var(--ds-text-muted)] hover:text-[var(--ds-text)] hover:bg-[var(--ds-surface-2)]'}`}
    >
      <Icon size={20} className={active ? 'text-white' : 'group-hover:text-brand'} />
      {!collapsed && (
        <span className="ds-caption font-semibold tracking-wider uppercase">
          {label}
        </span>
      )}
      {active && !collapsed && (
        <motion.div layoutId="active-indicator" className="ml-auto">
          <ChevronRight size={14} />
        </motion.div>
      )}
    </motion.div>
  </Link>
);

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: Database, label: 'Explorer', path: '/explorer' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[var(--ds-bg)] flex overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 80 : 260 }}
        className="hidden lg:flex flex-col border-r border-[var(--ds-border)] bg-[var(--ds-surface)] relative z-20"
      >
        <div className="p-6 flex justify-center mb-8">
          <div className="w-32 h-20 flex items-center justify-center">
            <img 
              src={theme === 'dark' ? "/assets/logo-white.svg" : "/assets/logo.svg"} 
              alt="Aeologic" 
              className="w-full h-full object-contain" 
            />
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {menuItems.map((item) => (
            <SidebarItem
              key={item.path}
              {...item}
              active={location.pathname === item.path}
              collapsed={collapsed}
            />
          ))}
        </nav>

        <div className="p-4 mt-auto space-y-2 border-t border-[var(--ds-border)]">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-4 px-4 py-3 text-[var(--ds-text-muted)] hover:text-brand hover:bg-brand/5 rounded-lg transition-all group"
          >
            <LogOut size={20} className="group-hover:text-brand" />
            {!collapsed && <span className="ds-caption font-semibold uppercase">Sign Out</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Topbar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-[var(--ds-border)] bg-[var(--ds-bg)]/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setCollapsed(!collapsed)}
              className="lg:flex hidden p-2 text-[var(--ds-text-muted)] hover:text-[var(--ds-text)] transition-colors"
            >
              <Menu size={20} />
            </button>
            <div className="flex items-center gap-2 text-[var(--ds-text-muted)] ds-caption font-semibold uppercase tracking-wider">
              <span>Admin</span>
              <ChevronRight size={14} />
              <span className="text-[var(--ds-text)]">
                {menuItems.find(i => i.path === location.pathname)?.label || 'Dashboard'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button 
              onClick={toggleTheme}
              className="p-2 text-[var(--ds-text-muted)] hover:text-[var(--ds-text)] transition-colors bg-[var(--ds-surface-2)] rounded-lg border border-[var(--ds-border)]"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <div className="flex items-center gap-3 pl-6 border-l border-[var(--ds-border)]">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-bold text-[var(--ds-text)] leading-tight">{user?.name}</p>
                <p className="text-[9px] text-[var(--ds-text-faint)] uppercase tracking-wider">System Architect</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand to-[#911a07] flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {user?.name?.charAt(0)}
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 relative custom-scrollbar">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
