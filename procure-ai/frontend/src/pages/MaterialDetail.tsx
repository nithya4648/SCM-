import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import api from '../lib/api';
import Badge from '../components/Badge';

export default function MaterialDetail() {
  const { id } = useParams<{ id: string }>();
  const [rfqResult, setRfqResult] = useState<any>(null);

  // We reuse shortages to find the detail (in a real app, this would be a dedicated GET /materials/:id endpoint)
  const { data: shortages, isLoading } = useQuery({
    queryKey: ['shortages'],
    queryFn: async () => {
      const res = await api.get('/shortages/');
      return res.data;
    }
  });

  const generateRfq = useMutation({
    mutationFn: async (quantity: number) => {
      // Required date is hardcoded to 14 days from now for prototype
      const date = new Date();
      date.setDate(date.getDate() + 14);
      const res = await api.post(`/procurement/${id}/rfq`, {
        quantity: quantity,
        required_date: date.toISOString().split('T')[0]
      });
      return res.data;
    },
    onSuccess: (data) => {
      setRfqResult(data);
    }
  });

  if (isLoading) return <div className="text-slate-400">Loading material...</div>;
  
  const material = shortages?.find((s: any) => s.material_id === id);
  if (!material) return <div className="text-red-400">Material not found or no shortage.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">{material.material_name}</h1>
        <p className="text-slate-400">Material ID: {id}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Shortage Details</h2>
            <div className="space-y-4">
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span className="text-slate-400">Required</span>
                <span className="text-white font-medium">{material.required_quantity}</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span className="text-slate-400">Inventory</span>
                <span className="text-white font-medium">{material.inventory_quantity}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Shortfall</span>
                <span className="text-red-400 font-bold">{material.shortage_quantity}</span>
              </div>
            </div>
            
            <button
              onClick={() => generateRfq.mutate(material.shortage_quantity)}
              disabled={generateRfq.isPending || !!rfqResult}
              className="mt-6 w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white rounded-lg font-medium transition-colors"
            >
              {generateRfq.isPending ? 'Generating...' : rfqResult ? 'RFQ Created' : 'Generate RFQ'}
            </button>
          </div>
        </div>

        <div className="col-span-2 space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 min-h-[300px]">
            <h2 className="text-lg font-semibold text-white mb-4">Active RFQs & Quotes</h2>
            {rfqResult ? (
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-emerald-900/20 border border-emerald-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-emerald-400 font-medium">RFQ Created Successfully</span>
                    <Badge variant="success">Status: {rfqResult.status}</Badge>
                  </div>
                  <p className="text-slate-400 text-sm break-all">ID: {rfqResult.id}</p>
                  <div className="mt-4 pt-4 border-t border-emerald-500/20">
                    <p className="text-sm text-slate-300">
                      Mock emails dispatched to suppliers. Quotes will appear here once extracted.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">
                No active RFQs for this material. Generate one to begin.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
