import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { lazy, Suspense } from 'react';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import MahasiswaDashboard from './pages/MahasiswaDashboard';
import DosenDashboard from './pages/DosenDashboard';
import DosenAllSuratPage from './pages/DosenAllSuratPage';
import AdminDashboard from './pages/AdminDashboard';
import AllSuratPage from './pages/AllSuratPage';
import AuditLogPage from './pages/AuditLogPage';
import CreateSuratPage from './pages/CreateSuratPage';
import SuratDetailPage from './pages/SuratDetailPage';
import SignatureProfilePage from './pages/SignatureProfilePage';
import PdfViewerPage from './pages/PdfViewerPage';
import './index.css';

// Lazy load VerifyPage to isolate framer-motion initialization in its own chunk
const VerifyPage = lazy(() => import('./pages/VerifyPage'));
// Lazy load ExternalUploadWizardPage to isolate react-pdf/pdfjs-dist TDZ crash
const ExternalUploadWizardPage = lazy(() => import('./pages/ExternalUploadWizardPage'));

export default function App() {
  return (
    <AuthProvider>
      <Toaster position="top-center" richColors theme="light" closeButton offset="80px" />
      <BrowserRouter>
        <div className="min-h-screen bg-ivory flex flex-col">
          <Navbar />
          <main className="flex-1 w-full flex flex-col">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify/:hash?" element={
              <Suspense fallback={<div className="flex justify-center items-center h-64 text-primary/50 text-sm">Memuat...</div>}>
                <VerifyPage />
              </Suspense>
            } />
            <Route path="/verify-sig/:hash?" element={
              <Suspense fallback={<div className="flex justify-center items-center h-64 text-primary/50 text-sm">Memuat...</div>}>
                <VerifyPage />
              </Suspense>
            } />

            <Route path="/" element={<HomePage />} />

            <Route path="/dashboard/mahasiswa" element={
              <ProtectedRoute roles={['MAHASISWA']}><MahasiswaDashboard /></ProtectedRoute>
            } />
            <Route path="/dashboard/dosen" element={
              <ProtectedRoute roles={['DOSEN']}><DosenDashboard /></ProtectedRoute>
            } />
            <Route path="/surat/all-dosen" element={
              <ProtectedRoute roles={['DOSEN']}><DosenAllSuratPage /></ProtectedRoute>
            } />
            <Route path="/dashboard/admin" element={
              <ProtectedRoute roles={['ADMIN']}><AdminDashboard /></ProtectedRoute>
            } />

            <Route path="/surat/new" element={
              <ProtectedRoute roles={['MAHASISWA']}><CreateSuratPage /></ProtectedRoute>
            } />
            <Route path="/surat/new/external" element={
              <ProtectedRoute roles={['MAHASISWA']}>
                <Suspense fallback={<div className="flex justify-center items-center h-64 text-primary/50 text-sm">Memuat...</div>}>
                  <ExternalUploadWizardPage />
                </Suspense>
              </ProtectedRoute>
            } />
            <Route path="/signature/me" element={
              <ProtectedRoute><SignatureProfilePage /></ProtectedRoute>
            } />
            <Route path="/admin/surat" element={
              <ProtectedRoute roles={['ADMIN']}><AllSuratPage /></ProtectedRoute>
            } />
            <Route path="/surat/all" element={
              <ProtectedRoute roles={['ADMIN']}><AllSuratPage /></ProtectedRoute>
            } />
            <Route path="/admin/audit-logs" element={
              <ProtectedRoute roles={['ADMIN']}><AuditLogPage /></ProtectedRoute>
            } />
            <Route path="/surat/:id" element={
              <ProtectedRoute><SuratDetailPage /></ProtectedRoute>
            } />
            <Route path="/surat/:id/pdf" element={
              <ProtectedRoute><PdfViewerPage /></ProtectedRoute>
            } />
          </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
