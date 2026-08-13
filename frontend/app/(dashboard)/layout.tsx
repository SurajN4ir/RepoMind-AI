import type { ReactNode } from "react";

import { AppSidebar } from "@/components/system/app-sidebar";
import { AppTopbar } from "@/components/system/app-topbar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <div className="flex flex-1 flex-col">
        <AppTopbar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
