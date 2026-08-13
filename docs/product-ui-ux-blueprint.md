# RepoMind — Product UI/UX Blueprint

> Single source of truth for the entire frontend experience.
> Every visual, interaction, and motion decision is documented here.
> No implementation decisions remain — only execution.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Design Language](#2-design-language)
3. [Motion System](#3-motion-system)
4. [Component Inventory](#4-component-inventory)
5. [Developer Experience](#5-developer-experience)
6. [Page Blueprints](#6-page-blueprints)
7. [Repository Workspace](#7-repository-workspace)
8. [User Journeys](#8-user-journeys)

---

## 1. Design Principles

### Non-Negotiable Rules

**Every pixel is intentional.** There are no magic values, no one-off colors, no arbitrary spacing. Every visual property references a design token. If a token doesn't exist for what you need, add it to the token system — don't hardcode a value.

**Every component exists once.** If you need a variant of an existing component, extend it with a prop. Never duplicate a component to change its appearance. Duplicated components rot independently and the design language fractures.

**Every animation follows the motion system.** Durations, easings, and variants are imported from `animations/`. No ad-hoc `transition={{ duration: 0.3 }}` in component code. If the motion system doesn't support what you need, extend the motion system.

**Every interaction works without a mouse.** Keyboard navigation is not optional. Focus indicators are not optional. Screen reader announcements are not optional. If an interaction works only with a pointer, it is not complete.

**Every page is responsive.** The layout adapts at three defined breakpoints. Content is never hidden behind hover-only interactions. Touch targets are never smaller than 44×44px.

**Consistency over novelty.** When in doubt, match the pattern used on the last page you built. Surprising users with a new interaction pattern for the same action erodes trust.

**Dark mode is default, light mode is correct.** All designs begin in dark mode. Light mode is a careful override, not an afterthought. Every color token has an explicit light value.

**No placeholder UIs in production.** Empty states, loading states, and error states are designed alongside the happy path. A page is not complete until all three states are implemented.

---

## 2. Design Language

### 2.1 Brand Personality

| Trait | Manifestation |
|---|---|
| **Precision** | Clean lines, generous whitespace, aligned grids. Everything has a reason. |
| **Intelligence** | Subtle gradients, glowing accents on interactive elements, thoughtful micro-interactions. |
| **Developer-first** | Monospace fonts for code, dark UI as default, keyboard shortcuts everywhere, minimal visual noise. |
| **Premium** | Smooth animations, glass-morphism surfaces, careful typography scale, no rough edges. |
| **Grounded** | Citations, file references, source links — every AI response is anchored to real code. |

### 2.2 Visual Identity

The product communicates "intelligent infrastructure." The visual language draws from:

- **Dark space** — deep navy backgrounds (not pure black) create depth without eye strain
- **Neon precision** — bright primary and accent colors used sparingly for interactive elements and highlights
- **Glass surfaces** — frosted glass panels (`backdrop-blur-xl`, translucent borders) layer information without visual weight
- **Glow as feedback** — subtle box-shadows on hover, pulsing glows on active streaming, gradient orbs in backgrounds
- **Typography-forward** — content is king. UI chrome is minimal, text is readable, code is prominent

### 2.3 Color Palette

```
DARK MODE (default)
─────────────────────────────────────────────────────────
Token            HSL                    Usage
─────────────────────────────────────────────────────────
--background     222  38%   7%          Page background
--foreground     210  40%  98%          Primary text
--surface        221  33%  11%          Card/surface backgrounds
--card           215  31%  15%          Elevated surfaces (dropdowns, modals)
--primary        218 100%  65%          CTAs, links, active states
--accent         253  91%  67%          Secondary brand accent (graph, badges)
--success        142  71%  45%          Positive states, health checks
--warning         38  92%  50%          Warning states, indexing in progress
--danger           0  84%  60%          Errors, destructive actions
--muted          217  19%  20%          Subtle backgrounds, dividers
--muted-fg       215  20%  65%          Secondary text, placeholders
--border         217  22%  22%          Borders, dividers, card edges
--ring           218 100%  65%          Focus rings (matches primary)

LIGHT MODE (overrides)
─────────────────────────────────────────────────────────
Token            HSL                    Change
─────────────────────────────────────────────────────────
--background     210  40%  98%          Warm off-white
--foreground     222  47%  11%          Near-black
--surface          0   0% 100%          Pure white
--card           210  40%  96%          Light gray
--primary        218  89%  54%          Slightly deeper blue
--accent         253  74%  60%          Slightly deeper purple
--muted          214  32%  91%          Light gray
--muted-fg       215  16%  47%          Medium gray
--border         214  24%  87%          Light gray border
```

### 2.4 Typography

| Role | Font | Weight | Size (desktop) | Size (mobile) |
|---|---|---|---|---|
| Hero headline | Geist | 600 (semibold) | 56px/1.1 | 32px/1.15 |
| Page title | Geist | 600 (semibold) | 28px/1.2 | 22px/1.3 |
| Section title | Geist | 500 (medium) | 20px/1.3 | 18px/1.3 |
| Card title | Geist | 500 (medium) | 16px/1.4 | 15px/1.4 |
| Body | Geist | 400 (regular) | 15px/1.6 | 14px/1.6 |
| Small | Geist | 400 (regular) | 13px/1.5 | 13px/1.5 |
| Caption | Geist | 400 (regular) | 12px/1.4 | 12px/1.4 |
| Code | Geist Mono | 400 (regular) | 14px/1.6 | 13px/1.6 |
| Code small | Geist Mono | 400 (regular) | 12px/1.5 | 12px/1.5 |

- Geist (UI) and Geist Mono (code) are loaded via `next/font/google`
- Line heights use unitless values for proportional spacing
- Fallback stack: `Inter, ui-sans-serif, system-ui, sans-serif` for UI, `JetBrains Mono, ui-monospace, monospace` for code

### 2.5 Spacing System

Based on a 4px grid:

| Token | px | rem | Usage |
|---|---|---|---|
| `space-0.5` | 2 | 0.125 | Icons gap, inline |
| `space-1` | 4 | 0.25 | Tight padding, icon spacing |
| `space-1.5` | 6 | 0.375 | Button padding Y |
| `space-2` | 8 | 0.5 | Card padding X, form gap |
| `space-3` | 12 | 0.75 | Section padding, card Y |
| `space-4` | 16 | 1 | Page padding, list gap |
| `space-6` | 24 | 1.5 | Section margin, modal padding |
| `space-8` | 32 | 2 | Page sections, hero spacing |
| `space-12` | 48 | 3 | Large sections, desktop padding |
| `space-16` | 64 | 4 | Page gutters (desktop) |
| `space-20` | 80 | 5 | Hero vertical spacing |
| `space-24` | 96 | 6 | Major sections |

- Horizontal padding on page containers: `px-6` (mobile), `px-8` (tablet), `px-12` (desktop)
- Max content width: `max-w-7xl` (1280px)

### 2.6 Grid System

- Content pages use a single-column layout with max-width constraint (`max-w-7xl`)
- Dashboard pages use a sidebar + content two-column layout
- Analytics uses a responsive card grid: 1 col (mobile), 2 col (tablet), 4 col (desktop)
- Chat uses a primary panel + optional citations side panel
- No 12-column grid framework — use Tailwind's utility grid and flexbox directly

### 2.7 Border Radius

| Token | Value | Usage |
|---|---|---|
| `rounded-lg` | 8px | Buttons, inputs, badges |
| `rounded-xl` | 12px | Cards, dialogs, dropdowns |
| `rounded-2xl` | 16px | Modals, large cards, panels |
| `rounded-3xl` | 24px | Hero sections, large containers |
| `rounded-full` | 9999px | Avatars, pills, status dots |

### 2.8 Elevation & Shadows

```
DARK MODE
────────────────────────────────────────────────────
Name       CSS                                          Usage
────────────────────────────────────────────────────
glow       0 0 0 1px hsl(primary/0.18),                Cards, elevated surfaces
           0 18px 48px hsl(222 47% 5% / 0.22)
glow-accent 0 0 0 1px hsl(accent/0.18),                Highlighted cards
            0 18px 48px hsl(222 47% 5% / 0.22)
glow-lg    0 0 40px hsl(primary/0.25),                 Modals, dialogs
           0 0 0 1px hsl(primary/0.12)
card        0 1px 3px hsl(222 47% 5% / 0.3),           Subtle card edge
           0 8px 24px hsl(222 47% 5% / 0.15)
dropdown   0 4px 16px hsl(222 47% 5% / 0.35),          Dropdowns, popovers
           0 0 0 1px hsl(border)
tooltip    0 2px 8px hsl(222 47% 5% / 0.4),            Tooltips

LIGHT MODE
────────────────────────────────────────────────────
glow       0 0 0 1px hsl(border),
           0 18px 48px hsl(222 47% 5% / 0.06)
glow-accent 0 0 0 1px hsl(accent/0.12),
            0 18px 48px hsl(222 47% 5% / 0.06)
glow-lg    0 0 40px hsl(primary/0.08),
           0 0 0 1px hsl(primary/0.06)
card        0 1px 3px hsl(222 47% 5% / 0.04),
           0 8px 24px hsl(222 47% 5% / 0.03)
```

### 2.9 Iconography

- All icons from **Lucide** (already a dependency), imported through the abstraction layer (`components/icons/`)
- Three icon sizes: 16px (inline, buttons), 20px (navigation), 24px (feature cards, empty states)
- No filled icons — outlined style only for consistency
- Icons are always SVG, always `currentColor`

### 2.10 Illustration Style

- Minimal, geometric, line-art style for empty states and error pages
- Use existing Lucide icons composed together rather than custom SVGs
- Pipeline section uses custom SVG pipeline nodes (already exists in `features/landing/`)
- No photography — the product is a developer tool, not a lifestyle brand

### 2.11 Dark Mode / Light Mode

- **Dark is default.** All components are designed dark-first. Light mode is an override.
- Transition between modes is handled by `next-themes` with `attribute="class"`
- Mode transition animation: `transition-colors duration-300` on `<html>` and all surface elements
- Avoid `duration-0` flashes — the theme provider suppresses hydration mismatch

### 2.12 Responsive Philosophy

- **Mobile-first CSS**, desktop as expansion. Base styles target mobile, `md:` and `lg:` add complexity.
- The workspace sidebar is the primary adaptive element: persistent on desktop, collapsible on tablet, overlay on mobile.
- Touch targets never smaller than 44×44px (WCAG 2.5.8).
- Content never horizontally scrolls on mobile — tables, code blocks, and graphs get responsive alternatives.

### 2.13 Accessibility Philosophy

- Target WCAG 2.2 AA.
- Every interactive element has a visible focus ring (`:focus-visible`).
- Every image has `alt` text. Every icon button has `aria-label`.
- Every form input has an associated `<label>`.
- Every status change is announced via `aria-live`.
- Custom components use ARIA roles from their Radix UI primitives.
- Reduced motion is respected globally — Motion variants check `useReducedMotion()`.

---

## 3. Motion System

### 3.1 Motion Principles

1. **Motion has purpose.** Elements move to express relationships (a dialog emerges from its trigger), provide feedback (button depresses on click), or guide attention (new message scrolls into view). Never animate for decoration.
2. **Motion is fast.** UI animations complete in 150–400ms. Longer durations feel sluggish and erode the perception of performance.
3. **Motion is consistent.** Every instance of the same interaction uses the same duration and easing. If a dialog opens with `duration: 0.28, ease: [0.22, 1, 0.36, 1]`, every dialog opens the same way.
4. **Motion respects reduced motion.** All animations check `prefers-reduced-motion` and return identity (no-op) variants when active.
5. **Motion never blocks.** Animations are always `pointer-events: none` on the animating element or use `will-change: transform` to avoid layout thrash.

### 3.2 Animation Philosophy

| Type | Philosophy | Examples |
|---|---|---|
| Micro-interactions | 100–200ms, spring-based | Button hover, card lift, icon rotate |
| Transitions | 200–400ms, ease-based | Page fade, dialog open, sidebar slide |
| Entrance | 300–600ms, staggered | Section reveals, list items, page load |
| Streaming | Real-time, no easing | AI text generation, progress indicators |
| Celebratory | 500–1000ms, spring-based | Indexing complete, query successful |

### 3.3 Motion Durations

| Token | Value | Usage |
|---|---|---|
| `duration-fast` | 150ms | Hover, focus, active states |
| `duration-standard` | 250ms | Dialog open/close, panel slide |
| `duration-slow` | 400ms | Page transitions, section reveals |
| `duration-stream` | 0ms (real-time) | AI streaming text |

### 3.4 Easing Curves

| Token | Curve | Usage |
|---|---|---|
| `ease-out` (default) | `cubic-bezier(0.22, 1, 0.36, 1)` | Entrances, exits, transitions |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Exits only (fade out) |
| `spring-snappy` | stiffness 400, damping 30 | Micro-interactions, button clicks |
| `spring-gentle` | stiffness 180, damping 22 | Card hover, list reveals |
| `spring-bouncy` | stiffness 500, damping 20 | Celebratory, completions |

### 3.5 Animation Inventory

#### Hover Animations

| Element | Effect | Duration | Easing |
|---|---|---|---|
| Button | `y: -1, scale: 1.01` | 150ms | spring-snappy |
| Card | `y: -3, scale: 1.005, shadow: glow→glow-lg` | 200ms | spring-gentle |
| Nav link | Color transition, no transform | 150ms | ease-out |
| Icon button | `scale: 1.1` or subtle rotation | 150ms | spring-snappy |
| Clickable row | Background color change | 150ms | ease-out |
| Tooltip trigger | Underline or subtle indicator | 150ms | ease-out |

#### Focus Animations

| Element | Effect | Duration | Easing |
|---|---|---|---|
| Input | Border color transition, ring appears | 200ms | ease-out |
| Button | Ring appears, subtle scale | 150ms | spring-snappy |
| Any focusable | `outline: 2px solid ring` | 0ms (instant) | — |

#### Page Transitions

| Transition | Effect | Duration | Easing |
|---|---|---|---|
| Page enter | `fadeInUp` — opacity 0→1, y: 16→0 | 400ms | ease-out |
| Page exit | `fadeOut` — opacity 1→0 | 200ms | ease-in |
| Route group change | No transition (instant) | 0ms | — |
| Tab switch (workspace) | Content cross-fade | 250ms | ease-out |

#### Shared Layout Transitions

| Element | Effect | Duration | Easing |
|---|---|---|---|
| Sidebar collapse/expand | Width transition with `layout` | 300ms | ease-out |
| Dialog open | Fade in + scale 0.95→1 | 280ms | ease-out |
| Dialog close | Fade out + scale 1→0.95 | 180ms | ease-in |
| Toast enter | Slide in from right | 300ms | spring-gentle |
| Toast exit | Fade out | 200ms | ease-in |
| Dropdown menu | Fade + slight y offset | 180ms | ease-out |

#### AI Streaming Animations

| Element | Effect | Notes |
|---|---|---|
| Streaming text | Characters appear one by one | No easing — deterministic tick |
| Citation cards | Slide in from bottom, fade in | Staggered by 80ms |
| Context panel | Files appear with fadeInUp | Staggered by 50ms |
| Typing indicator | Three dots bouncing | CSS animation, 1.2s loop |
| Query submitted | Input compresses, spinner appears | 200ms ease-out |

#### Repository Animations

| Element | Effect | Duration |
|---|---|---|
| Repository card enter | fadeInUp, staggered | Stagger 60ms, each 400ms |
| Repository delete | Scale down + fade out | 250ms ease-in |
| Indexing progress bar | Width tween + color pulse | Continuous |
| Indexing complete | Checkmark circle draw (CSS) | 500ms spring-bouncy |

#### Graph Animations

| Element | Effect | Duration |
|---|---|---|
| Graph load | Nodes fade in, edges draw | 200–800ms staggered |
| Node hover | Scale up, glow, label appears | 150ms spring-snappy |
| Node click | Slight scale bump, persists until deselected | 150ms spring |
| Edge highlight | Opacity increase, color shift | 200ms ease-out |
| Filter change | Nodes/edges animate out, new set animates in | 400ms ease-out |
| Zoom/pan | Instant (no animation — direct manipulation) | 0ms |

#### Loading Animations

| Element | Effect | Notes |
|---|---|---|
| Skeleton | Pulse opacity (CSS animation) | 1.5s loop, `bg-muted` |
| Spinner | Rotate (CSS animation) | 1s linear infinite |
| Progress bar | Width tween | 300ms ease-out per step |
| Page load | Content fades in after data resolves | 300ms ease-out |

### 3.6 Library Responsibilities

| Library | Role | When it runs | Bundle |
|---|---|---|---|
| **Motion** (by Motion One) | All UI motion — hover, focus, page transitions, `AnimatePresence`, `layout` animations, scroll-triggered entrances | Always. Bundled in initial chunk. | ~15 kB (permanent) |
| **Anime.js v4** | Complex SVG timeline animations — pipeline section node reveals, connector draws, glow pulses | Only on landing page pipeline section. Dynamic `import()`. Never in initial bundle. | ~10 kB (on demand) |
| **Lenis** | Smooth scrolling in workspace content areas | Only when user enters a repository workspace. Dynamic import on mount. | ~5 kB (on demand) |

- **Motion** handles everything the user interacts with directly
- **Anime.js** handles the marketing pipeline animation (existing code, no changes needed)
- **Lenis** handles scroll-based workspace navigation (only mounted when needed)

---

## 4. Component Inventory

### 4.1 UI Primitives (`components/ui/`)

All primitives use `"use client"` when they handle state, focus, or browser APIs.

| Component | Description | Props | Radix UI |
|---|---|---|---|
| `Button` | Interactive button with variants | `variant`, `size`, `asChild`, `disabled`, `loading` | `Slot` |
| `Badge` | Inline status label | `variant` (default, success, warning, danger) | — |
| `Card` | Container surface with glass effect | `asChild`, `hoverable` | — |
| `Input` | Text input with label, error, helper | `label`, `error`, `helperText`, `size` | — |
| `Textarea` | Multi-line text input | `label`, `error`, `maxRows`, `autoResize` | — |
| `Select` | Dropdown select | `options`, `placeholder`, `error` | `Select` |
| `Dialog` | Modal dialog | `open`, `onClose`, `title`, `description` | `Dialog` |
| `DropdownMenu` | Context/popover menu | `items`, `align`, `trigger` | `DropdownMenu` |
| `Tabs` | Tab navigation | `tabs`, `defaultValue`, `onChange` | `Tabs` |
| `Tooltip` | Hover tooltip | `content`, `side`, `delay` | `Tooltip` |
| `ScrollArea` | Custom scroll container | `asChild` | `ScrollArea` |
| `Skeleton` | Loading placeholder | `width`, `height`, `variant` | — |
| `Toast` | Transient notification | `variant`, `title`, `description`, `duration` | — |
| `Separator` | Horizontal/vertical divider | `orientation` | `Separator` |
| `Avatar` | User/repository avatar | `src`, `alt`, `fallback`, `size` | `Avatar` |
| `Progress` | Linear progress indicator | `value`, `max`, `variant` | `Progress` |
| `Switch` | Toggle control | `checked`, `onChange`, `label` | `Switch` |
| `Command` | Command palette container | `items`, `onSelect`, `search` | `Command` |

### 4.2 Shared Components (`components/shared/`)

| Component | Description | Props |
|---|---|---|
| `EmptyState` | Centered empty state with icon, title, description, action | `icon`, `title`, `description`, `action` |
| `ErrorBoundary` | React error boundary with fallback UI | `fallback`, `onError` |
| `LoadingScreen` | Full-page loading state | `message`, `variant` |
| `ConfirmDialog` | Confirmation modal for destructive actions | `open`, `title`, `message`, `confirmLabel`, `onConfirm`, `variant` |
| `PageHeader` | Page title, description, actions | `title`, `description`, `actions`, `backLink` |
| `StatusDot` | Colored status indicator | `status`, `size`, `label` |
| `Keybinding` | Displays keyboard shortcut | `keys` (e.g., `["⌘", "K"]`) |
| `Breadcrumbs` | Hierarchical page navigation | `items`, `current` |
| `SearchInput` | Global search input with keyboard shortcut | `value`, `onChange`, `placeholder`, `onSubmit` |
| `DataTable` | Sortable, paginated data table | `columns`, `data`, `sortable`, `pagination` |

### 4.3 System Components (`components/system/`)

| Component | Description | Connected To |
|---|---|---|
| `AppSidebar` | Dashboard sidebar navigation | `workspace-store`, `auth-store` |
| `AppTopbar` | Dashboard top bar with breadcrumbs, user menu, search | `workspace-store` |
| `ThemeToggle` | Dark/light mode toggle | `next-themes` |
| `UserMenu` | Clerk `UserButton` + dropdown with settings, sign out | Clerk |
| `AppFooter` | Marketing page footer | — |
| `CommandPalette` | ⌘K command palette | `ui-store` |
| `NotificationCenter` | Bell icon + dropdown with notifications | `ui-store` |

### 4.4 Workspace Components (`features/`)

#### Chat (`features/chat/components/`)

| Component | Description |
|---|---|
| `ChatThread` | Scrollable message container with auto-scroll |
| `ChatMessage` | Single message (user or assistant) with markdown rendering |
| `ChatInput` | Message composer with send, stop, suggestions |
| `StreamingMessage` | In-progress assistant message with word-by-word reveal |
| `CitationCard` | Individual citation with file path, excerpt, line range |
| `CitationPanel` | Side panel listing all citations for the current response |
| `ContextPanel` | Shows files and chunks used in the current response |
| `ThreadList` | History of past conversation threads |
| `ChatEmpty` | Prompt suggestions shown when no messages exist |
| `ModelSelector` | Dropdown to select AI model (if multiple are available) |

#### Repositories (`features/repositories/components/`)

| Component | Description |
|---|---|
| `RepositoryCard` | Repository summary card with status, language, last indexed |
| `RepositoryList` | Grid/list of repository cards |
| `RepositoryStatusBadge` | Indexing status indicator (pending, indexing, ready, failed) |
| `AddRepositoryDialog` | Form to register a new repository |
| `RepositorySettings` | Update name, description, re-index, delete |
| `WorkspaceTabs` | Tab bar for Chat / Graph / Code / Settings |
| `IndexingProgress` | Animated progress bar for indexing status |

#### Graph (`features/graph/components/`)

| Component | Description |
|---|---|
| `DependencyGraph` | Main graph canvas with force-directed layout |
| `GraphNode` | Individual node in the graph |
| `GraphEdge` | Directed edge between nodes |
| `GraphControls` | Zoom, pan, fit, filter, search controls |
| `GraphTooltip` | Hover tooltip showing node details |
| `GraphLegend` | Color/icon legend for node types |
| `GraphSearch` | Search within graph nodes |

#### Analytics (`features/analytics/components/`)

| Component | Description |
|---|---|
| `AnalyticsDashboard` | Grid layout of analytics panels |
| `MetricCard` | Single metric with value, label, sparkline |
| `TimeSeriesChart` | Line/area chart over time |
| `BarChart` | Horizontal/vertical bar chart |
| `LanguageBreakdown` | Language distribution visualization |
| `IndexingHealth` | Success/failure metrics with recent errors |
| `TimeRangeSelector` | Preset time range buttons |

### 4.5 Icon Components (`components/icons/`)

| File | Contents |
|---|---|
| `pipeline-icons.tsx` | Pipeline-specific icon map + `PipelineIcon` component (existing) |
| `navigation-icons.tsx` | Nav arrow, menu, close, external link icons (existing) |
| `feature-icons.tsx` | Feature card icons, comparison icons (existing) |
| `provider-icons.tsx` | GitHub, GitLab, Bitbucket, self-hosted icons |

---

## 5. Developer Experience

### 5.1 Command Palette

- Trigger: `⌘K` (macOS), `Ctrl+K` (Windows/Linux)
- Also accessible via a search icon in the topbar
- Modal overlay: glass surface, centered, 640px wide, `max-h-[60vh]`
- Search input auto-focused on open
- Results grouped by category: Pages, Repositories, Actions, Settings
- Fuzzy search on names and descriptions
- Keyboard navigation: `↑/↓` to move, `Enter` to select, `Escape` to close
- Recent items shown when search is empty
- Animate: fade in + scale, 280ms ease-out

### 5.2 Keyboard Shortcuts

| Shortcut | Action | Context |
|---|---|---|
| `⌘K` | Open command palette | Global |
| `⌘N` | New chat | Chat view |
| `⌘⇧C` | Clear current chat | Chat view |
| `⌘Enter` | Send message | Chat input focused |
| `Escape` | Cancel streaming / close dialog | Various |
| `⌘1`–`⌘4` | Switch workspace tab | Workspace |
| `⌘B` | Toggle sidebar | Dashboard |
| `⌘R` | Refresh repository | Repository view |
| `/` | Focus search | Any |
| `⌘,` | Open settings | Dashboard |
| `⌘⇧G` | Focus graph search | Graph view |
| `⌘+` / `⌘-` | Zoom in/out | Graph view |
| `⌘0` | Reset zoom | Graph view |

- Show available shortcuts in a dialog via `?` key or "Keyboard shortcuts" in command palette
- Display keybindings in tooltips for primary actions

### 5.3 Search Experience

- Global search in the topbar (magnifying glass icon + placeholder: "Search repositories, files, or ask a question...")
- On submit, navigates to chat with the query pre-filled
- Repository-specific search in workspace topbar: searches within the current repository
- Search results show: file path, match excerpt, repository name
- Keyboard shortcut: `/` from anywhere in the dashboard

### 5.4 Notifications

- Bell icon in topbar (right side, next to user menu)
- Badge count for unread notifications
- Dropdown panel: list of notifications grouped by date
- Notification types: indexing complete, indexing failed, query shared, team invite
- Click marks as read and navigates to relevant page
- Empty state: "No notifications"
- Real-time via polling or WebSocket (future)

### 5.5 Context Menus

| Element | Menu Items |
|---|---|
| Repository card | Open, Open in new tab, Copy URL, Re-index, Delete |
| Chat message | Copy text, Copy as markdown, Share, Regenerate |
| Graph node | View file, Show dependencies, Show dependents, Add to chat context |
| File in citation | Open in Code Viewer, Copy path, Add to chat context |
| Tab | Close, Close others, Close to the right |

- Right-click or long-press (mobile) triggers menu
- Uses `DropdownMenu` primitive
- Animate: fade in, 180ms ease-out

### 5.6 Drag and Drop

- **Repository reordering** in the sidebar (future)
- **File upload** for code snippets (future)
- Not a primary interaction pattern — use standard click/select for most actions

### 5.7 Repository Indexing Flow

```
1. User registers repository URL
2. Repository appears in list with status "pending"
3. Backend begins indexing
4. Repository status transitions: pending → indexing → ready / failed
5. Frontend polls status via TanStack Query (refetchInterval: 5000)
6. During indexing:
   - RepositoryCard shows animated progress bar
   - StatusBadge shows "Indexing" with pulse animation
   - Chat shows "Repository is being indexed" message
7. On completion:
   - Progress bar fills, checkmark appears
   - StatusBadge transitions to "Ready" (green)
   - Subtle success toast appears
   - Repository card animates with a brief glow
8. On failure:
   - StatusBadge shows "Failed" (red)
   - Error details shown in repository view
   - "Retry" button available
```

### 5.8 AI Streaming Flow

```
1. User types question in ChatInput
2. Input compresses, send button becomes stop button
3. Message appears in ChatThread as user message (instant)
4. Assistant message appears with streaming indicator (cursor blink)
5. Text streams word-by-word (no easing, ~12ms per word)
6. Citation cards appear as they resolve (slide in from bottom, staggered)
7. Context panel updates as chunks are identified
8. On completion: streaming cursor stops, "done" state
9. User can:
   - Click citation → navigate to file in Code Viewer
   - Regenerate response
   - Copy response
   - Ask a follow-up question
```

### 5.9 Citation Interactions

- Citations are numbered inline in the response text `[1]`, `[2]`, etc.
- Clicking a citation number opens the citation card below the message
- Citation card shows: file path, line range, code excerpt
- "Open in Code Viewer" button on each citation card
- Hovering over a citation number highlights the corresponding citation card
- Citations panel (side panel in desktop) lists all citations from the current response
- Files in citations panel can be added to the chat context

### 5.10 Graph Interactions

- Pan: click and drag empty space
- Zoom: scroll wheel, pinch (mobile), `⌘+` / `⌘-`
- Select node: single click — tooltip appears
- Inspect node: double click — zooms to node and shows details
- Drag node: click and drag to rearrange (temporarily)
- Filter by type: dropdown selector narrows visible nodes
- Search: highlights matching nodes
- Reset view: double click empty space or press `⌘0`

### 5.11 Theme Switching

- Toggle in topbar (sun/moon icon)
- Also available in Command Palette: "Toggle theme"
- Transition: `transition-colors duration-300` on `<html>` and surface elements
- Persisted in `localStorage` via `next-themes`
- Three states: dark (default), light, system (follows OS preference)
- System preference detected via `prefers-color-scheme` media query

---

## 6. Page Blueprints

### 6.1 Landing Page (`/`)

**Purpose:** Introduce RepoMind, communicate value proposition, drive sign-ups

**User Goals:** Understand what RepoMind does, see it in action, decide to sign up

**Information Hierarchy:**
1. Hero — headline, subheadline, CTA
2. Pipeline — visual explanation of how it works
3. Features — key capabilities
4. Architecture — technical trust signal
5. Why RepoMind — differentiation from traditional RAG
6. Mock demo — interactive prototype without sign-up
7. Tech stack — technology choices (trust)
8. CTA — final conversion

**Layout:** Single column, full-width sections with `max-w-7xl` content constraint

**Navigation:** Sticky transparent header → frosted glass on scroll. Logo left, nav links center, GitHub + CTA right. Mobile: hamburger drawer.

**Section Details:**
- Hero: gradient text headline, animated orbs, cursor spotlight
- Pipeline: SVG pipeline nodes with anime.js animation, triggered on scroll into view
- Features: 3×2 card grid (desktop), 2×3 (tablet), 1 column (mobile)
- Architecture: layered diagram with labels
- Why: comparison table (traditional RAG vs RepoMind)
- Mock demo: simulated chat interaction with animated typing
- Tech stack: categorized card grid
- CTA: large centered CTA with gradient treatment

**Empty States:** N/A (static marketing page)

**Loading States:** N/A (static content, no data fetching)

**Error States:** N/A

**Accessibility:** Skip-to-content link, keyboard-navigable demo, all animations respect reduced motion

**API Dependencies:** None (static content)

**User Journey:** First touchpoint → learn → sign up

**Motion:** Page sections fadeInUp on scroll via Motion `whileInView`. Pipeline section uses Anime.js timeline on enter. Background orbs drift continuously (CSS animation).

**Micro-interactions:** Button hover (lift), card hover (lift + glow), nav link color transition, demo typing animation

---

### 6.2 Authentication (`/sign-in`, `/sign-up`)

**Purpose:** Authenticate users, create accounts

**User Goals:** Sign in to existing account, create new account

**Layout:** Centered card layout, `max-w-md`, minimal chrome. Background uses same dark gradient as landing page.

**Sections:**
- RepoMind logo/wordmark at top
- Clerk `<SignIn />` or `<SignUp />` component
- Social login buttons (GitHub, Google)
- Link to switch between sign-in and sign-up
- Footer: terms, privacy

**States:**
- Default: form visible
- Loading: button shows spinner, form disabled
- Error: inline error message above form
- Success: redirect to `/dashboard`

**Mobile:** Same centered layout, full-width card with padding

**Accessibility:** Focus management on form, error announcements via `aria-live`, all Clerk components are accessible by default

**API Dependencies:** Clerk SDK

**User Journey:** Landing → Sign Up → Dashboard

**Motion:** Card fades in on mount (300ms ease-out). Button loading spinner (CSS animation).

---

### 6.3 Dashboard (`/dashboard`)

**Purpose:** Home base for authenticated users. Overview of repositories, recent activity, quick actions.

**User Goals:** See all repositories at a glance, navigate to a repository, add a new repository

**Layout:** Sidebar (left) + main content area. Sidebar shows: RepoMind logo, navigation links (Repositories, Analytics, Settings), user avatar/name at bottom.

**Sections:**
1. Welcome header — "Welcome back, {name}" + quick stats
2. Recent repositories — horizontal scrollable row of repository cards
3. Quick actions — "Add repository", "New chat", "View analytics"
4. Recent activity — list of recent queries, indexing events

**Empty State (no repositories):**
- Large illustration (composed Lucide icons)
- Title: "No repositories yet"
- Description: "Connect your first repository to start exploring your codebase with AI."
- CTA: "Add Repository" button

**Loading State:**
- Skeleton cards for repository list
- Skeleton text for stats

**Error State:**
- Error message with retry button
- "Unable to load repositories. Please try again."

**Navigation:** AppSidebar persistent (desktop), collapsible (tablet), overlay (mobile). Topbar with breadcrumbs, search, theme toggle, user menu.

**Accessibility:** Skip-to-main link, sidebar nav uses `<nav aria-label="Main">`, keyboard navigation between sections

**API Dependencies:** `GET /repositories`, `GET /dashboard/stats`

**User Journey:** Sign in → Dashboard → Select repository / Add repository

**Motion:** Staggered card entrance (60ms stagger, 400ms per card). Sidebar slide (300ms ease-out). Skeleton pulse (CSS, 1.5s).

---

### 6.4 Repository List (`/dashboard/repositories`)

**Purpose:** Full list of all user repositories with search, filter, sort.

**User Goals:** Find a specific repository, check indexing status, add or remove repositories

**Layout:** Sidebar + main content. Main content has: PageHeader ("Repositories"), search bar, filter tabs (All, Indexing, Ready, Failed), grid of RepositoryCards.

**Sections:**
1. PageHeader with "Add Repository" button
2. Search bar with filter tabs below
3. Repository card grid (responsive: 1→2→3 columns)
4. Pagination at bottom (if > 20 repos)

**Empty State:** Same as Dashboard empty state but more detailed.

**Loading State:** Skeleton card grid (6 skeleton cards matching desired grid layout).

**Error State:** Centered error with retry.

**RepositoryCard content:**
- Repository name (clickable → workspace)
- Git provider icon + URL
- Language summary (colored dots)
- StatusBadge (pending/indexing/ready/failed)
- Last indexed timestamp
- Quick actions menu (three-dot: Open, Re-index, Copy URL, Delete)

**Mobile:** Single column card list. Search bar is full width. Filter tabs are horizontal scrollable.

**Accessibility:** Card list is `<ul>` with `<li>` items. Each card is a single `<a>` tag or has `role="link"`. Status colors have text labels.

**API Dependencies:** `GET /repositories?page=&search=&status=`

**User Journey:** Dashboard → Repository List → Click repository → Workspace

**Motion:** Cards stagger in (60ms delay). Search results filter with layout animation. Delete: card shrinks and fades (250ms).

---

### 6.5 Repository Workspace (`/dashboard/repositories/[id]`)

This is the core experience. See [Section 7: Repository Workspace](#7-repository-workspace).

---

### 6.6 AI Chat (`/dashboard/repositories/[id]/chat`)

**Purpose:** Ask questions about a repository, receive grounded AI answers with citations.

**User Goals:** Understand code, find specific implementations, debug issues, learn a codebase

**Layout:** Three-panel layout (desktop):
- Left: Chat thread (primary, ~60% width)
- Right: Context panel (~30% width) showing current context files and citations
- Citations panel can overlay or be a toggleable side panel on narrower screens

**Sections:**
1. ChatThread — scrollable message list
2. ChatInput — fixed at bottom, textarea with send/stop button
3. ContextPanel (side) — files used in current context
4. CitationPanel (toggleable) — all citations from the response

**Empty State (no messages):**
- Centered prompt suggestions (4–6 example questions)
- Title: "Ask anything about this repository"
- Description: "Get grounded answers with direct citations to your source code."
- Example prompts as clickable chips

**Loading State (query in progress):**
- User message appears instantly
- Assistant message appears with streaming cursor
- Citation cards appear progressively as they resolve
- Context panel updates with file names

**Error State:**
- Message-level error: "Sorry, I couldn't process that question." + retry button
- Connection error: "Connection lost. Trying to reconnect..." with spinner

**ChatMessage types:**
- User: right-aligned, subtle background
- Assistant: left-aligned, citation numbers in text `[1]`, collapsible citation cards below
- System: centered, muted (for "Repository is indexing" messages)
- Error: left-aligned, red accent border

**ContextPanel content:**
- Repository name + status
- Active context files (clickable → open in Code Viewer)
- Token usage (if applicable)

**Mobile:** Single column. Chat is full width. Context panel is a bottom drawer or slide-over activated by a button. Citations inline below messages.

**Accessibility:** `aria-live="polite"` on streaming text. Focus stays on input after send. Tab through messages for citation links.

**API Dependencies:** `POST /repositories/{id}/query`, `GET /repositories/{id}/query/stream?id=`

**User Journey:** Workspace → Chat tab → Type question → Read answer → Click citation → View in Code Viewer (future)

**Motion:** Messages slide in (200ms). Streaming text no easing. Citations stagger (80ms). Context panel files fadeInUp (50ms stagger).

---

### 6.7 Repository Graph (`/dashboard/repositories/[id]/graph`)

**Purpose:** Visualize dependency relationships between files and modules in the repository.

**User Goals:** Understand code structure, find dependency chains, identify circular dependencies, navigate the codebase visually

**Layout:** Full-width canvas with overlay controls. Topbar with graph name, filter controls, search.

**Sections:**
1. Graph canvas (full remaining height)
2. GraphControls overlay (bottom-left or top-right):
   - Zoom in/out buttons
   - Fit to view button
   - Layer filter dropdown
   - View toggle (dependency graph / file tree)
3. GraphSearch (top, expandable)
4. GraphLegend (collapsible, bottom-right)
5. GraphTooltip (appears on hover, follows cursor)

**Empty State (no graph data):**
- "Repository has no indexed dependencies yet."
- "Start by chatting with the repository to generate indexing data."

**Loading State:**
- Full-screen skeleton with pulsing circles representing nodes
- "Building dependency graph..." text

**Error State:**
- "Unable to load dependency graph."
- "The repository may still be indexing." + retry button

**Node types:**
- File (rounded rectangle): module, component, service
- Directory (folder icon): grouping
- External package (rounded square): npm/crate/pip dependency
- Color-coded by layer (API, domain, infrastructure, test)

**Interactions:**
- Hover: tooltip with file path, dependencies count
- Click: select node, show details in tooltip
- Double-click: zoom to node, show immediate dependencies
- Drag: temporarily reposition node
- Pan: click-drag on empty canvas
- Zoom: scroll wheel, pinch, buttons

**Mobile:** Full-screen graph view. Controls in bottom sheet. Tap to select, double-tap to inspect. Pinch to zoom.

**Accessibility:** Graph has tabbable nodes. Arrow keys navigate between connected nodes. Screen reader reads node name, type, connections on focus.

**API Dependencies:** `GET /repositories/{id}/graph`

**User Journey:** Workspace → Graph tab → Explore dependencies → Click node → "Open in Chat" context menu

**Motion:** Nodes fade in staggered. Edges draw in (stroke-dashoffset animation). Hover scale and glow. Selection: brief scale pulse. Filter transitions: 400ms ease-out.

---

### 6.8 Code Viewer (`/dashboard/repositories/[id]/code`)

**Purpose:** Browse and read source files from the indexed repository.

**User Goals:** View file contents, navigate file tree, jump to specific lines from citations

**Layout:** Split panel:
- Left: File tree (collapsible, 280px default)
- Right: File content with syntax highlighting

**Sections:**
1. FileTree — recursive tree with expand/collapse, file type icons
2. FileToolbar — file path, breadcrumbs, "Add to chat context" button, line range indicator
3. FileContent — syntax-highlighted read-only view, line numbers, line highlighting
4. MiniMap (optional) — overview of file structure

**Empty State (no repository selected):**
- "Select a file from the tree to view its contents."
- Or redirects to the first indexed file.

**Loading State:**
- File tree: skeleton tree branches
- File content: skeleton with line-shaped blocks, matching file length estimate

**Error State:**
- "Failed to load file. The file may have been deleted or the repository needs re-indexing."

**Line highlighting:**
- Lines referenced by citations are highlighted with a subtle yellow/blue background
- Scroll-to-line on citation click
- Multiple highlighted ranges supported

**Mobile:** Tab-based toggle: Files tab (tree) | Content tab (file view). Tree is full-width when shown. File view is full-width when shown.

**Accessibility:** Tree is `<ul>` with proper `aria-expanded`. Code block uses `<code>` and `<pre>` with `tabindex="0"` for scroll. Syntax highlighting colors meet contrast requirements.

**API Dependencies:** `GET /repositories/{id}/files`, `GET /repositories/{id}/files/{path}`

**User Journey:** Citation click → Code Viewer at exact line → Browse file → Return to chat

**Motion:** File tree expand/collapse (150ms). File content fade in (200ms). Line highlight pulse on scroll-to (300ms).

---

### 6.9 Analytics (`/dashboard/analytics`)

**Purpose:** System-wide and per-repository usage metrics and health monitoring.

**User Goals:** Understand system usage, monitor indexing health, track query volume, identify trends

**Layout:** Sidebar + main content. Top section: time range selector + key metric cards. Bottom section: detailed charts in responsive grid.

**Sections:**
1. PageHeader ("Analytics") + TimeRangeSelector (24h, 7d, 30d, 90d)
2. Metric cards row (4 cards): Repositories, Queries, Avg Response Time, Indexing Success Rate
3. Charts grid:
   - Query Volume (line chart, time series)
   - Language Breakdown (horizontal bar chart)
   - Indexing Health (success/failure donut + recent errors list)
   - Top Queries (table, most frequent queries)

**Empty State (no data):**
- "No analytics data available yet."
- "Add a repository and start querying to see metrics."

**Loading State:**
- Metric cards: skeleton with text blocks
- Charts: skeleton with chart outlines

**Error State:**
- "Unable to load analytics data."
- Retry button per failed chart (granular error handling)

**Mobile:** Single column. Metric cards wrap. Charts stack vertically. Time range selector is a horizontal scrollable pill group.

**Accessibility:** Charts have accessible data tables as fallback. Color-coded elements have text labels or patterns. Keyboard navigable time range selector.

**API Dependencies:** `GET /analytics/metrics`, `GET /analytics/query-trends`, `GET /analytics/languages`, `GET /analytics/health`

**User Journey:** Dashboard → Analytics → Review metrics → Identify issues → Navigate to repository

**Motion:** Metric cards count-up animation on load (CSS, 600ms). Charts fade in (400ms). TimeRangeSelector pill active state color transition (150ms).

---

### 6.10 Settings (`/dashboard/settings`)

**Purpose:** User preferences, account management, and application configuration.

**User Goals:** Update profile, change theme, manage API keys, configure integrations

**Layout:** Sidebar + main content. Settings navigation on left (within content area, not the app sidebar): Profile, Appearance, API Keys, Integrations, Notifications, Danger Zone.

**Sections (each a card or panel):**
1. **Profile** — Name, email, avatar upload
2. **Appearance** — Theme toggle (dark/light/system), font size preference
3. **API Keys** — Create, copy, revoke API keys for programmatic access
4. **Integrations** — GitHub, GitLab, Bitbucket OAuth connections
5. **Notifications** — Email notification preferences, webhook URLs
6. **Danger Zone** — Delete account with confirmation dialog

**Empty States:** N/A (settings always have content)

**Loading State:** Skeleton form fields.

**Error State:** Inline error on the affected form field. Global save error banner.

**Save pattern:** Auto-save on change (debounced 500ms) for toggles and selects. Manual save button for text inputs.

**Mobile:** Settings nav is a collapsible section picker (dropdown or tabs). Content is full width below.

**Accessibility:** Settings sections use proper `<form>` elements. Each field has `<label>`. Error messages use `aria-describedby`.

**API Dependencies:** `GET /user/settings`, `PUT /user/settings`, `DELETE /user`

**User Journey:** Dashboard → Settings → Update preferences → Continue

**Motion:** Section transitions (fade, 200ms). Toggle switch slide (150ms spring).

---

### 6.11 Profile (`/dashboard/settings/profile`)

Covered under Settings. If a standalone profile page is needed, it shows:
- User avatar (large)
- Name, email
- Join date
- Repositories count, queries count
- Recent activity

**Layout:** Centered card with profile info at top, activity list below.

---

### 6.12 404 Page (`/not-found.tsx`)

**Purpose:** Catch-all for undefined routes.

**Layout:** Centered, full viewport height. Dark background.

**Content:**
- Large 404 text (Geist, 120px, semibold, gradient)
- "This page doesn't exist." subtitle
- "The page you're looking for was moved, deleted, or never existed."
- CTA: "Go to Dashboard" button
- Illustration: Composed Lucide icons (search + X)

**Motion:** 404 number fades in (400ms). Illustration subtle float (CSS animation, 4s).

---

### 6.13 500 Page (`/error.tsx`)

**Purpose:** Catch-all for server errors.

**Layout:** Centered, full viewport height. Dark background.

**Content:**
- Large 500 text (Geist, 120px, semibold, gradient)
- "Something went wrong." subtitle
- "An unexpected error occurred. Our team has been notified."
- CTA: "Try again" button + "Go to Dashboard" secondary button

**Motion:** Same as 404.

---

## 7. Repository Workspace

### 7.1 Concept

The workspace is the primary user environment — a multi-tab, single-repository interface where users explore, query, and understand a codebase. It is the heart of the product. It must feel closer to VS Code or JetBrains than a typical CRUD dashboard.

### 7.2 Layout

```
┌──────────────────────────────────────────────────────┐
│  AppTopbar                                            │
│  ← Dashboard  │  Breadcrumb > repo/cli-tool  │  [🔍] │
├──────────┬───────────────────────────────────────────┤
│          │  WorkspaceTabs                              │
│ Sidebar  │  ┌──────┬──────┬──────┬──────────┐        │
│          │  │ Chat │ Graph│ Code │ Settings │        │
│ Repos    │  └──────┴──────┴──────┴──────────┘        │
│ . . .    │                                           │
│ repo A   │  ┌─────────────────────────────────────┐  │
│ repo B   │  │  Workspace Content                    │  │
│ repo C   │  │                                       │  │
│ . . .    │  │  (Tab-dependent — see below)          │  │
│          │  │                                       │  │
│          │  └─────────────────────────────────────┘  │
│          │                                           │
│          │  StatusBar (bottom)                        │
│          │  repo/cli-tool · main · 245 files · ✓     │
└──────────┴───────────────────────────────────────────┘
```

### 7.3 Sidebar (Repository List)

- Lists all user repositories (not just the active one)
- Active repository highlighted with accent border
- Each item shows: name, status dot, current branch
- Click switches workspace to that repository
- Drag to reorder (future)
- Collapsible: `⌘B` to toggle, button in topbar
- Width: 280px (desktop), full-width overlay (mobile)

### 7.4 WorkspaceTabs

- Horizontal tab bar below topbar
- Tabs: Chat, Graph, Code, Settings
- Active tab underlined with accent color
- Tab icons: Chat (MessageSquare), Graph (Network), Code (Code2), Settings (Settings)
- On mobile: tabs are icons-only with tooltips, horizontally scrollable
- Each tab maps to a route segment: `/chat`, `/graph`, `/code`, `/settings`

### 7.5 StatusBar

- Bottom bar spanning the content area (~36px height)
- Content: repository name, current branch, file count, indexing status
- Subtle, muted text, no visual weight
- Indexing status with animated dot

### 7.6 Tab Contents

#### Chat Tab

```
┌─────────────────────────────────────────┬──────────────────┐
│  ChatThread                              │  ContextPanel     │
│                                         │                   │
│  ┌──────────────────────────────────┐   │  Context Files    │
│  │ User message                      │   │  ┌─────────────┐ │
│  └──────────────────────────────────┘   │  │ auth/jwt...  │ │
│  ┌──────────────────────────────────┐   │  │ auth/midd... │ │
│  │ Assistant message [1][2]          │   │  │ api/depen... │ │
│  │ Lorem ipsum dolor sit amet        │   │  └─────────────┘ │
│  │                                   │   │                   │
│  │ [1] src/auth/jwt_handler.py:12    │   │  Repository       │
│  │ [2] src/auth/middleware.py:45     │   │  cli-tool · main  │
│  └──────────────────────────────────┘   │  Status: ✓ Ready   │
│                                         │                   │
│  ┌──────────────────────────────────┐   │  Citations         │
│  │ Assistant response (streaming)    │   │  ┌─────────────┐ │
│  │ The authentication flow uses █    │   │  │ [1] jwt...  │ │
│  └──────────────────────────────────┘   │  │ [2] midd... │ │
│                                         │  └─────────────┘ │
│                                         │                   │
│  ┌────────────────────────────────────┐ │                   │
│  │ Type a message...              [➤] │ │                   │
│  └────────────────────────────────────┘ │                   │
└─────────────────────────────────────────┴──────────────────┘
```

#### Graph Tab

```
┌──────────────────────────────────────────────────────────┐
│  [🔍 Search files...]  [All Layers ▼]  [🔍 Fit] [+][−]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│              ┌──────┐         ┌──────┐                   │
│     ┌────────┤ Auth ├─────────┤ API  ├─────┐             │
│     │        └──────┘         └──────┘     │             │
│  ┌─────┐                                   ┌──────┐      │
│  │ CLI │                                   │ Core │      │
│  └─────┘                                   └──────┘      │
│     │                                                   │
│     │        ┌──────────┐                               │
│     └────────┤ Database │                               │
│              └──────────┘                               │
│                                                          │
│  ┌────────────── Tooltip ──────────────────┐             │
│  │ src/auth/jwt_handler.py                 │             │
│  │ Dependencies: 3 · Dependents: 5         │             │
│  │ [View file] [Add to chat context]       │             │
│  └─────────────────────────────────────────┘             │
├──────────────────────────────────────────────────────────┤
│  Legend: [■] API · [■] Domain · [■] Infra · [■] Test    │
└──────────────────────────────────────────────────────────┘
```

#### Code Tab

```
┌──────────────────┬───────────────────────────────────────┐
│  File Tree        │  File Content                         │
│                   │                                       │
│  src/             │  ┌─ src/auth/jwt_handler.py ────────┐ │
│  ├─ api/          │  │  1  import jwt                   │ │
│  ├─ auth/         │  │  2  from datetime import ...     │ │
│  │  ├─ jwt...     │  │  3                               │ │
│  │  ├─ midd...   │  │  4  class JWTHandler:            │ │
│  │  └─ schemas   │  │  5      def create_token(...)    │ │
│  ├─ core/         │  │  6          ...                  │ │
│  └─ infra/        │  │  7      def decode_token(...)    │ │
│                   │  │  8          ...                  │ │
│                   │  └───────────────────────────────────┘ │
│                   │                                       │
└──────────────────┴───────────────────────────────────────┘
```

#### Settings Tab

```
┌──────────────────────────────────────────────────────────┐
│  Repository Settings                                      │
│                                                          │
│  ┌─ General ──────────────────────────────────────────┐  │
│  │  Name: cli-tool                                     │  │
│  │  URL: https://github.com/org/cli-tool               │  │
│  │  Description: CLI tool for repository management    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Indexing ──────────────────────────────────────────┐  │
│  │  Status: ✓ Ready · Last indexed: 2 hours ago        │  │
│  │  [Re-index repository]                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Danger Zone ───────────────────────────────────────┐  │
│  │  [Delete repository] — removes all indexed data     │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 7.7 Workspace Responsive Behavior

| Viewport | Sidebar | Tabs | Chat | Graph | Code |
|---|---|---|---|---|---|
| ≥1280px | Persistent 280px | Full bar | 3-panel | Full canvas | Split tree/file |
| 768–1279px | Collapsible toggle | Full bar (scrollable) | 2-panel (citations drawer) | Full canvas (controls overlay) | Tree overlay |
| <768px | Overlay drawer | Icons only | Full screen (citations bottom sheet) | Full screen (controls bottom sheet) | Tab toggle tree/file |

### 7.8 Workspace Accessibility

- Tab list uses `role="tablist"` with proper `aria-controls`, `aria-selected`, `aria-orientation`
- Content panels use `role="tabpanel"` with `aria-labelledby`
- Sidebar is `<nav aria-label="Repository list">`
- StatusBar is `<footer role="status">`

---

## 8. User Journeys

### 8.1 First-Time User Journey

```
Landing Page
  │
  ├── Scroll through sections (learn about RepoMind)
  │
  ├── Try the mock demo (interact without sign-up)
  │
  ├── Click "Get Started"
  │     │
  │     ▼
  │   Sign Up (/sign-up)
  │     │
  │     ├── Enter email + password OR GitHub OAuth
  │     │
  │     ▼
  │   Dashboard (empty state)
  │     │
  │     ├── "Connect your first repository" CTA
  │     │
  │     ▼
  │   Add Repository Dialog
  │     │
  │     ├── Paste Git URL (e.g., https://github.com/org/repo)
  │     ├── Select provider (auto-detected from URL)
  │     ├── Click "Add Repository"
  │     │
  │     ▼
  │   Repository List (new repo appears, status: pending → indexing)
  │     │
  │     ├── Wait for indexing (progress bar, poll every 5s)
  │     │
  │     ▼
  │   Indexing Complete (status: ready, brief glow animation)
  │     │
  │     ├── Click repository → Workspace → Chat tab
  │     │
  │     ▼
  │   Chat (empty state with prompt suggestions)
  │     │
  │     ├── Click "How does authentication work?"
  │     │
  │     ▼
  │   Streaming answer appears with citations
  │     │
  │     ├── Read answer
  │     ├── Click citation → highlights file
  │     ├── Click "Open in Code Viewer" → transitions to Code tab
  │     │
  │     ▼
  │   Code Viewer (file loaded, line highlighted)
  │     │
  │     ├── Browse file tree
  │     ├── Switch to Graph tab
  │     │
  │     ▼
  │   Graph (dependency visualization)
  │     │
  │     ├── Explore dependencies
  │     ├── Click node → "Add to chat context"
  │     │
  │     ▼
  │   Return to Chat (context includes graph node)
  │     │
  │     └── Ask follow-up questions
```

### 8.2 Returning User Journey

```
Sign In → Dashboard
  │
  ├── Recent repositories (horizontal scroll)
  ├── Quick stats (queries this week, repos indexed)
  │
  ├── Click most-used repository
  │     │
  │     ▼
  │   Workspace → Chat tab (previous session restored?)
  │     │
  │     ├── Ask new question
  │     ├── Or scroll up to review past answers
  │     │
  │     └── Continue from where they left off
```

---

## A. Appendices

### A.1 File Naming Quick Reference

| Category | Convention | Example |
|---|---|---|
| Pages | `page.tsx` | `app/(dashboard)/repositories/page.tsx` |
| Layouts | `layout.tsx` | `app/(dashboard)/layout.tsx` |
| UI primitives | `kebab-case.tsx` | `button.tsx`, `dropdown-menu.tsx` |
| Feature components | `kebab-case.tsx` | `chat-input.tsx`, `repository-card.tsx` |
| Hooks | `use-kebab-case.ts` | `use-scroll-y.ts`, `use-chat.ts` |
| Services | `kebab-case.ts` | `chat-api.ts`, `repository-api.ts` |
| Types | `kebab-case.ts` | `chat.ts`, `repository.ts` |
| Stores | `kebab-store.ts` | `workspace-store.ts`, `ui-store.ts` |
| Data | `kebab-case.ts` | `features.ts`, `pipeline.ts` |
| Constants | `kebab-case.ts` | `landing.ts`, `navigation.ts` |

### A.2 Import Convention

```typescript
// Absolute imports only — never relative across feature boundaries
import { Button } from "@/components/ui/button";
import { useChat } from "@/features/chat";
import { cn } from "@/lib/utils";
import { apiClient } from "@/services/api-client";
import { useWorkspaceStore } from "@/stores/workspace-store";

// Direct file imports for primitives (avoid barrel index.ts for components/ui/)
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Barrel imports for features (index.ts is the public API)
import { ChatThread, useChat } from "@/features/chat";
```

### A.3 Design Token Usage Checklist

Before merging any component, verify:

- [ ] All colors reference CSS custom properties (never raw hex codes)
- [ ] All spacing uses Tailwind spacing scale (4px grid)
- [ ] All border radii use Tailwind's `rounded-*` classes
- [ ] All shadows use the predefined shadow tokens
- [ ] All typography uses the predefined font size + weight combinations
- [ ] All animations use the predefined duration and easing tokens
- [ ] All transitions check `prefers-reduced-motion`
- [ ] All interactive elements have visible focus indicators
- [ ] All touch targets are ≥44×44px
- [ ] No magic values exist
