# RepoMind Frontend Architecture

> Production-grade architecture for an AI-powered repository intelligence platform.
> Next.js 15 App Router · React 19 · TypeScript 5 · Tailwind CSS v3 · Motion · TanStack Query · Zustand · Clerk

---

## Table of Contents

1. [Overall Frontend Architecture](#1-overall-frontend-architecture)
2. [Folder Structure](#2-folder-structure)
3. [Routing Architecture](#3-routing-architecture)
4. [Feature Architecture](#4-feature-architecture)
5. [Component Architecture](#5-component-architecture)
6. [API Layer](#6-api-layer)
7. [State Management](#7-state-management)
8. [Authentication Architecture](#8-authentication-architecture)
9. [Design System Architecture](#9-design-system-architecture)
10. [Motion Architecture](#10-motion-architecture)
11. [Repository Workspace Architecture](#11-repository-workspace-architecture)
12. [User Flows](#12-user-flows)
13. [Responsive Strategy](#13-responsive-strategy)
14. [Accessibility Strategy](#14-accessibility-strategy)
15. [Frontend Implementation Roadmap](#15-frontend-implementation-roadmap)

---

## 1. Overall Frontend Architecture

### Guiding Principles

- **Feature-first, not file-type-first.** Group by domain (chat, repository, graph), not by technical role (components, hooks, utils). Shared primitives live in cross-cutting directories; feature-specific code stays in its feature module.
- **Immutable public API per feature.** Each feature module exports a well-defined set of components, hooks, and types. No feature reaches into another feature's internals.
- **Data flows down, events flow up.** Server state enters through TanStack Query, client state through Zustand, and UI state stays local. Components never fetch directly.
- **Design-system-bound.** Every pixel is accounted for by a design token. No magic values, no ad-hoc colors, no one-off spacing.
- **Progressive enhancement.** The core experience works without JavaScript, with full interactivity layering on top. Motion is additive, never structural.
- **Accessibility is not a sprint.** Keyboard navigation, screen reader support, and reduced-motion respect are built in from the first component, not bolted on later.

### Technology Stack

| Concern | Choice | Rationale |
|---|---|---|
| Framework | Next.js 15 App Router | File-based routing, server components, streaming SSR |
| UI Runtime | React 19 | Server components, use() hook, improved hydration |
| Language | TypeScript 5.7 | Strict mode, no `any`, exhaustive type exports |
| Styling | Tailwind CSS v3 + CSS custom properties | Design token system, zero-runtime CSS, dark mode via class |
| UI Primitives | Radix UI + hand-rolled | Accessible, headless primitives; custom-styled per design tokens |
| Motion | Motion (by Motion One) | Successor to Framer Motion, smaller bundle, same API |
| Complex Animation | Anime.js v4 | Dynamic import only — SVG pipeline animation, connector draws |
| Smooth Scroll | Lenis | RequestAnimationFrame-based smooth scrolling for workspace content |
| Server State | TanStack Query v5 | Caching, deduplication, optimistic updates, streaming |
| Client State | Zustand | Minimal boilerplate, no providers, subscribe outside React |
| Auth | Clerk | Drop-in components, webhook support, session management |
| HTTP | fetch (native) | No Axios dependency — thin typed wrappers |

---

## 2. Folder Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (marketing)/              # Route group — public pages
│   │   ├── page.tsx              # Landing page
│   │   ├── layout.tsx            # Marketing layout (header, footer)
│   │   ├── pricing/
│   │   └── docs/
│   │       └── [...slug]/
│   ├── (auth)/                   # Route group — authentication
│   │   ├── sign-in/
│   │   │   └── [[...sign-in]]/page.tsx
│   │   └── sign-up/
│   │       └── [[...sign-up]]/page.tsx
│   ├── (dashboard)/              # Route group — authenticated app
│   │   ├── layout.tsx            # Dashboard shell (sidebar, topbar)
│   │   ├── page.tsx              # Dashboard home / overview
│   │   ├── repositories/
│   │   │   ├── page.tsx          # Repository list
│   │   │   └── [repositoryId]/
│   │   │       ├── page.tsx      # Repository workspace (redirects to chat)
│   │   │       ├── layout.tsx    # Workspace shell (tabs, breadcrumbs)
│   │   │       ├── chat/
│   │   │       │   └── page.tsx
│   │   │       ├── graph/
│   │   │       │   └── page.tsx
│   │   │       └── settings/
│   │   │           └── page.tsx
│   │   ├── analytics/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   ├── api/                      # Next.js API route proxies
│   │   └── clerk/
│   │       └── webhook/
│   ├── layout.tsx                # Root layout (fonts, providers)
│   └── globals.css               # Design tokens, base styles
│
├── components/                   # Shared design system
│   ├── ui/                       # Primitive components
│   │   ├── button.tsx
│   │   ├── badge.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── select.tsx
│   │   ├── tabs.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── tooltip.tsx
│   │   ├── scroll-area.tsx
│   │   ├── skeleton.tsx
│   │   ├── toast.tsx
│   │   └── index.ts              # Barrel export
│   ├── icons/                    # Icon abstraction layer
│   │   ├── pipeline-icons.tsx    # Pipeline-specific icons
│   │   ├── navigation-icons.tsx  # Nav, header, footer icons
│   │   ├── feature-icons.tsx     # Feature card, comparison icons
│   │   └── provider-icons.tsx    # Git provider logos
│   ├── system/                   # App-shell components
│   │   ├── theme-toggle.tsx
│   │   ├── user-menu.tsx
│   │   ├── app-sidebar.tsx
│   │   ├── app-topbar.tsx
│   │   └── app-footer.tsx
│   └── shared/                   # Composite shared components
│       ├── empty-state.tsx
│       ├── error-boundary.tsx
│       ├── loading-screen.tsx
│       ├── confirm-dialog.tsx
│       └── page-header.tsx
│
├── features/                     # Domain feature modules
│   ├── landing/                  # Marketing landing page
│   │   ├── components/
│   │   │   ├── nav-bar.tsx
│   │   │   └── animated-background.tsx
│   │   ├── sections/
│   │   │   ├── hero-section.tsx
│   │   │   ├── pipeline-section.tsx
│   │   │   ├── features-section.tsx
│   │   │   ├── architecture-section.tsx
│   │   │   ├── why-section.tsx
│   │   │   ├── mock-demo-section.tsx
│   │   │   ├── tech-stack-section.tsx
│   │   │   ├── cta-section.tsx
│   │   │   └── footer-section.tsx
│   │   ├── data/                 # Static content data
│   │   ├── constants/            # Copy, links, labels
│   │   ├── hooks/
│   │   └── index.ts              # Public API — exports LandingPage
│   │
│   ├── chat/                     # AI Chat feature
│   │   ├── components/
│   │   │   ├── chat-input.tsx
│   │   │   ├── chat-message.tsx
│   │   │   ├── chat-thread.tsx
│   │   │   ├── citation-card.tsx
│   │   │   ├── context-panel.tsx
│   │   │   └── streaming-message.tsx
│   │   ├── hooks/
│   │   │   ├── use-chat.ts           # Chat state machine
│   │   │   ├── use-chat-stream.ts    # SSE stream consumer
│   │   │   └── use-chat-history.ts   # TanStack Query
│   │   ├── services/
│   │   │   └── chat-api.ts
│   │   ├── types/
│   │   │   └── chat.ts
│   │   └── index.ts
│   │
│   ├── repositories/             # Repository Management feature
│   │   ├── components/
│   │   │   ├── repository-card.tsx
│   │   │   ├── repository-list.tsx
│   │   │   ├── repository-status-badge.tsx
│   │   │   ├── add-repository-dialog.tsx
│   │   │   ├── repository-settings.tsx
│   │   │   ├── repository-workspace-tabs.tsx
│   │   │   └── indexing-progress.tsx
│   │   ├── hooks/
│   │   │   ├── use-repositories.ts
│   │   │   ├── use-repository.ts
│   │   │   └── use-indexing-status.ts
│   │   ├── services/
│   │   │   └── repository-api.ts
│   │   ├── types/
│   │   │   └── repository.ts
│   │   └── index.ts
│   │
│   ├── graph/                    # Repository Graph feature
│   │   ├── components/
│   │   │   ├── dependency-graph.tsx
│   │   │   ├── graph-node.tsx
│   │   │   ├── graph-edge.tsx
│   │   │   ├── graph-controls.tsx
│   │   │   ├── graph-tooltip.tsx
│   │   │   └── graph-legend.tsx
│   │   ├── hooks/
│   │   │   ├── use-dependency-graph.ts
│   │   │   ├── use-graph-layout.ts
│   │   │   └── use-graph-interaction.ts
│   │   ├── services/
│   │   │   └── graph-api.ts
│   │   ├── types/
│   │   │   └── graph.ts
│   │   └── index.ts
│   │
│   ├── analytics/                # Analytics feature
│   │   ├── components/
│   │   │   ├── analytics-dashboard.tsx
│   │   │   ├── metric-card.tsx
│   │   │   ├── language-chart.tsx
│   │   │   ├── query-trends.tsx
│   │   │   ├── indexing-health.tsx
│   │   │   └── time-range-selector.tsx
│   │   ├── hooks/
│   │   │   ├── use-analytics.ts
│   │   │   └── use-metrics.ts
│   │   ├── services/
│   │   │   └── analytics-api.ts
│   │   ├── types/
│   │   │   └── analytics.ts
│   │   └── index.ts
│   │
│   └── auth/                     # Authentication feature
│       ├── components/
│       │   ├── auth-guard.tsx
│       │   └── onboarding-flow.tsx
│       ├── hooks/
│       │   └── use-auth.ts        # Clerk wrapper
│       ├── services/
│       │   └── auth-api.ts        # Backend user sync
│       └── index.ts
│
├── hooks/                        # Shared React hooks
│   ├── use-scroll-y.ts           # Window scroll position (from animations/)
│   ├── use-in-view.ts            # IntersectionObserver wrapper
│   ├── use-scroll-progress.ts    # Element scroll progress
│   ├── use-media-query.ts        Responsive breakpoint matching
│   ├── use-debounce.ts
│   ├── use-keyboard.ts           # Keyboard shortcut registration
│   └── use-local-storage.ts
│
├── services/                     # API client layer
│   ├── api-client.ts             # Typed fetch wrapper, token injection
│   ├── repositories.ts
│   ├── chat.ts
│   ├── analytics.ts
│   ├── graph.ts
│   └── indexing.ts
│
├── stores/                       # Zustand stores
│   ├── auth-store.ts             # Auth state mirror from Clerk
│   ├── workspace-store.ts        # Active repository, active tab, sidebar
│   ├── theme-store.ts            # Theme preference
│   └── ui-store.ts               # Sidebar state, panel sizes, toasts
│
├── providers/                    # React context providers
│   ├── theme-provider.tsx         # next-themes wrapper
│   ├── query-provider.tsx         # TanStack Query provider
│   ├── auth-provider.tsx          # Clerk provider wrapper
│   └── toast-provider.tsx         # Toast notification provider
│
├── animations/                   # Motion system
│   ├── variants.ts               # Motion variant definitions
│   ├── transitions.ts            # Transition presets
│   ├── motion.ts                 # Motion token constants
│   ├── pipeline.ts               # Anime.js pipeline animation driver
│   └── timeline.ts               # Anime.js timeline helpers
│
├── lib/                          # Pure utilities (no React deps)
│   ├── utils.ts                  # cn(), formatters, validators
│   ├── constants.ts              # App-wide constants
│   ├── navigation.ts             # Nav link definitions
│   └── fetcher.ts                # Base fetch wrapper
│
├── types/                        # Shared TypeScript types
│   ├── common.ts                 # Pagination, API response wrappers
│   ├── repository.ts             # Repository domain types
│   ├── chat.ts                   # Chat domain types
│   ├── graph.ts                  # Graph domain types
│   └── analytics.ts              # Analytics domain types
│
├── config/                       # Static configuration
│   ├── site.ts                   # Site name, URLs, social links
│   ├── features.ts               # Feature flags
│   └── navigation.ts             # Nav link structure, footer groups
│
├── public/                       # Static assets
│   ├── favicon.ico
│   ├── og-image.png
│   ├── logos/
│   └── illustrations/
│
├── middleware.ts                  # Next.js middleware (Clerk auth, redirects)
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── eslint.config.js
└── components.json               # shadcn config (path references TBD)
```

---

## 3. Routing Architecture

### Route Groups

```
/                          → (marketing)  → RootLayout → LandingPage
/pricing                   → (marketing)  → MarketingLayout → PricingPage
/docs/[...slug]            → (marketing)  → MarketingLayout → DocsPage

/sign-in                   → (auth)       → AuthLayout → SignInPage
/sign-up                   → (auth)       → AuthLayout → SignUpPage

/dashboard                 → (dashboard)  → DashboardLayout → DashboardHome
/dashboard/repositories    → (dashboard)  → DashboardLayout → RepositoryListPage
/dashboard/repositories/   → (dashboard)  → DashboardLayout → WorkspaceLayout →
  [repositoryId]                                       │
  [repositoryId]/chat                                  ├── ChatPage
  [repositoryId]/graph                                 ├── GraphPage
  [repositoryId]/code                                  ├── CodeViewerPage
  [repositoryId]/settings                              └── RepositorySettingsPage
/dashboard/analytics       → (dashboard)  → DashboardLayout → AnalyticsPage
/dashboard/settings        → (dashboard)  → DashboardLayout → UserSettingsPage
```

### Layout Hierarchy

```
RootLayout
├── ThemeProvider
├── QueryProvider
├── AuthProvider
│
├── (marketing)/layout.tsx
│   ├── NavBar
│   ├── {children}
│   └── Footer
│
├── (auth)/layout.tsx
│   │   └── {children}           # Centered card layout
│
└── (dashboard)/layout.tsx
    ├── AuthGuard               # Redirects to /sign-in if unauthenticated
    ├── AppSidebar
    ├── AppTopbar
    └── {children}               # Page content with padding
        │
        └── [repositoryId]/layout.tsx
            ├── RepositoryWorkspaceTabs
            └── {children}       # ChatPage | GraphPage | CodePage | SettingsPage
```

### Route Design Decisions

- **`/dashboard` as the authenticated root.** All authenticated pages nest under `/dashboard`. This makes middleware protection straightforward — match `/dashboard/:path*` and check the session.
- **Repository workspace is a nested layout.** The `[repositoryId]` layout renders the workspace chrome (tabs, breadcrumbs, status) while the nested page swaps the content. This avoids re-mounting the workspace shell when switching between Chat, Graph, Code, and Settings.
- **No catch-all workspace page.** Each workspace view gets its own route segment (`/chat`, `/graph`, `/code`, `/settings`). This enables per-route loading states, error boundaries, and metadata.
- **Marketing is a route group.** The landing page, pricing, and docs share a common layout (header, footer) but live outside the `/dashboard` middleware guard.
- **Clerk handles auth routes.** `/sign-in` and `/sign-up` are either Clerk-hosted pages or custom pages using Clerk components. Using Clerk's `[[...sign-in]]` catch-all supports both.

---

## 4. Feature Architecture

### Feature Module Contract

Every feature module at `features/<name>/` adheres to:

```
features/<name>/
├── components/          Feature-specific components (not shared)
├── hooks/               Feature-specific hooks
├── services/            API call functions (thin wrappers)
├── types/               Feature-specific TypeScript types
└── index.ts             Public API barrel export
```

### Rules

- **No downward imports.** Features never import from other features. Shared code lives in `components/`, `hooks/`, `lib/`, or `services/`.
- **Public API only.** `index.ts` exports only the components, hooks, and types that pages and other features are allowed to consume. Internal implementation details stay private.
- **Services are thin.** A feature service file contains typed functions that call `api-client.ts`. They handle request construction and response parsing but never manage state or caching — that's TanStack Query's job.
- **Types are local first.** Types that only one feature uses live in that feature's `types/` directory. Types shared across features (pagination, API response envelope) live in `types/common.ts`.

### Feature Map

| Feature | Responsibility | Key Exports |
|---|---|---|
| `landing` | Marketing site, static content | `LandingPage` |
| `auth` | Auth guard, user sync, onboarding | `AuthGuard`, `useAuth`, `OnboardingFlow` |
| `chat` | AI Q&A, streaming responses, citations | `ChatPage`, `useChat`, `useChatStream` |
| `repositories` | CRUD, indexing status, workspace tabs | `RepositoryList`, `AddRepositoryDialog`, `WorkspaceTabs` |
| `graph` | Dependency visualization, code graph | `DependencyGraph`, `useDependencyGraph` |
| `analytics` | Metrics, charts, health monitoring | `AnalyticsDashboard`, `useAnalytics` |

---

## 5. Component Architecture

### Component Taxonomy

```
components/
├── ui/              Primitive, atomic components (Button, Input, Dialog)
├── icons/           Icon abstraction layer (Lucide wrappers)
├── system/          App-shell components (Sidebar, Topbar, UserMenu)
└── shared/          Composite, cross-feature components (EmptyState, ErrorBoundary)
```

### Classification Rules

| Category | Description | State Management | Examples |
|---|---|---|---|
| **Primitive** | Single-purpose, unstyled or minimally styled, no business logic | None (controlled) | `Button`, `Input`, `Badge`, `Dialog` |
| **Composite** | Multiple primitives, cross-cutting concern, some business logic | Props-driven | `EmptyState`, `ConfirmDialog`, `PageHeader` |
| **System** | App-shell chrome, layout structure | Zustand stores | `AppSidebar`, `AppTopbar`, `ThemeToggle` |
| **Feature** | Domain-specific, feature-internal | Feature hooks + Query | `ChatInput`, `DependencyGraph`, `RepositoryCard` |

### Primitive Component Contract

Every primitive in `components/ui/` follows:

- **`use client`** if it uses React state, effects, or browser APIs
- **Server-component-safe** where possible (pure rendering, no state)
- **`cn()` for class merging** using `tailwind-merge` + `clsx`
- **`forwardRef`** for form controls and focusable elements
- **`asChild` prop** (from Radix Slot) for polymorphic composition where appropriate
- **Accessible by default** — proper `role`, `aria-*`, keyboard navigation built in
- **Exported from `components/ui/index.ts`** as a barrel

---

## 6. API Layer

### Architecture

```
Pages / Components
       │
       ▼
TanStack Query hooks          ← Caching, deduplication, refetching
  features/<name>/hooks/
       │
       ▼
Feature service functions      ← Type-safe request builders
  features/<name>/services/
       │
       ▼
api-client.ts                  ← Base fetch wrapper, token injection
  services/
       │
       ▼
Next.js rewrite proxy          ← /api/* → BACKEND_API_URL/api/*
  next.config.ts
       │
       ▼
FastAPI backend
```

### `api-client.ts` Responsibility

- Creates a typed `fetch` wrapper with:
  - Base URL resolution (uses Next.js rewrite or direct URL)
  - Clerk session token injection via `useAuth().getToken()`
  - JSON content-type headers
  - Error normalization (maps HTTP status codes to typed errors)
  - Request/response type generics
  - AbortController support for cancellation
- No state management, no caching — that is TanStack Query's role

### Service Function Pattern

Every service function:
- Accepts typed parameters
- Returns a typed promise
- Throws typed errors on failure
- Never accesses React hooks or component state

```typescript
// Example: services/repositories.ts
import { apiClient } from "./api-client";
import type { Repository, RepositoryListParams, PaginatedResponse } from "@/types/repository";

export async function listRepositories(
  params: RepositoryListParams,
  signal?: AbortSignal
): Promise<PaginatedResponse<Repository>> {
  return apiClient.get("/repositories", { params, signal });
}
```

### TanStack Query Integration

Query hooks in each feature:
- Use `useQuery` for reads, `useMutation` for writes
- Feature-specific query key factories for cache invalidation
- Optimistic updates for fast UI (repository add/delete)
- `useSuspenseQuery` for routes that need data before render

---

## 7. State Management

### State Ownership

| State Type | Tool | Owner | Examples |
|---|---|---|---|
| **Server state** | TanStack Query | `features/*/hooks/` | Repository list, chat history, analytics data |
| **Client app state** | Zustand | `stores/` | Sidebar open, active repository ID, active tab |
| **Auth state** | Clerk + Zustand mirror | `stores/auth-store.ts` | User object, session status, org membership |
| **UI state** | Local (`useState`) | Component | Form input values, dropdown open, tooltip hover |
| **URL state** | Next.js `useParams`/`useSearchParams` | Page component | Repository ID, page number, search query |
| **Theme state** | `next-themes` | `providers/theme-provider.tsx` | Dark/light mode, system preference |

### Zustand Store Design Principles

- **Single responsibility.** One store per domain concern (`workspace-store.ts`, `ui-store.ts`).
- **No server data in Zustand.** Server state belongs in TanStack Query cache. Zustand holds only client-side UI state.
- **Subscribe outside React.** Zustand supports `store.getState()` for service-layer reads.
- **Actions co-located with state.** Each store exports its own action functions alongside the hook.

### TanStack Query Configuration

- `staleTime: 30_000` (30s) — repositories list
- `staleTime: 5 * 60_000` (5m) — analytics data
- `gcTime: 10 * 60_000` (10m) — garbage collection
- `refetchOnWindowFocus: true` for list views
- `refetchOnWindowFocus: false` for detail views (user expects stale data is fine)
- Query key factory pattern — centralised key definitions per domain

---

## 8. Authentication Architecture

### Flow

```
1. User visits /dashboard/*           → middleware.ts checks Clerk session
2. No session                          → Redirect to /sign-in
3. User signs in via Clerk             → Clerk sets session cookie
4. Clerk webhook hits /api/clerk/webhook → Backend creates/syncs user record
5. User returns to /dashboard/*        → middleware.ts finds session, allows through
6. Client hydrates: AuthProvider reads session → Zustand auth-store updated
7. api-client.ts injects session token → All subsequent API calls authenticated
```

### Middleware

```typescript
// middleware.ts
// - Matches /dashboard/:path* and /api/:path*
// - Uses Clerk's authMiddleware() or clerkClient()
// - Redirects unauthenticated requests to /sign-in
// - Passes through public routes: /, /pricing, /docs/*
// - Adds user ID to request headers for backend correlation
```

### Clerk Integration Points

| Integration | Location | Purpose |
|---|---|---|
| `<ClerkProvider>` | `providers/auth-provider.tsx` | Wraps root layout |
| `authMiddleware()` | `middleware.ts` | Protects dashboard routes |
| `<SignIn />` | `app/(auth)/sign-in/page.tsx` | Sign-in page |
| `<UserButton />` | `components/system/user-menu.tsx` | User menu in topbar |
| `useUser()` | `hooks/use-auth.ts` | Client-side user access |
| `useAuth().getToken()` | `services/api-client.ts` | Token injection |
| Webhook | `app/api/clerk/webhook/route.ts` | User.created → backend sync |

### Auth Store (Zustand)

Mirrors key Clerk state to avoid prop drilling and enable non-React code to check auth:

```typescript
interface AuthState {
  userId: string | null;
  isLoaded: boolean;
  isSignedIn: boolean;
  user: UserResource | null;
}
```

Updated by `AuthProvider` on mount and session change.

---

## 9. Design System Architecture

### Token System

CSS custom properties scoped to `:root` and `.light` (already defined in `globals.css`):

```
:root {                         /* Dark theme (default) */
  --background: 222 38% 7%;     /* Surface colors */
  --foreground: 210 40% 98%;
  --surface: 221 33% 11%;
  --card: 215 31% 15%;
  --primary: 218 100% 65%;      /* Brand colors */
  --accent: 253 91% 67%;
  --success: 142 71% 45%;       /* Semantic colors */
  --warning: 38 92% 50%;
  --danger: 0 84% 60%;
  --muted: 217 19% 20%;         /* Muted / border */
  --muted-foreground: 215 20% 65%;
  --border: 217 22% 22%;
  --ring: 218 100% 65%;
  --radius: 0.75rem;            /* Geometry */
  --font-ui: "Geist", ...;
  --font-code: "Geist Mono", ...;
}
```

Tailwind maps these HSL variables via `tailwind.config.ts` `colors` extension (already done).

### Component Variant Pattern

Every interactive primitive follows a consistent variant schema:

```typescript
type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";
```

Implemented via `class-variance-authority` (CVA) — already used in `Button`.

### Dark/Light Mode

- Dark is default (matches existing `globals.css`)
- Light class on `<html>` triggers `.light` overrides
- `next-themes` `<ThemeProvider attribute="class" defaultTheme="dark">`
- Every component is dark-first — light overrides are additive

### shadcn Compatibility

The `components.json` file stays but no `npx shadcn add` commands will be run. Instead, every primitive is hand-rolled following:
- Radix UI for headless behavior (Dialog, DropdownMenu, Tabs, Tooltip)
- CVA for variant management
- Tailwind for styling
- cn() for class merging

This avoids shadcn's opinionated style decisions while keeping the option to adopt shadcn primitives later if needed.

---

## 10. Motion Architecture

### Library Responsibilities

| Library | Responsibility | Bundle Impact |
|---|---|---|
| **Motion** (by Motion One) | All UI animations — page transitions, hover effects, entrance animations, layout animations, `AnimatePresence` | Always bundled, ~15 kB |
| **Anime.js v4** | Complex timeline animations — pipeline SVG connector draws, sequential node reveals, glow pulses | Dynamic import only, never in initial bundle |
| **Lenis** | Smooth scrolling in workspace content areas, scroll-linked animations | Dynamic import on workspace mount |

### Motion Principles

- **Motion is additive.** No animation is required for core functionality. Every animation enhances but never replaces.
- **`prefers-reduced-motion` respected globally.** All Motion variants check `useReducedMotion()` and return identity variants when active. Anime.js timelines check a module-level flag.
- **Token-based transitions.** Every `transition` and `variant` uses the shared easing `[0.22, 1, 0.36, 1]` from `animations/motion.ts` and `animations/transitions.ts`.
- **Anime.js is async-only.** Imported via dynamic `import("animejs")` inside `useEffect` callbacks. Never included in server components or route-level chunks.
- **Lenis is workspace-only.** Enabled when the user enters a repository workspace. Disabled on marketing pages where native scroll is preferred.

### Animation Ownership

```
animations/
├── variants.ts          # Motion Variants — use in JSX
│                        #   <motion.div variants={fadeInUp} />
│
├── transitions.ts       # Motion Transition presets
│                        #   <motion.div transition={springGentle} />
│
├── motion.ts            # Motion token constants
│                        #   import { motionTokens } ...
│
├── pipeline.ts          # Anime.js — pipeline section animation
│                        #   useEffect(() => runPipelineAnimation(), [])
│
└── timeline.ts          # Anime.js timeline helper factories
```

### Scroll-Related Motion

| Concern | Tool | Location |
|---|---|---|
| Section `whileInView` entrance | Motion | `animations/variants.ts` (fadeInUp, staggerContainer) |
| Scroll-based progress | `useScrollProgress` hook | `hooks/use-scroll-progress.ts` |
| Smooth scroll (workspace) | Lenis | Feature module on mount |
| Nav bar hide/show on scroll | `useScrollY` hook | `hooks/use-scroll-y.ts` |
| Parallax effects | Motion `useScroll` + `useTransform` | Feature module |

---

## 11. Repository Workspace Architecture

### Concept

The Repository Workspace is the primary user-facing environment — a multi-tab, single-repository interface where users explore, query, and understand a codebase.

### Workspace Layout

```
┌─────────────────────────────────────────────┐
│  Topbar                                      │
│  ← Dashboard  │  repo/cli-tool  │  Status: ✓ │
├──────────────┬──────────────────────────────┤
│              │                              │
│  Sidebar     │  Workspace Content            │
│              │                              │
│  Chat        │  (Tab-dependent)              │
│  Graph       │                              │
│  Code        │  ChatPage                     │
│  Settings    │  GraphPage                    │
│              │  CodeViewerPage               │
│              │  SettingsPage                 │
│              │                              │
└──────────────┴──────────────────────────────┘
```

### State (Zustand: `workspace-store.ts`)

```typescript
interface WorkspaceState {
  activeRepositoryId: string | null;
  activeTab: "chat" | "graph" | "code" | "settings";
  sidebarOpen: boolean;
  sidebarWidth: number;        // User-resizable
  setActiveRepository: (id: string) => void;
  setActiveTab: (tab: WorkspaceTab) => void;
  toggleSidebar: () => void;
}
```

### Tab Ownership

| Tab | Page Component | Route | Backend Data |
|---|---|---|---|
| Chat | `features/chat/components/chat-thread.tsx` | `/dashboard/repositories/[id]/chat` | Query pipeline (SSE stream) |
| Graph | `features/graph/components/dependency-graph.tsx` | `/dashboard/repositories/[id]/graph` | Dependency graph API (JSON) |
| Code | (future) | `/dashboard/repositories/[id]/code` | File tree + file content API |
| Settings | `features/repositories/components/repository-settings.tsx` | `/dashboard/repositories/[id]/settings` | Repository CRUD API |

### Workspace Data Flow

```
1. User navigates to /dashboard/repositories/abc123/chat
2. [repositoryId]/layout.tsx:
   a. Reads repositoryId from useParams()
   b. Updates workspace-store activeRepositoryId
   c. Renders WorkspaceTabs + children outlet
3. ChatPage:
   a. useQuery to fetch repository metadata (title, status)
   b. useChat to manage conversation state
   c. useChatStream to consume SSE from /api/repositories/abc123/query/stream
4. User switches to Graph tab (no page reload — Next.js soft navigation)
5. [repositoryId]/layout persists
   GraphPage mounts in the children outlet
```

### Multi-Repository Consideration

The workspace is scoped to one repository at a time. A future cross-repository view can be added as a new tab or a separate dashboard page without changing the workspace architecture.

---

## 12. User Flows

### Flow 1: First Visit → Sign Up → Onboarding

```
Landing Page → "Get Started"
  → /sign-up (Clerk)
  → Clerk webhook creates backend user record
  → Redirect to /dashboard
  → Dashboard shows empty state: "Connect your first repository"
  → "Add Repository" dialog:
      1. Enter Git URL
      2. Select provider (GitHub, GitLab, self-hosted)
      3. Submit → Backend registers repository
      4. Repository appears in list with "indexing" badge
  → User clicks repository → workspace opens on Chat tab
  → Chat shows: "Repository is being indexed. This may take a few minutes."
```

### Flow 2: Query a Repository (Happy Path)

```
User on /dashboard/repositories/abc123/chat
  → Types question in ChatInput
  → ChatInput dispatches to useChat hook
  → useChat POST to /api/repositories/abc123/query (trigger)
  → Backend returns 202 Accepted with query ID
  → Client opens SSE connection to /api/repositories/abc123/query/stream?id=<queryId>
  → StreamingMessage component renders text word-by-word
  → Citation cards appear as they are resolved
  → Completed message shows full answer with file citations
  → User can click citation → opens file in Code tab (future)
```

### Flow 3: Explore Repository Dependencies

```
User on /dashboard/repositories/abc123/graph
  → DependencyGraph mounts
  → useDependencyGraph fires useQuery to fetch dependency data
  → Graph renders with force-directed layout (D3.js or similar)
  → User can:
      - Pan/zoom the graph
      - Click a node → tooltip with file info
      - Double-click a node → zoom to its dependencies
      - Filter by layer (API, domain, infrastructure)
      - Search for a specific module
  → User can switch back to Chat with the graph context preserved
```

### Flow 4: Monitor Analytics

```
User navigates to /dashboard/analytics
  → AnalyticsDashboard mounts
  → useAnalytics fires parallel queries:
      - Total repositories indexed
      - Query volume (daily/weekly/monthly)
      - Average response time
      - Top languages
      - Indexing health (success rate, failed repos)
  → Each metric is displayed in a MetricCard with sparkline
  → TimeRangeSelector controls the query window
  → Data refreshes automatically every 5 minutes
```

---

## 13. Responsive Strategy

### Breakpoints

| Name | Width | Target |
|---|---|---|
| `xs` | 480px | Small phones |
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small desktops |
| `xl` | 1280px | Standard desktops |
| `2xl` | 1536px | Large desktops |

### Adaptive Layout Rules

| Viewport | Sidebar | Workspace | Chat Panel |
|---|---|---|---|
| ≥1280px | Persistent, 280px | Full remaining | Side-by-side with citations |
| 768–1279px | Collapsible (toggle) | Full width | Citations in bottom drawer |
| <768px | Hidden (overlay drawer) | Full width | Chat full-screen, citations in slide-over |

### Component Responsiveness

- **Primitives**: No breakpoint logic — the layout system controls responsive behavior
- **System components**: `AppSidebar` uses `md:` breakpoints to toggle between persistent and overlay modes
- **Feature components**: `RepositoryCard` switches from row layout (desktop) to stacked layout (mobile) via container queries where supported, fallback to media queries
- **Graph**: Dedicated mobile view with simplified layout, pinch-to-zoom, single-tap node selection
- **Analytics charts**: Responsive SVG with `viewBox` — scales to container width

---

## 14. Accessibility Strategy

### Standard

- **WCAG 2.2 AA** compliance target
- Automated checks via `eslint-plugin-jsx-a11y` in CI
- Manual checks: keyboard-only navigation, screen reader (VoiceOver, NVDA), zoom to 200%

### Baseline Requirements

Every component must:

1. **Be keyboard navigable.** All interactive elements reachable via `Tab`, activatable via `Enter`/`Space`. No mouse-only interactions.
2. **Have visible focus indicators.** `:focus-visible` ring (already in `globals.css`). Never `outline: none` without a replacement.
3. **Include accessible labels.** `aria-label`, `aria-labelledby`, or visible `<label>` for every interactive element.
4. **Support reduced motion.** `prefers-reduced-motion` respected globally. Motion variants check `useReducedMotion()`. Anime.js animations check a global flag.
5. **Announce dynamic content.** Toast notifications, streaming text, and chat responses use `aria-live="polite"` regions.
6. **Use semantic HTML.** `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<footer>` — never generic `<div>` for structure.
7. **Support screen reader announcements.** Loading states, errors, and status changes announced via `aria-live` regions.

### Implementation Patterns

- **Skip-to-content link** as first focusable element in every layout
- **Focus trap** in modals, dialogs, and mobile menus
- **Escape key** closes overlays, menus, and drawers
- **Reduced-motion variant helper**: `withReducedMotion(variants, prefersReduced)` from `animations/variants.ts`
- **Color contrast**: All text/background combinations checked against WCAG AA (4.5:1 normal, 3:1 large)
- **Error announcements**: Form validation errors use `aria-describedby` to associate error text with inputs

---

## 15. Frontend Implementation Roadmap

### Sprint 1: Foundation

> Establish the project structure, design system, and developer tooling.

| Task | Details |
|---|---|
| Restructure folders | Apply the approved folder structure. Remove dead scaffolding. |
| Configure ESLint | Keep `eslint.config.js`, remove `.eslintrc.json`. Enable `jsx-a11y` rules. |
| Configure TypeScript | Strict mode, path aliases (`@/*` → root). Verify `next-env.d.ts`. |
| Set up providers | `ThemeProvider`, `QueryProvider`, `ToastProvider` in root layout. |
| Wire TanStack Query | `query-provider.tsx` with sensible defaults. DevTools in dev mode. |
| Build primitive UI kit | `Button`, `Badge`, `Card`, `Input`, `Skeleton`, `ScrollArea` — all with CVA variants, dark mode, focus rings. |
| Build system shell | `AppSidebar`, `AppTopbar`, `ThemeToggle`, `UserMenu` — responsive, Zustand-powered. |
| Configure middleware | Clerk auth middleware for `/dashboard/*`. Public route allowlist. |
| Verify build | `npm run build` passes with zero errors. |

**Deliverable:** A working app shell with design system, theme switching, and route protection. No features visible.

---

### Sprint 2: Authentication & Repository Management

> Ship login/signup and the ability to register and list repositories.

| Task | Details |
|---|---|
| Set up Clerk | Configure Clerk project, install provider, wire middleware. |
| Build sign-in/sign-up pages | Custom pages using Clerk components. |
| Build auth store | Zustand `auth-store.ts` mirroring Clerk state. |
| Build `api-client.ts` | Typed fetch wrapper with token injection. |
| Build repository API service | `listRepositories`, `getRepository`, `createRepository`, `deleteRepository` |
| Build repository list page | `RepositoryCard`, `RepositoryList`, `RepositoryStatusBadge`. TanStack Query for data. |
| Build add-repository dialog | Form with URL input, provider selector. Mutation with optimistic update. |
| Build empty state | `EmptyState` component for new users with no repositories. |

**Deliverable:** User can sign up, sign in, add a Git repository, see it in a list with indexing status.

---

### Sprint 3: Repository Workspace Shell

> Build the multi-tab workspace environment that all other features plug into.

| Task | Details |
|---|---|
| Build `workspace-store.ts` | Zustand store: activeRepositoryId, activeTab, sidebar state. |
| Build `[repositoryId]/layout.tsx` | Workspace shell with tabs, breadcrumbs, status bar. |
| Build `RepositoryWorkspaceTabs` | Tab navigation: Chat, Graph, Settings. Active tab drives route. |
| Build responsive sidebar | Persistent on desktop, collapsible on tablet, overlay on mobile. |
| Integrate Lenis | Smooth scroll in workspace content area. |
| Build `PageHeader` component | Title, description, actions slot. Reusable across all pages. |

**Deliverable:** User can click a repository, see the workspace shell, switch between tabs, and each tab shows a placeholder page.

---

### Sprint 4: AI Chat — Core

> Build the real-time streaming AI chat experience.

| Task | Details |
|---|---|
| Build `chat/types/chat.ts` | Message, Thread, Citation, StreamEvent types. |
| Build `chat/services/chat-api.ts` | `startQuery` (POST), `streamQuery` (SSE). |
| Build `useChat` hook | State machine: idle → loading → streaming → done → error. Message history management. |
| Build `useChatStream` hook | SSE consumer. Parses `text`, `citation`, `error` events. Yields to `useChat`. |
| Build `ChatInput` | Textarea with submit, keyboard shortcut (Enter to send), loading state. |
| Build `ChatMessage` | Renders Markdown, code blocks (syntax-highlighted), citations. |
| Build `StreamingMessage` | Appends text word-by-word from SSE. Citation cards animate in. |
| Build `CitationCard` | File path, line range, excerpt. Click navigates to Code tab (future). |
| Build `ChatThread` | Scrollable message list, auto-scroll on new message, citation panel. |
| Wire SSE endpoint | Connect to backend `/repositories/{id}/query/stream`. |

**Deliverable:** User can ask a question and receive a streaming, cited answer from the backend.

---

### Sprint 5: AI Chat — Polish & Context

> Add conversation history, context panel, and edge case handling.

| Task | Details |
|---|---|
| Build conversation history | TanStack Query fetching past threads. Thread list in sidebar. |
| Build context panel | Shows files and chunks used in the current response. Expandable. |
| Handle errors | Network failure, backend error, timeout — with retry and recovery. |
| Handle empty states | No messages yet → prompt suggestions. |
| Handle long responses | Progressive rendering, scroll-to-bottom button. |
| Keyboard shortcuts | `Ctrl+Enter` to send, `↑` to edit last message, `Escape` to cancel streaming. |
| Accessibility | `aria-live="polite"` on streaming text, focus management on new message, skip-to-chat link. |

**Deliverable:** A production-quality chat experience with history, context, and error recovery.

---

### Sprint 6: Repository Graph

> Build the dependency visualization interface.

| Task | Details |
|---|---|
| Build `graph/types/graph.ts` | Node, Edge, GraphLayout, Filter types. |
| Build `graph/services/graph-api.ts` | `getDependencyGraph`, `getFileDetails`. |
| Build `useDependencyGraph` hook | TanStack Query fetching graph data. Layout computation. |
| Build `useGraphLayout` hook | Force-directed layout (D3-force or @xyflow/react). |
| Build `DependencyGraph` component | Canvas/SVG renderer. Pan, zoom, drag. |
| Build `GraphNode` component | File/type icon, label, color by layer. Selection state. |
| Build `GraphEdge` component | Directed edges with arrowheads. Highlight on hover. |
| Build `GraphControls` | Zoom in/out, fit to view, filter by layer, search. |
| Build `GraphTooltip` | File path, dependencies, "Open in Chat" action. |
| Build `GraphLegend` | Layer color coding, node shape key. |
| Responsive graph view | Simplified layout on mobile, pinch-to-zoom. |

**Deliverable:** User can explore a repository's dependency graph with pan/zoom, search, and filtering.

---

### Sprint 7: Analytics

> Build the analytics dashboard with metrics and charts.

| Task | Details |
|---|---|
| Build `analytics/types/analytics.ts` | Metric, TimeSeries, AnalyticsDashboard types. |
| Build `analytics/services/analytics-api.ts` | `getDashboardMetrics`, `getQueryTrends`, `getLanguageBreakdown`. |
| Build `useAnalytics` hook | Parallel TanStack Query for all dashboard panels. |
| Build `AnalyticsDashboard` | Grid layout with responsive columns. |
| Build `MetricCard` | Value, label, sparkline, trend indicator. |
| Build `LanguageChart` | Horizontal bar chart showing file count per language. |
| Build `QueryTrends` | Line chart showing query volume over time. |
| Build `IndexingHealth` | Success/failure rate, recent errors list. |
| Build `TimeRangeSelector` | 24h, 7d, 30d, 90d presets. |
| Chart library decision | Evaluate recharts vs. visx vs. chart.js. Lightweight, server-compatible. |

**Deliverable:** User can view repository-level and system-wide analytics with time-range filtering.

---

### Sprint 8: Code Viewer (Future)

> Basic read-only file tree and file content viewer integrated into the workspace.

| Task | Details |
|---|---|
| Build code viewer service | `getFileTree`, `getFileContent`. |
| Build file tree | Recursive tree with expand/collapse. Icon per file type. |
| Build file content viewer | Syntax-highlighted read-only view (use `shiki` or `prism-react-renderer`). |
| Wire citations → code | `CitationCard` click opens file in Code tab at exact line. |

---

### Sprint 9: Polish & Performance

> Performance audits, loading states, error boundaries, and final polish.

| Task | Details |
|---|---|
| Loading states | `Skeleton` components for every page and panel. |
| Error boundaries | `ErrorBoundary` per route segment. Fallback UI with retry. |
| Empty states | Every list view has a meaningful empty state. |
| Performance audit | Lighthouse, bundle analysis, image optimization, route prefetching. |
| Animation audit | Verify all reduced-motion paths. Remove unnecessary animations. |
| Accessibility audit | Keyboard nav pass, screen reader pass, color contrast pass. |
| Responsive audit | Test all pages at 320px, 768px, 1280px, 1920px. |
| Build verification | `npm run build` passes. Docker build succeeds. |

---

### Sprint 10: Beta Readiness

> Documentation, error monitoring, and launch preparation.

| Task | Details |
|---|---|
| User-facing documentation | Tooltips, empty-state helpers, onboarding tips. |
| Error monitoring | Integrate Sentry or similar. Source maps uploaded. |
| Feature flags | `config/features.ts` — disable graph/analytics for MVP if needed. |
| Final build optimization | Code splitting, dynamic imports, image optimization. |
| Docker verification | Frontend Dockerfile builds and runs. |
| Backend integration test | Full E2E test across all features. |
| Deployment docs | Environment variables, build steps, health check endpoint. |

---

## Architecture Decision Records

### ADR-1: Why not React Server Components everywhere?

Server Components are used for data-fetching pages (repository list, analytics dashboard) where TanStack Query's `useSuspenseQuery` can be called in server components via `prefetchQuery`. However, the chat feature is inherently client-side (SSE streaming, real-time state), and the graph requires client-side DOM manipulation (canvas/SVG). Server components provide metadata, initial data loading, and static content; client components handle interactivity.

### ADR-2: Why Motion (by Motion One) instead of Framer Motion?

Motion is the official successor to Framer Motion, developed by the same team. It has a smaller bundle size (~15 kB vs ~30 kB), the same API surface, and is actively maintained. The existing codebase already uses `framer-motion` in imports — these will be updated to `motion` with minimal diff. The API is a drop-in replacement.

### ADR-3: Why Zustand over Jotai/Valtio/Redux?

Zustand is the simplest store that works outside React components. This matters for `api-client.ts` token injection and for `workspace-store.ts` reads from non-component code (route guards, service layer). It has zero boilerplate, no provider nesting, and TypeScript inference works out of the box.

### ADR-4: Why TanStack Query for chat history?

Chat history is server-persisted data that benefits from TanStack Query's caching, background refetching, and pagination. The streaming chat session itself (the current conversation) is managed by `useChat` in local state — only persisted threads go through TanStack Query.

---

## Appendices

### A. Import Convention

```typescript
// Absolute imports only
import { Button } from "@/components/ui/button";
import { useChat } from "@/features/chat";
import { cn } from "@/lib/utils";
import { apiClient } from "@/services/api-client";
import { useWorkspaceStore } from "@/stores/workspace-store";

// No relative imports across feature boundaries
// No barrel imports from index.ts in component files (import directly from the file)
```

### B. File Naming Convention

| Pattern | Example | Used For |
|---|---|---|
| `kebab-case.ts` | `use-scroll-y.ts` | Hooks, utilities, services, types, config |
| `kebab-case.tsx` | `chat-input.tsx` | Components (except pages) |
| `PascalCase.tsx` | `page.tsx`, `layout.tsx` | Next.js page/layout files |
| `CAMEL_CASE.ts` | `SITE_NAME` in constants | Constant values |

### C. Component File Template

```typescript
// 1. "use client" (top of file, if needed)
// 2. Imports (grouped)
// 3. Types (local to component)
// 4. Component function (exported)
// 5. Sub-components (private, not exported)
// 6. Styles (none — Tailwind only)
```

### D. State Management Decision Tree

```
Is it server data?
  → YES → TanStack Query (useQuery / useMutation)
  → NO  → Is it shared across unrelated components?
           → YES → Zustand store
           → NO  → Is it URL-relevant?
                    → YES → useParams / useSearchParams
                    → NO  → useState / useReducer
```
