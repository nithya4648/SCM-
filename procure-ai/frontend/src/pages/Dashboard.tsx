import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import StatCard from '../components/StatCard';
import { Package, AlertCircle, Clock, MessageSquare, ShieldAlert } from 'lucide-react';

interface DashboardSummary {
  open_procurement_requirements: int;
  critical_shortages: int;
  rfqs_awaiting: int;
  supplier_responses: int;
  pos_at_risk: int;
}

export default function Dashboard() {
  const { data, isLoading } = useQuery<DashboardSummary>({
    queryKey: ['dashboardSummary'],
    queryFn: async () => {
      const res = await api.get('/dashboard/summary');
      return res.data;
    }
  });

  if (isLoading) return <div className="text-slate-400">Loading dashboard...</div>;
  if (!data) return <div className="text-red-400">Failed to load data.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Procurement Overview</h1>
        <p className="text-slate-400">Real-time insights across your supply chain operations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        <StatCard 
          title="Open Reqs" 
          value={data.open_procurement_requirements} 
          icon={<Package className="w-5 h-5 text-blue-400" />} 
        />
        <StatCard 
          title="Critical Shortages" 
          value={data.critical_shortages} 
          icon={<AlertCircle className="w-5 h-5 text-amber-400" />} 
        />
        <StatCard 
          title="Pending RFQs" 
          value={data.rfqs_awaiting} 
          icon={<Clock className="w-5 h-5 text-indigo-400" />} 
        />
        <StatCard 
          title="Supplier Replies" 
          value={data.supplier_responses} 
          icon={<MessageSquare className="w-5 h-5 text-emerald-400" />} 
        />
        <StatCard 
          title="POs at Risk" 
          value={data.pos_at_risk} 
          icon={<ShieldAlert className="w-5 h-5 text-red-400" />} 
          className="border-red-900/30 bg-red-900/10"
        />
      </div>
    </div>
  );
}
