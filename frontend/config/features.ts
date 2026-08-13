export const featureFlags = {
  landingMockDemo: false,
  auth: !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
} as const;
