import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Lock, ArrowRight, Sun, Moon, AlertCircle, Loader2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const { theme, toggleTheme } = useTheme();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const containerVariants = {
    initial: { opacity: 0, y: 24 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.7,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(email, password);
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[var(--ds-bg)] overflow-hidden relative">
      {/* Theme Toggle */}
      <button 
        onClick={toggleTheme}
        className="fixed top-6 right-6 z-50 p-3 rounded-full bg-[var(--ds-surface-2)] border border-[var(--ds-border)] text-[var(--ds-text)] hover:text-brand transition-all shadow-lg"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      {/* Left Panel: Architectural Grid & Brand Presence */}
      <div className="hidden lg:flex flex-1 relative ds-grid-bg items-center justify-center border-r border-[var(--ds-border)]">
        <div className="absolute inset-0 bg-radial-gradient(ellipse at 20% 50%, var(--ds-ambient-color) 0%, transparent 65%) pointer-events-none" />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="z-10 text-center"
        >
          <img 
            src={theme === 'dark' ? "/assets/logo-white.svg" : "/assets/logo.svg"} 
            alt="Aeologic" 
            className="h-24 w-auto object-contain mx-auto mb-6" 
          />
          <h1 className="ds-heading-md text-[var(--ds-text)] uppercase tracking-widest">
            AI SQL Query Generator
          </h1>
        </motion.div>

        {/* Scan line effect */}
        <motion.div 
          animate={{ top: ['0%', '100%', '0%'] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
          className="absolute left-0 w-full h-[1px] bg-[rgba(198,32,8,0.15)] shadow-[0_0_15px_rgba(198,32,8,0.5)] z-0"
        />
      </div>

      {/* Right Panel: Login Form */}
      <div className="w-full lg:w-[500px] flex flex-col justify-center px-8 sm:px-16 lg:px-20 bg-[var(--ds-bg)] relative z-10">
        <motion.div
          variants={containerVariants}
          initial="initial"
          animate="animate"
          className="w-full max-w-sm mx-auto"
        >
          <motion.div variants={itemVariants} className="flex items-center gap-3 mb-5">
            <div className="ds-brand-line" />
            <span className="ds-label-brand">Auth Portal</span>
          </motion.div>

          <motion.h1 variants={itemVariants} className="ds-heading-lg text-[var(--ds-text)] mb-2">
            Secure Entry
          </motion.h1>
          <motion.p variants={itemVariants} className="ds-body text-[var(--ds-text-muted)] mb-6">
            Welcome back. Please authenticate to access the command center.
          </motion.p>

          {error && (
            <motion.div 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6 p-4 bg-brand/10 border border-brand/20 rounded-lg flex items-center gap-3 text-brand text-[13px] font-medium"
            >
              <AlertCircle size={16} />
              {error}
            </motion.div>
          )}

          <form onSubmit={handleLogin} className="space-y-8">
            <motion.div variants={itemVariants} className="ds-input-wrap">
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                className="ds-input-line pl-0 uppercase text-[10.5px] tracking-[0.14em] font-semibold"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </motion.div>

            <motion.div variants={itemVariants} className="ds-input-wrap">
              <input
                type="password"
                placeholder="ACCESS KEY"
                className="ds-input-line pl-0 uppercase text-[10.5px] tracking-[0.14em] font-semibold"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </motion.div>

            <motion.div variants={itemVariants} className="pt-4">
              <button 
                type="submit" 
                disabled={isLoading}
                className="ds-btn-primary w-full group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    AUTHENTICATE
                    <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </motion.div>
          </form>

          <motion.div variants={itemVariants} className="mt-12 text-center">
            <p className="ds-caption text-[var(--ds-text-faint)]">
              Authorized personnel only. All access is logged and monitored.
            </p>
          </motion.div>
        </motion.div>
      </div>

      {/* Atmospheric Ambient Glow */}
      <div className="fixed top-0 right-0 w-1/3 h-full bg-radial-gradient(ellipse at 80% 50%, rgba(198,32,8,0.03) 0%, transparent 60%) pointer-events-none z-0" />
    </div>
  );
};

export default LoginPage;
