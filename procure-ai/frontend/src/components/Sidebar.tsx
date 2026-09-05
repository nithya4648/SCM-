import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, AlertTriangle, FileText, ShoppingCart } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/shortages', icon: AlertTriangle, label: 'Shortages' },
    { to: '/rfqs', icon: FileText, label: 'RFQs' },
    { to: '/purchase-orders', icon: ShoppingCart, label: 'Purchase Orders' },
  ];

  return (
    <div className="w-64 bg-slate-800 border-r border-slate-700 min-h-screen flex flex-col p-4">
      <div className="flex items-center gap-3 px-2 py-4 mb-6 text-white font-bold text-xl tracking-tight">
        <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        ProcureAI
      </div>
      
      <nav className="flex-1 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-blue-500/10 text-blue-400' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
              }`
            }
          >
            <link.icon className="w-5 h-5" />
            {link.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
