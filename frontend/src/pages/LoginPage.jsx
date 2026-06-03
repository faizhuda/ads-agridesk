import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/error';
import api from '../api';
import { ShieldCheck, Clock, FileCheck, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ dokumen_terbit: 0, tanda_tangan: 0, rata_rata_jam: 0 });

  useEffect(() => {
    // Fetch real stats
    api.get('/api/surat/public/stats')
      .then(res => setStats(res.data))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.toLowerCase().endsWith('@apps.ipb.ac.id')) {
      const errorMsg = 'Silakan gunakan email institusi IPB yang valid (@apps.ipb.ac.id) untuk masuk.';
      setError(errorMsg);
      toast.error('Domain email tidak valid!');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(getErrorMessage(err, 'Login gagal. Periksa kembali kredensial Anda.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-ivory text-primary font-sans">
      {/* Header Panel */}
      <header className="flex justify-between items-center p-6 lg:px-12 border-b border-sepia-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary text-white flex items-center justify-center font-serif text-lg font-bold rounded-sm">A</div>
          <div>
            <h1 className="font-serif font-bold text-lg leading-none">Agridesk</h1>
            <p className="text-[10px] tracking-widest text-primary/60 mt-0.5 uppercase">Ilmu Komputer</p>
          </div>
        </div>
        <div className="text-xs sm:text-sm text-primary/70 text-right">
          <span className="hidden sm:inline">Belum memiliki akun? </span>
          <Link to="/register" className="font-medium text-primary hover:text-primary-dark underline underline-offset-4 decoration-primary/30">
            Daftar di sini
          </Link>
        </div>
      </header>

      {/* Content Wrapper */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Left Panel - Stats & Branding */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center p-8 sm:p-12 lg:p-24 border-b lg:border-b-0 lg:border-r border-sepia-200 order-2 lg:order-1">
          <div className="max-w-md mx-auto lg:mx-0">
            <p className="text-xs tracking-widest text-primary/50 uppercase mb-8 hidden lg:block">Jilid 01 &middot; 2026</p>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-serif leading-tight mb-4 lg:mb-6">
              Setiap lembar surat,<br />
              <span className="italic">dirawat</span> dengan tertib.
            </h2>
            <p className="text-sm leading-relaxed text-primary/80 mb-8 lg:mb-12">
              Platform tata kelola surat internal Ilmu Komputer. Dari pengajuan mahasiswa, disposisi dosen, hingga tanda tangan kaprodi dalam satu alur yang terukur.
            </p>

            <div className="grid grid-cols-3 gap-4 sm:gap-8 mt-12">
              <div>
                <p className="text-[10px] tracking-widest text-primary/50 uppercase mb-2">Surat Diterbitkan</p>
                <p className="text-2xl sm:text-3xl font-serif">{stats.dokumen_terbit.toLocaleString('id-ID')}</p>
              </div>
              <div>
                <p className="text-[10px] tracking-widest text-primary/50 uppercase mb-2">Tanda Tangan Digital</p>
                <p className="text-2xl sm:text-3xl font-serif">{stats.tanda_tangan.toLocaleString('id-ID')}</p>
              </div>
              <div>
                <p className="text-[10px] tracking-widest text-primary/50 uppercase mb-2">Rata-rata Waktu</p>
                <p className="text-2xl sm:text-3xl font-serif">{stats.rata_rata_jam.toLocaleString('id-ID')}<span className="text-xs sm:text-sm font-sans text-primary/60 ml-1">jam</span></p>
              </div>
            </div>

            <div className="mt-12 hidden lg:block">
              <p className="text-xs italic text-primary/60">
                "Ketertiban administrasi adalah bentuk paling sunyi dari pelayanan." <br />
                <span className="not-italic opacity-75">— Adalah Pokoknya</span>
              </p>
            </div>
          </div>
        </div>

        {/* Right Panel - Login Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center p-8 sm:p-12 lg:p-24 bg-ivory order-1 lg:order-2">
          <div className="w-full max-w-sm mx-auto">
            <p className="text-[10px] tracking-widest text-primary/50 uppercase mb-4">Masuk &middot; Sesi Pengguna</p>
            <h2 className="text-3xl sm:text-4xl font-serif mb-4">Selamat datang kembali.</h2>
            <p className="text-sm text-primary/70 mb-8">
              Gunakan akun Anda untuk melanjutkan.
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50/50 border border-red-200 text-red-700 px-4 py-3 text-sm rounded-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs tracking-widest text-primary/60 uppercase mb-2">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-white/50 border border-sepia-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-sm transition-colors text-sm"
                  placeholder="nama@apps.ipb.ac.id"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-xs tracking-widest text-primary/60 uppercase">
                    Kata Sandi
                  </label>
                  <p className="text-xs text-primary/40">Lupa? Hubungi administrator prodi.</p>
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-white/50 border border-sepia-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-sm transition-colors text-sm"
                  placeholder="••••••••"
                />
              </div>

              <div className="pt-4 space-y-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 bg-primary text-white text-sm font-medium hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-ivory rounded-sm transition-all disabled:opacity-70"
                >
                  {loading ? 'Memproses...' : 'Masuk ke Beranda'}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/verify')}
                  className="w-full py-3 px-4 bg-white border border-sepia-200 text-primary text-sm font-medium hover:bg-sepia-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-ivory rounded-sm transition-all flex justify-center items-center gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                  Verifikasi Dokumen / Tanda Tangan
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
