"use client";

import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { useEffect, type ReactNode } from "react";

import { setTokenProvider } from "@/services/api-client";

function AuthTokenInitializer({ children }: { children: ReactNode }) {
  const { getToken } = useAuth();

  useEffect(() => {
    setTokenProvider(() => getToken({ template: undefined }));
  }, [getToken]);

  return <>{children}</>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  return (
    <ClerkProvider>
      <AuthTokenInitializer>{children}</AuthTokenInitializer>
    </ClerkProvider>
  );
}
