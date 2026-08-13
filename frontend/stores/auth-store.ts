"use client";

import { useUser, useAuth } from "@clerk/nextjs";

export function useSyncAuthStore() {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();

  return {
    isLoaded,
    isSignedIn: !!isSignedIn,
    user,
    userInitials: user
      ? `${user.firstName?.charAt(0) ?? ""}${user.lastName?.charAt(0) ?? ""}`
          .toUpperCase() || user.emailAddresses[0]?.emailAddress.charAt(0).toUpperCase()
      : "?",
  };
}
