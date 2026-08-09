import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

import QueryProvider from "./providers/QueryProvider";
import { AuthProvider } from "./context/AuthContext";
import ErrorBoundary from "./components/common/ErrorBoundary";

import { Toaster } from "sonner";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryProvider>
        <AuthProvider>

          <App />

          <Toaster
            position="top-right"
            richColors
            closeButton
            duration={3000}
          />

        </AuthProvider>
      </QueryProvider>
    </ErrorBoundary>
  </React.StrictMode>
);