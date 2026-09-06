import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import StatCard from '../components/StatCard';
import { Package, AlertCircle, Clock, MessageSquare, ShieldAlert } from 'lucide-react';

interface DashboardSummary {
  open_procurement_requirements: number;
  critical_shortages: number;
  rfqs_awaiting: number;
  supplier_responses: number;
  pos_at_risk: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
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
        <div onClick={() => navigate('/shortages')} className="cursor-pointer">
          <StatCard 
            title="Open Reqs" 
            value={data.open_procurement_requirements} 
            icon={<Package className="w-5 h-5 text-blue-400" />} 
          />
        </div>
        <div onClick={() => navigate('/shortages')} className="cursor-pointer">
          <StatCard 
            title="Critical Shortages" 
            value={data.critical_shortages} 
            icon={<AlertCircle className="w-5 h-5 text-amber-400" />} 
          />
        </div>
        <div onClick={() => navigate('/rfqs')} className="cursor-pointer">
          <StatCard 
            title="Pending RFQs" 
            value={data.rfqs_awaiting} 
            icon={<Clock className="w-5 h-5 text-indigo-400" />} 
          />
        </div>
        <div onClick={() => navigate('/rfqs')} className="cursor-pointer">
          <StatCard 
            title="Supplier Replies" 
            value={data.supplier_responses} 
            icon={<MessageSquare className="w-5 h-5 text-emerald-400" />} 
          />
        </div>
        <div onClick={() => navigate('/purchase-orders')} className="cursor-pointer">
          <StatCard 
            title="POs at Risk" 
            value={data.pos_at_risk} 
            icon={<ShieldAlert className="w-5 h-5 text-red-400" />} 
            className="border-red-900/30 bg-red-900/10"
          />
        </div>
      </div>
    </div>
  );
}
