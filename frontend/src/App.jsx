import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { lazy, Suspense } from 'react';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';

// Lazy load all pages to isolate circular dependency TDZ crashes
// (pdfjs-dist, react-dropzone, framer-motion all have init order issues with Vite 5 + React 19)
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const HomePage = lazy(() => import('./pages/HomePage'));
const MahasiswaDashboard = lazy(() => import('./pages/MahasiswaDashboard'));
const DosenDashboard = lazy(() => import('./pages/DosenDashboard'));
const DosenAllSuratPage = lazy(() => import('./pages/DosenAllSuratPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const AllSuratPage = lazy(() => import('./pages/AllSuratPage'));
const AuditLogPage = lazy(() => import('./pages/AuditLogPage'));
const CreateSuratPage = lazy(() => import('./pages/CreateSuratPage'));
const SuratDetailPage = lazy(() => import('./pages/SuratDetailPage'));
const VerifyPage = lazy(() => import('./pages/VerifyPage'));
const SignatureProfilePage = lazy(() => import('./pages/SignatureProfilePage'));
const PdfViewerPage = lazy(() => import('./pages/PdfViewerPage'));
const ExternalUploadWizardPage = lazy(() => import('./pages/ExternalUploadWizardPage'));

const Loading = () => (
  <div className="flex justify-center items-center h-64 text-primary/50 text-sm">
    Memuat...
  </div>
);

export default function App() {
  return (
    <AuthProvider>
      <Toaster position="top-center" richColors theme="light" closeButton offset="80px" />
      <BrowserRouter>
        <div className="min-h-screen bg-ivory flex flex-col">
          <Navbar />
          <main className="flex-1 w-full flex flex-col">
            <Suspense fallback={<Loading />}>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/verify/:hash?" element={<VerifyPage />} />
                <Route path="/verify-sig/:hash?" element={<VerifyPage />} />
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
                  <ProtectedRoute roles={['MAHASISWA']}><ExternalUploadWizardPage /></ProtectedRoute>
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
            </Suspense>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
