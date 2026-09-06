import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import Badge from '../components/Badge';

export default function RFQList() {
  const navigate = useNavigate();
  const { data: rfqs, isLoading } = useQuery({
    queryKey: ['rfqs'],
    queryFn: async () => {
      const res = await api.get('/rfqs/');
      return res.data;
    },
  });

  if (isLoading) return <div className="text-slate-400">Loading RFQs...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Requests for Quote</h1>
        <p className="text-slate-400">Track and manage all procurement RFQs.</p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/80 text-slate-300">
            <tr>
              <th className="px-6 py-4 font-medium">RFQ ID</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Items</th>
              <th className="px-6 py-4 font-medium">Quotes</th>
              <th className="px-6 py-4 font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {rfqs?.map((rfq: any) => (
              <tr
                key={rfq.id}
                onClick={() => navigate(`/rfqs/${rfq.id}`)}
                className="hover:bg-slate-700/30 cursor-pointer transition-colors group"
              >
                <td className="px-6 py-4 font-mono text-xs text-slate-300 group-hover:text-blue-400 transition-colors">
                  {rfq.id.slice(0, 12)}...
                </td>
                <td className="px-6 py-4">
                  <Badge variant={rfq.status === 'Open' ? 'info' : 'success'}>
                    {rfq.status}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-white">{rfq.items?.length ?? 0}</td>
                <td className="px-6 py-4 text-white">{rfq.quotes?.length ?? 0}</td>
                <td className="px-6 py-4 text-slate-400 text-xs">
                  {new Date(rfq.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {(!rfqs || rfqs.length === 0) && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                  No RFQs created yet. Go to a shortage material to generate one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
