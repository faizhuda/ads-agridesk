import React from 'react';

export default class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('Agridesk Error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-ivory flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <h2 className="text-2xl font-serif text-primary mb-3">Terjadi Kesalahan</h2>
            <p className="text-sm text-primary/60 mb-6">
              Halaman tidak dapat dimuat. Silakan muat ulang atau hubungi administrator.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-primary text-white text-sm rounded-sm hover:bg-primary-dark transition-colors"
            >
              Muat Ulang
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
