import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getCurrentUser } from "aws-amplify/auth";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import LandingPage from "./pages/marketing/LandingPage";
import PricingPage from "./pages/marketing/PricingPage";
import OnboardingPage from "./pages/OnboardingPage";
import AdminPortal from "./pages/admin/AdminPortal";
import HelpCenter from "./components/onboarding/HelpCenter";
import OnboardingChecklist from "./components/onboarding/OnboardingChecklist";
import "./services/auth";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [authed, setAuthed] = useState<boolean | null>(null);
  useEffect(() => {
    getCurrentUser().then(() => setAuthed(true)).catch(() => setAuthed(false));
  }, []);
  if (authed === null) return <div className="loading">Loading...</div>;
  return authed ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"           element={<LandingPage />} />
        <Route path="/login"      element={<Login />} />
        <Route path="/pricing"    element={<PricingPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/dashboard"  element={
          <ProtectedRoute>
            <>
              <Dashboard />
              <OnboardingChecklist />
              <HelpCenter />
            </>
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute>
            <AdminPortal />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
