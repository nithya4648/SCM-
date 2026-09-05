import React from 'react';

interface BadgeProps {
  variant: 'default' | 'success' | 'warning' | 'danger' | 'info';
  children: React.ReactNode;
}

export default function Badge({ variant, children }: BadgeProps) {
  const styles = {
    default: 'bg-slate-700 text-slate-300',
    success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    danger: 'bg-red-500/10 text-red-400 border border-red-500/20',
    info: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[variant]}`}>
      {children}
    </span>
  );
}
