import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import EmployeeDashboard from "./pages/EmployeeDashboard";
import LoginPage from "./pages/LoginPage";
import TeamleadDashboard from "./pages/TeamleadDashboard";

function ProtectedRoute({
  children,
  role,
}: {
  children: React.ReactNode;
  role?: "TEAMLEAD" | "EMPLOYEE";
}) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="app-layout">Загрузка...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to={user.role === "TEAMLEAD" ? "/teamlead" : "/employee"} replace />;
  }
  return <>{children}</>;
}

export default function App() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="app-layout">Загрузка...</div>;
  }

  return (
    <Routes>
      <Route
        path="/"
        element={
          user ? (
            <Navigate to={user.role === "TEAMLEAD" ? "/teamlead" : "/employee"} replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/teamlead"
        element={
          <ProtectedRoute role="TEAMLEAD">
            <TeamleadDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee"
        element={
          <ProtectedRoute role="EMPLOYEE">
            <EmployeeDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
