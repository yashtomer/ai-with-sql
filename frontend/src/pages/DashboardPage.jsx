import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Play, 
  ShieldCheck, 
  Zap, 
  Database, 
  Table as TableIcon, 
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertCircle,
  Copy,
  Download,
  LayoutDashboard,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useConfig } from '../context/ConfigContext';

const DashboardPage = () => {
  const { user } = useAuth();
  const { llmConfig } = useConfig();
  const [nlQuery, setNlQuery] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [generatedSql, setGeneratedSql] = useState('');
  const [explanation, setExplanation] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [databases, setDatabases] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [isLoadingDatabases, setIsLoadingDatabases] = useState(false);

  const getlicenseQuestions = [
    { icon: "💰", label: "Agent Commission Audit", query: "Calculate the total commission earned by each agent in the current month by joining agent_transactions with commission_ranges. Identify which agents have reached a top-tier commission bracket but still have more than 10% of their transactions in a 'pending' state in payment_webhook." },
    { icon: "⏳", label: "Renewal Bottleneck Analysis", query: "Identify renewal_orders that have taken longer than the average processing time to move from 'initiated' to 'completed'. Cross-reference these with the scrape_status and failed_vehicle_fetches tables to find delays by province." },
    { icon: "💳", label: "EMI Health & Payments", query: "For all active installment_plans, generate a report showing the percentage of payment_emis that were successfully processed versus failed. Filter for owners who have more than 2 vehicles in the vehicles table." },
    { icon: "📉", label: "Province Fee Volatility", query: "Find the top 3 provinces with the most frequent price changes in the last 6 months using the province_master_rate_history table. Show the variance for 'Heavy Vehicle' categories." },
    { icon: "📄", label: "Document & Debt Compliance", query: "List all owners who have missing entries in the documents table for at least one of their vehicles, but currently have an outstanding balance in natis_payment_transactions." }
  ];

  useEffect(() => {
    fetchDatabases();
  }, []);

  const fetchDatabases = async () => {
    setIsLoadingDatabases(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/databases`);
      const data = await response.json();
      if (response.ok) {
        setDatabases(data.databases || []);
        if (data.databases?.length > 0) setSelectedDatabase(data.databases[0]);
      }
    } catch (err) {
      console.error("Failed to fetch databases", err);
    } finally {
      setIsLoadingDatabases(false);
    }
  };

  const handleGenerate = async () => {
    if (!nlQuery.trim()) return;
    if (!llmConfig.apiKey) {
      setError('Please configure your AI provider and API key in Settings first.');
      return;
    }
    
    setIsGenerating(true);
    setError('');
    setGeneratedSql('');
    setResults(null);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          nl_query: nlQuery,
          database: selectedDatabase,
          llm_config: {
            provider: llmConfig.provider,
            model: llmConfig.model,
            api_key: llmConfig.apiKey
          }
        }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setGeneratedSql(data.sql_query);
        setExplanation(data.explanation);
      } else {
        setError(data.error || 'Failed to generate SQL');
      }
    } catch (err) {
      setError('Connection failed. Please ensure the backend server is running.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecute = async () => {
    if (!generatedSql) return;
    setIsExecuting(true);
    setError('');
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          sql_query: generatedSql,
          llm_config: {
            provider: llmConfig.provider,
            model: llmConfig.model,
            api_key: llmConfig.apiKey
          }
        }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setResults(data);
      } else {
        setError(data.error || 'Execution failed');
      }
    } catch (err) {
      setError('Connection failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const downloadCSV = () => {
    if (!results || !results.results.length) return;
    const headers = Object.keys(results.results[0]).join(',');
    const rows = results.results.map(row => Object.values(row).join(','));
    const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows.join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `query_results_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 mb-3"
          >
            <div className="ds-brand-line" />
            <span className="ds-label-brand">Command Center</span>
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="ds-heading-lg text-[var(--ds-text)]"
          >
            Welcome back, {user?.name?.split(' ')[0]}
          </motion.h1>
        </div>
        
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-4 bg-[var(--ds-surface-2)] p-2 rounded-xl border border-[var(--ds-border)]"
        >
          {llmConfig.apiKey ? (
            <div className="px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-[10px] font-bold text-green-500 uppercase tracking-widest">
                {llmConfig.provider} • {llmConfig.model}
              </span>
            </div>
          ) : (
            <Link to="/settings" className="px-4 py-2 bg-brand/10 border border-brand/20 rounded-lg flex items-center gap-2 hover:bg-brand/20 transition-colors">
              <AlertCircle size={14} className="text-brand" />
              <span className="text-[10px] font-bold text-brand uppercase tracking-widest">Configure AI Provider</span>
            </Link>
          )}
        </motion.div>
      </div>

      {!llmConfig.apiKey && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-brand/10 border border-brand/20 rounded-xl flex items-center justify-between"
        >
          <div className="flex items-center gap-3 text-brand">
            <AlertCircle size={20} />
            <p className="text-sm font-bold text-brand">AI functions are disabled. Please configure your provider settings to begin generating queries.</p>
          </div>
          <Link to="/settings" className="ds-btn-primary h-9 px-4 text-xs flex items-center gap-2">
            GO TO SETTINGS <ExternalLink size={14} />
          </Link>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Panel */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="ds-card p-6"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-brand/10 rounded-lg text-brand">
                  <Sparkles size={20} />
                </div>
                <h3 className="ds-heading-sm text-[var(--ds-text)]">Natural Language Query</h3>
              </div>
              
              <div className="flex items-center gap-2 bg-[var(--ds-surface-2)] p-1 rounded-lg border border-[var(--ds-border)]">
                <Database size={14} className="ml-2 text-[var(--ds-text-faint)]" />
                <select 
                  value={selectedDatabase}
                  onChange={(e) => setSelectedDatabase(e.target.value)}
                  className="bg-transparent border-none outline-none text-[10px] font-bold text-[var(--ds-text)] uppercase tracking-wider pr-2 py-1"
                >
                  {databases.length > 0 ? (
                    databases.map(db => <option key={db} value={db}>{db}</option>)
                  ) : (
                    <option value="">No DB Found</option>
                  )}
                </select>
              </div>
            </div>

            <div className="bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-xl overflow-hidden transition-all focus-within:border-brand/40 shadow-inner">
              <textarea
                value={nlQuery}
                onChange={(e) => setNlQuery(e.target.value)}
                placeholder="e.g. Show me the top 10 users by total spending in the last 30 days..."
                className="w-full h-32 bg-transparent p-4 text-[var(--ds-text)] ds-body outline-none resize-none border-none"
              />
              <div className="p-3 border-t border-[var(--ds-border)] bg-[var(--ds-surface-3)]/30 flex flex-col sm:flex-row justify-between items-center gap-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[10px] text-[var(--ds-text-faint)] font-bold uppercase">Quick Examples:</span>
                  {['User Statistics', 'Sales Report', 'Recent Activity'].map(tip => (
                    <button 
                      key={tip}
                      onClick={() => setNlQuery(tip === 'User Statistics' ? "Show me the total number of users and their average age" : tip === 'Sales Report' ? "Get top 10 products by sales revenue this month" : "Find all orders placed in the last 7 days with customer details")}
                      className="text-[9px] font-bold text-[var(--ds-text-muted)] hover:text-brand bg-[var(--ds-surface-2)] px-2.5 py-1 rounded-md border border-[var(--ds-border)] transition-colors"
                    >
                      {tip}
                    </button>
                  ))}
                </div>
                
                <button 
                  onClick={handleGenerate}
                  disabled={isGenerating || !nlQuery.trim() || !llmConfig.apiKey}
                  className="ds-btn-primary h-10 px-6 group disabled:opacity-50 w-full sm:w-auto"
                >
                  {isGenerating ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      THINKING...
                    </div>
                  ) : (
                    <>
                      <Zap size={15} className="mr-2 fill-current" />
                      GENERATE SQL
                    </>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 p-4 bg-brand/10 border border-brand/20 rounded-xl flex items-center gap-3 text-brand"
              >
                <AlertCircle size={18} />
                <p className="text-sm font-bold">{error}</p>
              </motion.div>
            )}
          </motion.div>

          <AnimatePresence>
            {generatedSql && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-6"
              >
                {/* SQL Result Area */}
                <div className="ds-card p-6 border-l-4 border-l-brand">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3 text-brand">
                      <ShieldCheck size={20} />
                      <h3 className="ds-heading-sm">Validated SQL Command</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <button 
                        onClick={() => copyToClipboard(generatedSql)}
                        className="p-2 hover:bg-[var(--ds-surface-3)] rounded-lg transition-colors text-[var(--ds-text-faint)]"
                      >
                        <Copy size={16} />
                      </button>
                      <button 
                        onClick={handleExecute}
                        disabled={isExecuting}
                        className="flex items-center gap-2 bg-brand text-white px-4 py-2 rounded-lg ds-caption font-bold hover:shadow-[0_0_20px_rgba(198,32,8,0.3)] transition-all disabled:opacity-50"
                      >
                        {isExecuting ? (
                          <>
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            EXECUTING...
                          </>
                        ) : (
                          <>
                            <Play size={14} fill="currentColor" />
                            EXECUTE
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                  
                  <div className="bg-[#0c0c14] p-4 rounded-xl border border-white/5 overflow-x-auto">
                    <pre className="text-sm font-mono text-green-400/90 leading-relaxed">
                      <code>{generatedSql}</code>
                    </pre>
                  </div>

                  {explanation && (
                    <div className="mt-6 flex gap-4 p-4 bg-[var(--ds-surface-2)] rounded-xl border border-[var(--ds-border)]">
                      <div className="mt-1 text-brand">
                        <CheckCircle2 size={16} />
                      </div>
                      <div>
                        <p className="ds-caption font-bold text-[var(--ds-text)] uppercase tracking-wider mb-1">Execution Plan</p>
                        <p className="text-[13px] text-[var(--ds-text-muted)] leading-relaxed">{explanation}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Results Table */}
                {results && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="ds-card overflow-hidden"
                  >
                    <div className="p-6 border-b border-[var(--ds-border)] flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand/10 rounded-lg text-brand">
                          <LayoutDashboard size={18} />
                        </div>
                        <h3 className="ds-heading-sm text-[var(--ds-text)]">Dataset Results</h3>
                        <span className="px-2 py-0.5 bg-[var(--ds-surface-3)] rounded text-[10px] font-bold text-[var(--ds-text-faint)]">
                          {results.row_count} ROWS
                        </span>
                      </div>
                      <button 
                        onClick={downloadCSV}
                        className="flex items-center gap-2 text-[var(--ds-text-faint)] hover:text-[var(--ds-text)] transition-colors ds-caption font-bold uppercase"
                      >
                        <Download size={16} />
                        Export CSV
                      </button>
                    </div>
                    
                    <div className="overflow-x-auto custom-scrollbar max-h-[500px]">
                      {results.results.length > 0 ? (
                        <table className="w-full text-left border-collapse">
                          <thead className="sticky top-0 z-10">
                            <tr className="bg-[var(--ds-surface-2)] border-b border-[var(--ds-border)]">
                              {Object.keys(results.results[0]).map(key => (
                                <th key={key} className="px-6 py-4 text-[10px] font-bold text-[var(--ds-text-faint)] uppercase tracking-widest">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {results.results.map((row, i) => (
                              <tr key={i} className="border-b border-[var(--ds-border)] hover:bg-white/[0.02] transition-colors">
                                {Object.values(row).map((val, j) => (
                                  <td key={j} className="px-6 py-4 text-sm text-[var(--ds-text-muted)] whitespace-nowrap font-mono">
                                    {val === null ? <span className="italic opacity-50">null</span> : String(val)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <div className="p-12 text-center text-[var(--ds-text-faint)]">
                          No records found for this query.
                        </div>
                      )}
                    </div>
                    
                    {results.optimization_suggestion && (
                      <div className="p-4 bg-brand/5 border-t border-[var(--ds-border)] flex gap-3">
                        <Zap size={16} className="text-brand mt-1 shrink-0" />
                        <div>
                          <p className="text-[11px] font-bold text-brand uppercase tracking-wider mb-0.5">Performance Insight</p>
                          <p className="text-xs text-[var(--ds-text-muted)] italic">"{results.optimization_suggestion}"</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar Panel */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="ds-card p-6"
          >
            <h4 className="ds-label mb-6 text-brand">GetLicense DB Insights</h4>
            <div className="space-y-3">
              {getlicenseQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setNlQuery(q.query)}
                  className="w-full text-left p-3 rounded-xl border border-[var(--ds-border)] bg-[var(--ds-surface-2)] hover:border-brand/40 hover:bg-brand/5 transition-all group"
                >
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-lg">{q.icon}</span>
                    <span className="text-[11px] font-bold text-[var(--ds-text)] uppercase tracking-wider">{q.label}</span>
                  </div>
                  <p className="text-[10px] text-[var(--ds-text-muted)] leading-tight line-clamp-2 group-hover:text-[var(--ds-text)]">
                    {q.query}
                  </p>
                </button>
              ))}
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
