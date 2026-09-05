import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

export default function StatCard({ title, value, icon, trend, className = '' }: StatCardProps) {
  return (
    <div className={`bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 flex flex-col gap-4 transition-all hover:bg-slate-800/80 hover:shadow-lg hover:shadow-blue-900/10 ${className}`}>
      <div className="flex items-start justify-between">
        <h3 className="text-slate-400 font-medium text-sm">{title}</h3>
        <div className="text-slate-500 bg-slate-800 p-2 rounded-lg">
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-3">
        <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
        {trend && (
          <span className={`text-xs font-semibold ${trend.isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
            {trend.isPositive ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
