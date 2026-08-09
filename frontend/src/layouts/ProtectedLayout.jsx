import { Outlet } from "react-router-dom";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import DashboardLayout from "./DashboardLayout";

export default function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <Outlet />
      </DashboardLayout>
    </ProtectedRoute>
  );
}