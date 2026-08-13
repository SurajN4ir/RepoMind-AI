"use client";

/**
 * features/landing/sections/footer-section.tsx
 *
 * Site footer with:
 * - RepoMind wordmark + tagline
 * - Three link columns (Product, Documentation, Community)
 * - Bottom bar: copyright + theme toggle
 */

import Link from "next/link";
import { useTheme } from "next-themes";
import { MoonIcon, SunIcon, GithubIcon } from "@/components/icons/navigation-icons";
import { cn } from "@/lib/utils";
import {
  SITE_NAME,
  SITE_TAGLINE,
  FOOTER_GROUPS,
  FOOTER_COPYRIGHT,
} from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Theme Toggle (footer variant)
// ---------------------------------------------------------------------------

function FooterThemeToggle() {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark" || theme === "system";

  return (
    <button
      type="button"
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={cn(
        "focus-ring flex h-8 w-8 items-center justify-center rounded-lg",
        "text-muted-foreground transition-colors hover:text-foreground",
      )}
    >
      {isDark ? <SunIcon size={16} /> : <MoonIcon size={16} />}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function FooterSection() {
  return (
    <footer
      role="contentinfo"
      aria-label="Site footer"
      className="border-t border-border bg-surface/40"
    >
      <div className="content-width px-6 py-16">
        {/* Upper grid */}
        <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand column */}
          <div className="sm:col-span-2 lg:col-span-1">
            <Link
              href="/"
              className="focus-ring inline-block rounded-lg"
              aria-label={`${SITE_NAME} home`}
            >
              <span className="text-gradient text-base font-bold tracking-tight">
                {SITE_NAME}
              </span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted-foreground">
              {SITE_TAGLINE}
            </p>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="RepoMind on GitHub (opens in new tab)"
              className="focus-ring mt-4 inline-flex items-center gap-2 rounded-lg text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <GithubIcon size={16} aria-hidden="true" />
              GitHub
            </a>
          </div>

          {/* Link columns */}
          {FOOTER_GROUPS.map((group) => (
            <div key={group.label}>
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-foreground">
                {group.label}
              </h3>
              <ul className="space-y-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="focus-ring rounded text-sm text-muted-foreground transition-colors hover:text-foreground"
                      {...(link.href.startsWith("http")
                        ? { target: "_blank", rel: "noopener noreferrer" }
                        : {})}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-border/50 pt-8">
          <p className="text-xs text-muted-foreground">{FOOTER_COPYRIGHT}</p>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Theme</span>
            <FooterThemeToggle />
          </div>
        </div>
      </div>
    </footer>
  );
}
