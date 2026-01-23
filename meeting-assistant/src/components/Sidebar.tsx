import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Mic, 
  Clock, 
  Settings, 
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Zap
} from 'lucide-react';
import { useUIStore } from '@/store';
import './Sidebar.css';

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/meeting', icon: Mic, label: 'Meeting' },
  { path: '/history', icon: Clock, label: 'History' },
  { path: '/integrations', icon: Zap, label: 'Integrations' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <MessageSquare className="logo-icon" />
          {!sidebarCollapsed && <span className="logo-text">MeetAI</span>}
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => 
              `sidebar-nav-item ${isActive ? 'active' : ''}`
            }
            title={label}
          >
            <Icon className="nav-icon" />
            {!sidebarCollapsed && <span className="nav-label">{label}</span>}
          </NavLink>
        ))}
      </nav>

      <button 
        className="sidebar-toggle"
        onClick={toggleSidebar}
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {sidebarCollapsed ? <ChevronRight /> : <ChevronLeft />}
      </button>
    </aside>
  );
}
