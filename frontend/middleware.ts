import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/about(.*)",
  "/pricing(.*)",
  "/blog(.*)",
  "/docs(.*)",
  "/api(.*)",
  "/_next(.*)",
  "/favicon.ico",
  "/og.png",
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|og.png).*)",
  ],
};
