import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Application Error:", error);
    console.error(errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-[#020817] px-6">
          <div className="w-full max-w-2xl rounded-2xl border border-red-500/30 bg-slate-900 p-8 shadow-xl">
            <h1 className="mb-4 text-3xl font-bold text-red-400">
              Something went wrong
            </h1>

            <p className="mb-6 text-gray-300">
              The application encountered an unexpected error.
            </p>

            <pre className="mb-6 overflow-auto rounded-lg bg-black p-4 text-sm text-red-400">
              {this.state.error?.toString()}
            </pre>

            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white transition hover:bg-blue-700"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;