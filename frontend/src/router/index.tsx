import { Navigate, Outlet, createBrowserRouter, useLocation } from "react-router-dom";

import AppLayout from "@/components/layout/AppLayout";
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import DatasetsPage from "@/pages/DatasetsPage";
import DatasetDetailPage from "@/pages/DatasetDetailPage";
import TrainingRunsPage from "@/pages/TrainingRunsPage";
import TrainingRunDetailPage from "@/pages/TrainingRunDetailPage";
import NewTrainingRunPage from "@/pages/NewTrainingRunPage";
import AIAssistantInfoPage from "@/pages/AIAssistantInfoPage";
import { useAuth } from "@/hooks/useAuth";

const ProtectedOutlet = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="card">Checking PulseML session...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
};

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/",
    element: <ProtectedOutlet />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "datasets", element: <DatasetsPage /> },
      { path: "datasets/:id", element: <DatasetDetailPage /> },
      { path: "training-runs", element: <TrainingRunsPage /> },
      { path: "training-runs/:id", element: <TrainingRunDetailPage /> },
      { path: "training/new", element: <NewTrainingRunPage /> },
      { path: "ai-assistant", element: <AIAssistantInfoPage /> },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/dashboard" replace />,
  },
]);


