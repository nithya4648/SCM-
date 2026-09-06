import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import Badge from '../components/Badge';

export default function POList() {
  const navigate = useNavigate();
  const { data: pos, isLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const res = await api.get('/purchase-orders/');
      return res.data;
    },
  });

  if (isLoading) return <div className="text-slate-400">Loading Purchase Orders...</div>;

  const statusVariant = (status: string) => {
    switch (status) {
      case 'Confirmed': return 'success' as const;
      case 'Created': return 'info' as const;
      default: return 'default' as const;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Purchase Orders</h1>
        <p className="text-slate-400">All generated purchase orders and their statuses.</p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/80 text-slate-300">
            <tr>
              <th className="px-6 py-4 font-medium">PO ID</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">ERP Reference</th>
              <th className="px-6 py-4 font-medium">Items</th>
              <th className="px-6 py-4 font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {pos?.map((po: any) => (
              <tr
                key={po.id}
                onClick={() => navigate(`/purchase-orders/${po.id}`)}
                className="hover:bg-slate-700/30 cursor-pointer transition-colors group"
              >
                <td className="px-6 py-4 font-mono text-xs text-slate-300 group-hover:text-blue-400 transition-colors">
                  {po.id.slice(0, 12)}...
                </td>
                <td className="px-6 py-4">
                  <Badge variant={statusVariant(po.status)}>{po.status}</Badge>
                </td>
                <td className="px-6 py-4 font-mono text-xs text-slate-400">
                  {po.erp_reference ?? '—'}
                </td>
                <td className="px-6 py-4 text-white">{po.items?.length ?? 0}</td>
                <td className="px-6 py-4 text-slate-400 text-xs">
                  {new Date(po.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {(!pos || pos.length === 0) && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                  No Purchase Orders yet. Approve an RFQ recommendation to create one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
