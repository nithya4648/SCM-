import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import Badge from '../components/Badge';
import { ShieldAlert, CheckCircle2, Truck, Loader2 } from 'lucide-react';

export default function PODetail() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const [confirmQty, setConfirmQty] = useState('');
  const [confirmDate, setConfirmDate] = useState('');
  const [deliveryResult, setDeliveryResult] = useState<any>(null);

  const { data: po, isLoading: poLoading } = useQuery({
    queryKey: ['po', id],
    queryFn: async () => {
      const res = await api.get(`/purchase-orders/${id}`);
      return res.data;
    }
  });

  const { data: risks, isLoading: risksLoading, refetch: refetchRisks } = useQuery({
    queryKey: ['po-risks', id],
    queryFn: async () => {
      const res = await api.get(`/purchase-orders/${id}/risk`);
      return res.data;
    }
  });

  const confirmDelivery = useMutation({
    mutationFn: async () => {
      const res = await api.post(`/purchase-orders/${id}/confirm`, {
        confirmed_quantity: parseFloat(confirmQty),
        first_delivery_date: new Date(confirmDate).toISOString(),
      });
      return res.data;
    },
    onSuccess: (data) => {
      setDeliveryResult(data);
      queryClient.invalidateQueries({ queryKey: ['po', id] });
      refetchRisks();
    },
  });

  if (poLoading || risksLoading) return <div className="text-slate-400">Loading Purchase Order...</div>;
  if (!po) return <div className="text-red-400">Purchase Order not found.</div>;

  // Suggest values from PO items for the form
  const totalQty = po.items?.reduce((sum: number, item: any) => sum + item.quantity, 0) ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Purchase Order</h1>
          <p className="text-slate-400 font-mono text-sm">{id}</p>
        </div>
        <Badge variant={po.status === 'Created' ? 'info' : po.status === 'Confirmed' ? 'success' : 'default'}>
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

          {/* Delivery Confirmation Form */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Truck className="w-5 h-5 text-slate-400" />
              Delivery Confirmation
            </h2>

            {deliveryResult ? (
              <div className="p-4 rounded-lg bg-emerald-900/20 border border-emerald-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Delivery Confirmed</span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm mt-3">
                  <div>
                    <span className="text-slate-400">Quantity Committed</span>
                    <div className="text-white font-medium">{deliveryResult.quantity}</div>
                  </div>
                  <div>
                    <span className="text-slate-400">Committed Date</span>
                    <div className="text-white font-medium">
                      {new Date(deliveryResult.committed_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-slate-400 text-sm">
                  Simulate a supplier confirming delivery for this PO. This will trigger risk event
                  analysis comparing against Sales Order requirements.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Confirmed Quantity</label>
                    <input
                      type="number"
                      value={confirmQty}
                      onChange={(e) => setConfirmQty(e.target.value)}
                      placeholder={`Ordered: ${totalQty}`}
                      className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1">Delivery Date</label>
                    <input
                      type="date"
                      value={confirmDate}
                      onChange={(e) => setConfirmDate(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                </div>
                <button
                  onClick={() => confirmDelivery.mutate()}
                  disabled={confirmDelivery.isPending || !confirmQty || !confirmDate}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                >
                  {confirmDelivery.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Truck className="w-4 h-4" />
                  )}
                  Confirm Delivery
                </button>
                {confirmDelivery.isError && (
                  <div className="p-3 rounded-lg bg-red-900/10 border border-red-500/20 text-red-400 text-sm">
                    {(confirmDelivery.error as any)?.response?.data?.detail || 'Confirmation failed'}
                  </div>
                )}
              </div>
            )}
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
