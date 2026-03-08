import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="bg-gray-900 text-white shadow-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="shrink-0">
            <Link to="/" className="text-xl font-bold bg-linear-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">Agridesk</Link>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {user.role === 'MAHASISWA' && (
                <>
                  <Link to="/" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Surat Saya</Link>
                  <Link to="/surat/new" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Buat Surat</Link>
                  <Link to="/signature/me" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Tanda Tangan</Link>
                </>
              )}
              {user.role === 'DOSEN' && (
                <>
                  <Link to="/" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Pending TTD</Link>
                  <Link to="/surat/all-dosen" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Semua Surat</Link>
                  <Link to="/signature/me" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Tanda Tangan</Link>
                </>
              )}
              {user.role === 'ADMIN' && (
                <>
                  <Link to="/" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Pending Admin</Link>
                  <Link to="/surat/all" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Semua Surat</Link>
                  <Link to="/signature/me" className="hover:bg-gray-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">Tanda Tangan</Link>
                </>
              )}
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-300">{user.name} <span className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded-full">{user.role}</span></span>
            <button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-md text-sm font-medium transition-colors shadow">Logout</button>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none">
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-gray-800">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {user.role === 'MAHASISWA' && (
              <>
                <Link to="/" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Surat Saya</Link>
                <Link to="/surat/new" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Buat Surat</Link>
                <Link to="/signature/me" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Tanda Tangan</Link>
              </>
            )}
            {user.role === 'DOSEN' && (
              <>
                <Link to="/" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Pending TTD</Link>
                <Link to="/surat/all-dosen" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Semua Surat</Link>
                <Link to="/signature/me" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Tanda Tangan</Link>
              </>
            )}
            {user.role === 'ADMIN' && (
              <>
                <Link to="/" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Pending Admin</Link>
                <Link to="/surat/all" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Semua Surat</Link>
                <Link to="/signature/me" onClick={() => setIsOpen(false)} className="hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium">Tanda Tangan</Link>
              </>
            )}
            <div className="mt-4 pt-4 border-t border-gray-700 px-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-white">{user.name} <span className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded-full ml-2">{user.role}</span></span>
                <button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors">Logout</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
