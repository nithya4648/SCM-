import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import Badge from '../components/Badge';
import { ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function PODetail() {
  const { id } = useParams<{ id: string }>();

  const { data: po, isLoading: poLoading } = useQuery({
    queryKey: ['po', id],
    queryFn: async () => {
      const res = await api.get(`/purchase-orders/${id}`);
      return res.data;
    }
  });

  const { data: risks, isLoading: risksLoading } = useQuery({
    queryKey: ['po-risks', id],
    queryFn: async () => {
      const res = await api.get(`/purchase-orders/${id}/risk`);
      return res.data;
    }
  });

  if (poLoading || risksLoading) return <div className="text-slate-400">Loading Purchase Order...</div>;
  if (!po) return <div className="text-red-400">Purchase Order not found.</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Purchase Order</h1>
          <p className="text-slate-400 font-mono text-sm">{id}</p>
        </div>
        <Badge variant={po.status === 'Created' ? 'info' : 'success'}>
          {po.status}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Line Items</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-slate-400 border-b border-slate-700">
                  <tr>
                    <th className="pb-3 font-medium">Material ID</th>
                    <th className="pb-3 font-medium">Quantity</th>
                    <th className="pb-3 font-medium">Unit Price</th>
                    <th className="pb-3 font-medium">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {po.items.map((item: any) => (
                    <tr key={item.id}>
                      <td className="py-4 font-mono text-xs text-slate-300">{item.material_id}</td>
                      <td className="py-4 text-white">{item.quantity}</td>
                      <td className="py-4 text-white">${item.unit_price?.toFixed(2)}</td>
                      <td className="py-4 text-white font-medium">${(item.quantity * item.unit_price)?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-span-1 space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">ERP Integration</h2>
            {po.erp_reference ? (
              <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/30 border border-slate-600/50">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-xs text-slate-400">ERP Reference</div>
                  <div className="font-mono text-sm text-slate-200">{po.erp_reference}</div>
                </div>
              </div>
            ) : (
              <div className="text-slate-400 text-sm">Not synced to ERP.</div>
            )}
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-slate-400" />
              Risk Events
            </h2>
            {risks && risks.length > 0 ? (
              <div className="space-y-3">
                {risks.map((risk: any) => (
                  <div key={risk.id} className="p-3 rounded-lg bg-red-900/10 border border-red-500/20">
                    <div className="flex justify-between items-start mb-2">
                      <Badge variant="danger">{risk.severity}</Badge>
                      <span className="text-xs text-slate-500">{new Date(risk.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-slate-300">{risk.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-emerald-400 text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> No delivery risks detected.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
