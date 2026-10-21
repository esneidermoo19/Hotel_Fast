import { StrictMode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import App from "./App";
import { TemaProvider } from "./components/layout/TemaProvider";
import { AuthProvider } from "./features/auth/AuthProvider";
import "./index.css";

const clienteConsultas = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

const raiz = document.getElementById("root");

if (!raiz) {
  throw new Error("No se encontro el elemento raiz");
}

createRoot(raiz).render(
  <StrictMode>
    <QueryClientProvider client={clienteConsultas}>
      <BrowserRouter>
        <TemaProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </TemaProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
