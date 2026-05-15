import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  Table as TableIcon, 
  Columns, 
  ChevronRight, 
  Search, 
  RefreshCw,
  Box,
  Hash,
  Type,
  Calendar,
  Lock
} from 'lucide-react';

const DatabaseExplorerPage = () => {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDatabases();
  }, []);

  const fetchDatabases = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/databases`);
      const data = await response.json();
      if (response.ok) {
        setDatabases(data.databases || []);
      } else {
        setError(data.error || 'Failed to fetch databases');
      }
    } catch (err) {
      setError('Connection failed');
    } finally {
      setLoading(false);
    }
  };

  const fetchTables = async (dbName) => {
    setSelectedDb(dbName);
    setSelectedTable(null);
    setTables([]);
    setColumns([]);
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/databases/${dbName}/tables`);
      const data = await response.json();
      if (response.ok) {
        setTables(data.tables || []);
      } else {
        setError(data.error || 'Failed to fetch tables');
      }
    } catch (err) {
      setError('Connection failed');
    } finally {
      setLoading(false);
    }
  };

  const fetchColumns = async (tableName) => {
    setSelectedTable(tableName);
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/tables/${tableName}/columns?database=${selectedDb}`);
      const data = await response.json();
      if (response.ok) {
        setColumns(data.columns || []);
      } else {
        setError(data.error || 'Failed to fetch columns');
      }
    } catch (err) {
      setError('Connection failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div>
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3 mb-3"
        >
          <div className="ds-brand-line" />
          <span className="ds-label-brand">Infrastructure</span>
        </motion.div>
        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="ds-heading-lg text-[var(--ds-text)]"
        >
          Database Explorer
        </motion.h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Databases List */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="ds-card flex flex-col h-[600px]"
        >
          <div className="p-4 border-b border-[var(--ds-border)] flex items-center justify-between">
            <div className="flex items-center gap-2 text-brand">
              <Database size={18} />
              <span className="ds-label text-xs">Databases</span>
            </div>
            <button 
              onClick={fetchDatabases}
              className="p-1.5 hover:bg-[var(--ds-surface-3)] rounded-lg transition-colors text-[var(--ds-text-faint)]"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
            {databases.map(db => (
              <button
                key={db}
                onClick={() => fetchTables(db)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left mb-1
                  ${selectedDb === db 
                    ? 'bg-brand/10 text-brand border border-brand/20' 
                    : 'text-[var(--ds-text-muted)] hover:bg-[var(--ds-surface-2)] hover:text-[var(--ds-text)] border border-transparent'}`}
              >
                <Database size={16} className={selectedDb === db ? 'text-brand' : 'text-[var(--ds-text-faint)]'} />
                <span className="text-sm font-medium">{db}</span>
                {selectedDb === db && <ChevronRight size={14} className="ml-auto" />}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Tables List */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="ds-card flex flex-col h-[600px]"
        >
          <div className="p-4 border-b border-[var(--ds-border)] flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-400">
              <TableIcon size={18} />
              <span className="ds-label text-xs">Tables</span>
            </div>
            <span className="text-[10px] font-bold text-[var(--ds-text-faint)] uppercase">
              {tables.length} Total
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
            {!selectedDb ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <Box size={40} className="text-[var(--ds-text-faint)] mb-4" />
                <p className="text-sm text-[var(--ds-text-faint)]">Select a database to view its tables</p>
              </div>
            ) : (
              tables.map(table => (
                <button
                  key={table}
                  onClick={() => fetchColumns(table)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left mb-1
                    ${selectedTable === table 
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' 
                      : 'text-[var(--ds-text-muted)] hover:bg-[var(--ds-surface-2)] hover:text-[var(--ds-text)] border border-transparent'}`}
                >
                  <TableIcon size={16} className={selectedTable === table ? 'text-blue-400' : 'text-[var(--ds-text-faint)]'} />
                  <span className="text-sm font-medium">{table}</span>
                  {selectedTable === table && <ChevronRight size={14} className="ml-auto" />}
                </button>
              ))
            )}
          </div>
        </motion.div>

        {/* Columns List */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="ds-card flex flex-col h-[600px]"
        >
          <div className="p-4 border-b border-[var(--ds-border)] flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-400">
              <Columns size={18} />
              <span className="ds-label text-xs">Columns</span>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            {!selectedTable ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <Columns size={40} className="text-[var(--ds-text-faint)] mb-4" />
                <p className="text-sm text-[var(--ds-text-faint)]">Select a table to view its structure</p>
              </div>
            ) : (
              <div className="space-y-3">
                {columns.map(col => (
                  <div 
                    key={col}
                    className="flex items-center justify-between p-3 bg-[var(--ds-surface-2)] border border-[var(--ds-border)] rounded-lg group hover:border-green-500/30 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-[var(--ds-surface-3)] rounded text-[var(--ds-text-faint)] group-hover:text-green-400 transition-colors">
                        <Type size={14} />
                      </div>
                      <span className="text-sm font-medium text-[var(--ds-text)]">{col}</span>
                    </div>
                    {col.includes('id') && (
                      <span className="text-[9px] font-bold bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded uppercase">PK</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DatabaseExplorerPage;
