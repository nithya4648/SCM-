import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import Badge from '../components/Badge';
import { Mail, Sparkles, BarChart3, CheckCircle2, Loader2, Send, ArrowRight } from 'lucide-react';

const MOCK_SUPPLIER_EMAILS: Record<string, string> = {
  default: `Dear Procurement Team,

Thank you for your RFQ. We are pleased to quote as follows:

- Unit Price: $12.75 per unit
- Quantity Available: 1,000 units
- MOQ: 100 units
- Lead Time: 14 business days
- Manufacturer Part Number: MPN-2024-A1
- Delivery Date: 2026-10-15
- Validity: 30 days
- Payment Terms: Net 30

Best regards,
Sales Team`,
};

function generateEmailForSupplier(index: number): string {
  const variations = [
    {
      price: (10 + Math.random() * 8).toFixed(2),
      qty: 500 + Math.floor(Math.random() * 1000),
      moq: [50, 100, 200][index % 3],
      lead: 7 + Math.floor(Math.random() * 21),
      mpn: `MPN-${2024 + index}-${String.fromCharCode(65 + index)}${index + 1}`,
    },
  ];
  const v = variations[0];
  const deliveryDate = new Date();
  deliveryDate.setDate(deliveryDate.getDate() + v.lead + 5);

  return `Dear Procurement Team,

Thank you for your RFQ. We are pleased to quote as follows:

- Unit Price: $${v.price} per unit
- Quantity Available: ${v.qty} units
- MOQ: ${v.moq} units
- Lead Time: ${v.lead} business days
- Manufacturer Part Number: ${v.mpn}
- Delivery Date: ${deliveryDate.toISOString().split('T')[0]}
- Validity: 30 days
- Payment Terms: Net ${[15, 30, 45][index % 3]}

Best regards,
Sales Team - Supplier ${index + 1}`;
}

interface SimStep {
  supplierId: string;
  supplierIndex: number;
  commId?: string;
  emailSent: boolean;
  extracting: boolean;
  extracted: boolean;
  error?: string;
}

export default function RFQDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [simSteps, setSimSteps] = useState<SimStep[]>([]);
  const [comparison, setComparison] = useState<any>(null);
  const [approvalResult, setApprovalResult] = useState<any>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  // Fetch RFQ detail
  const { data: rfq, isLoading, refetch } = useQuery({
    queryKey: ['rfq', id],
    queryFn: async () => {
      const res = await api.get(`/rfqs/${id}`);
      return res.data;
    },
  });

  // Step 1: Simulate inbound emails for all pending quotes
  const simulateEmails = useMutation({
    mutationFn: async () => {
      const pendingQuotes = rfq.quotes.filter((q: any) => q.status === 'Pending');
      const results: SimStep[] = [];

      for (let i = 0; i < pendingQuotes.length; i++) {
        const quote = pendingQuotes[i];
        const emailBody = generateEmailForSupplier(i);

        // Send mock inbound email
        const inboundRes = await api.post('/supplier-communications/mock-inbound', {
          rfq_id: id,
          supplier_id: quote.supplier_id,
          raw_text: emailBody,
        });

        results.push({
          supplierId: quote.supplier_id,
          supplierIndex: i,
          commId: inboundRes.data.comm_id,
          emailSent: true,
          extracting: false,
          extracted: false,
        });
      }
      return results;
    },
    onSuccess: (data) => {
      setSimSteps(data);
    },
  });

  // Step 2: Extract quotes from the simulated emails
  const extractQuotes = useMutation({
    mutationFn: async () => {
      const updated = [...simSteps];
      for (let i = 0; i < updated.length; i++) {
        updated[i] = { ...updated[i], extracting: true };
        setSimSteps([...updated]);

        try {
          await api.post(
            `/supplier-communications/${updated[i].commId}/extract?rfq_id=${id}`
          );
          updated[i] = { ...updated[i], extracting: false, extracted: true };
        } catch (err: any) {
          updated[i] = {
            ...updated[i],
            extracting: false,
            error: err?.response?.data?.detail || 'Extraction failed',
          };
        }
        setSimSteps([...updated]);
      }
      return updated;
    },
    onSuccess: () => {
      refetch(); // Refresh RFQ to get updated quote statuses
    },
  });

  // Step 3: Compare quotes
  const compareQuotes = async () => {
    setIsComparing(true);
    try {
      const res = await api.post(`/rfqs/${id}/compare`);
      setComparison(res.data);
    } catch (err: any) {
      setComparison({ error: err?.response?.data?.detail || 'Comparison failed' });
    }
    setIsComparing(false);
  };

  // Step 4: Approve recommendation → create PO
  const approveRecommendation = async () => {
    if (!comparison?.recommendation_id) return;
    setIsApproving(true);
    try {
      const res = await api.post(`/recommendations/${comparison.recommendation_id}/approve`);
      setApprovalResult(res.data);
      queryClient.invalidateQueries({ queryKey: ['rfq', id] });
    } catch (err: any) {
      setApprovalResult({ error: err?.response?.data?.detail || 'Approval failed' });
    }
    setIsApproving(false);
  };

  if (isLoading) return <div className="text-slate-400">Loading RFQ...</div>;
  if (!rfq) return <div className="text-red-400">RFQ not found.</div>;

  const pendingQuotes = rfq.quotes.filter((q: any) => q.status === 'Pending');
  const extractedQuotes = rfq.quotes.filter((q: any) => q.status === 'Extracted');
  const allExtracted = simSteps.length > 0 && simSteps.every((s) => s.extracted);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">RFQ Detail</h1>
          <p className="text-slate-400 font-mono text-sm">{id}</p>
        </div>
        <Badge variant={rfq.status === 'Open' ? 'info' : 'success'}>{rfq.status}</Badge>
      </div>

      {/* RFQ Items summary */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Requested Items</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-400 border-b border-slate-700">
              <tr>
                <th className="pb-3 font-medium">Material ID</th>
                <th className="pb-3 font-medium">Quantity</th>
                <th className="pb-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {rfq.items.map((item: any) => (
                <tr key={item.id}>
                  <td className="py-4 font-mono text-xs text-slate-300">{item.material_id}</td>
                  <td className="py-4 text-white">{item.quantity}</td>
                  <td className="py-4 text-slate-400 text-xs">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Supplier Quotes */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Supplier Quotes ({rfq.quotes.length})</h2>
        {rfq.quotes.length === 0 ? (
          <p className="text-slate-400">No quotes yet.</p>
        ) : (
          <div className="space-y-3">
            {rfq.quotes.map((quote: any, idx: number) => (
              <div
                key={quote.id}
                className="p-4 rounded-lg bg-slate-700/30 border border-slate-600/50"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">Supplier {idx + 1}</span>
                    <span className="text-xs text-slate-500 font-mono">{quote.supplier_id.slice(0, 8)}...</span>
                  </div>
                  <Badge
                    variant={
                      quote.status === 'Pending'
                        ? 'warning'
                        : quote.status === 'Extracted'
                        ? 'success'
                        : 'default'
                    }
                  >
                    {quote.status}
                  </Badge>
                </div>
                {quote.items && quote.items.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <span className="text-slate-400">Unit Price</span>
                      <div className="text-white font-medium">
                        {quote.items[0].unit_price != null ? `$${quote.items[0].unit_price.toFixed(2)}` : '—'}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400">Quantity</span>
                      <div className="text-white font-medium">
                        {quote.items[0].quoted_quantity ?? '—'}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400">Lead Time</span>
                      <div className="text-white font-medium">
                        {quote.items[0].lead_time_days != null ? `${quote.items[0].lead_time_days}d` : '—'}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400">MOQ</span>
                      <div className="text-white font-medium">
                        {quote.items[0].moq ?? '—'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pipeline Actions */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 space-y-6">
        <h2 className="text-lg font-semibold text-white mb-2">Pipeline Actions</h2>

        {/* Step 1: Simulate Emails */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-sm font-bold">
              1
            </div>
            <div>
              <h3 className="text-white font-medium">Simulate Supplier Responses</h3>
              <p className="text-slate-400 text-sm">
                Send mock inbound emails for {pendingQuotes.length} pending quote(s)
              </p>
            </div>
          </div>
          <button
            onClick={() => simulateEmails.mutate()}
            disabled={simulateEmails.isPending || simSteps.length > 0 || pendingQuotes.length === 0}
            className="ml-11 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            {simulateEmails.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {simSteps.length > 0
              ? `${simSteps.length} Email(s) Sent`
              : 'Simulate Inbound Emails'}
          </button>
          {simSteps.length > 0 && (
            <div className="ml-11 space-y-2">
              {simSteps.map((s, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-sm p-2 rounded bg-slate-700/20"
                >
                  <Mail className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-300">Supplier {i + 1}</span>
                  {s.emailSent && (
                    <Badge variant="success">Email Sent</Badge>
                  )}
                  {s.extracted && <Badge variant="info">Extracted</Badge>}
                  {s.extracting && (
                    <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
                  )}
                  {s.error && <Badge variant="danger">{s.error}</Badge>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Step 2: Extract */}
        <div className="space-y-3 border-t border-slate-700 pt-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-bold">
              2
            </div>
            <div>
              <h3 className="text-white font-medium">AI Quote Extraction</h3>
              <p className="text-slate-400 text-sm">
                Use AI to parse supplier emails into structured quote data
              </p>
            </div>
          </div>
          <button
            onClick={() => extractQuotes.mutate()}
            disabled={
              extractQuotes.isPending ||
              simSteps.length === 0 ||
              allExtracted
            }
            className="ml-11 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            {extractQuotes.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            {allExtracted ? 'All Quotes Extracted' : 'Extract Quotes via AI'}
          </button>
        </div>

        {/* Step 3: Compare */}
        <div className="space-y-3 border-t border-slate-700 pt-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm font-bold">
              3
            </div>
            <div>
              <h3 className="text-white font-medium">Compare & Score</h3>
              <p className="text-slate-400 text-sm">
                Deterministic scoring + LLM explanation
              </p>
            </div>
          </div>
          <button
            onClick={compareQuotes}
            disabled={isComparing || (!allExtracted && extractedQuotes.length === 0) || !!comparison}
            className="ml-11 px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            {isComparing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <BarChart3 className="w-4 h-4" />
            )}
            {comparison ? 'Comparison Complete' : 'Compare Quotes'}
          </button>

          {comparison && !comparison.error && (
            <div className="ml-11 space-y-4">
              <div className="p-4 rounded-lg bg-amber-900/10 border border-amber-500/20">
                <h4 className="text-amber-400 font-medium mb-3">Ranked Results</h4>
                <div className="space-y-2">
                  {comparison.ranked_quotes?.map((rq: any, i: number) => (
                    <div
                      key={rq.quote_id}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        i === 0
                          ? 'bg-emerald-900/20 border border-emerald-500/30'
                          : 'bg-slate-700/20'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-400 text-sm">#{i + 1}</span>
                        <span className="text-white text-sm font-mono">
                          {rq.supplier_id?.slice(0, 8)}...
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-slate-400">
                          ${rq.unit_price?.toFixed(2) ?? '—'}
                        </span>
                        <span className="text-slate-400">{rq.lead_time_days ?? '—'}d</span>
                        <span
                          className={`font-bold ${
                            i === 0 ? 'text-emerald-400' : 'text-slate-300'
                          }`}
                        >
                          Score: {rq.score?.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {comparison.explanation && (
                <div className="p-4 rounded-lg bg-slate-700/30 border border-slate-600/50">
                  <h4 className="text-slate-300 font-medium mb-2 text-sm">AI Explanation</h4>
                  <p className="text-slate-400 text-sm whitespace-pre-line leading-relaxed">
                    {comparison.explanation}
                  </p>
                </div>
              )}
            </div>
          )}
          {comparison?.error && (
            <div className="ml-11 p-3 rounded-lg bg-red-900/10 border border-red-500/20 text-red-400 text-sm">
              {comparison.error}
            </div>
          )}
        </div>

        {/* Step 4: Approve → PO */}
        <div className="space-y-3 border-t border-slate-700 pt-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm font-bold">
              4
            </div>
            <div>
              <h3 className="text-white font-medium">Approve & Generate PO</h3>
              <p className="text-slate-400 text-sm">
                Approve the top recommendation to create a Purchase Order
              </p>
            </div>
          </div>
          <button
            onClick={approveRecommendation}
            disabled={
              isApproving ||
              !comparison?.recommendation_id ||
              !!approvalResult
            }
            className="ml-11 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            {isApproving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            {approvalResult && !approvalResult.error
              ? 'PO Created'
              : 'Approve Recommendation'}
          </button>

          {approvalResult && !approvalResult.error && (
            <div className="ml-11 p-4 rounded-lg bg-emerald-900/20 border border-emerald-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-emerald-400 font-medium">Purchase Order Created</h4>
                  <p className="text-slate-400 text-sm mt-1 font-mono">
                    PO ID: {approvalResult.id}
                  </p>
                  {approvalResult.erp_reference && (
                    <p className="text-slate-400 text-sm font-mono">
                      ERP: {approvalResult.erp_reference}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => navigate(`/purchase-orders/${approvalResult.id}`)}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-1"
                >
                  View PO <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
          {approvalResult?.error && (
            <div className="ml-11 p-3 rounded-lg bg-red-900/10 border border-red-500/20 text-red-400 text-sm">
              {approvalResult.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
