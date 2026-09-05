import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import Badge from '../components/Badge';

interface Shortage {
  material_id: string;
  material_name: string;
  required_quantity: number;
  inventory_quantity: number;
  shortage_quantity: number;
}

export default function Shortages() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery<Shortage[]>({
    queryKey: ['shortages'],
    queryFn: async () => {
      const res = await api.get('/shortages/');
      return res.data;
    }
  });

  if (isLoading) return <div className="text-slate-400">Loading shortages...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Material Shortages</h1>
        <p className="text-slate-400">Items requiring immediate procurement action.</p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/80 text-slate-300">
            <tr>
              <th className="px-6 py-4 font-medium">Material</th>
              <th className="px-6 py-4 font-medium">Required</th>
              <th className="px-6 py-4 font-medium">Inventory</th>
              <th className="px-6 py-4 font-medium">Shortage</th>
              <th className="px-6 py-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {data?.map((item) => (
              <tr 
                key={item.material_id} 
                onClick={() => navigate(`/materials/${item.material_id}`)}
                className="hover:bg-slate-700/30 cursor-pointer transition-colors group"
              >
                <td className="px-6 py-4 font-medium text-white group-hover:text-blue-400 transition-colors">
                  {item.material_name}
                </td>
                <td className="px-6 py-4 text-slate-300">{item.required_quantity}</td>
                <td className="px-6 py-4 text-slate-300">{item.inventory_quantity}</td>
                <td className="px-6 py-4 text-red-400 font-medium">{item.shortage_quantity}</td>
                <td className="px-6 py-4">
                  <Badge variant="danger">Critical</Badge>
                </td>
              </tr>
            ))}
            {data?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                  No shortages detected.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
