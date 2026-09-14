import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, LogIn, Lock, AlertCircle } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('david.odigie');
  const [password, setPassword] = useState('Icanbuild2026');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', { credentials: 'include', 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Login failed');
      }
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neo-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md neo-card bg-neo-yellow p-8">
        <div className="text-center mb-8 bg-white border-neo border-neo-border p-6 rounded-neo shadow-neo transform -rotate-1">
          <ShieldAlert className="w-16 h-16 text-neo-primary mx-auto mb-4" />
          <h1 className="text-3xl font-black tracking-tight text-neo-text">Daily BRIEF</h1>
          <p className="font-bold text-gray-600 mt-2">Security Operations Center</p>
        </div>

        {error && (
          <div className="bg-neo-accent text-white p-3 rounded-neo border-neo border-neo-border shadow-neo mb-6 font-bold flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-neo-text mb-2">Email / Username</label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="neo-input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-neo-text mb-2">Password</label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="neo-input pl-10"
                required
              />
              <Lock className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full neo-btn flex justify-center items-center gap-2 py-3 text-lg"
          >
            {loading ? 'Authenticating...' : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
