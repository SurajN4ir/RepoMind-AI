"use client";

/**
 * features/landing/components/nav-bar.tsx
 *
 * Sticky landing page navigation.
 *
 * Behaviour:
 * - Transparent at the top of the page
 * - Transitions to frosted glass on scroll (> 60px)
 * - Mobile: hamburger menu with animated drawer
 * - Keyboard accessible (focus trap in mobile menu, ESC closes)
 * - Framer Motion scroll-triggered backdrop transition
 */

import { motion, useReducedMotion, AnimatePresence } from "motion/react";
import { useEffect, useCallback, useState } from "react";
import Link from "next/link";

import { GithubIcon, MenuIcon, CloseIcon } from "@/components/icons/navigation-icons";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { navContainer, navItem } from "@/animations/variants";
import { NAV_LINKS, SITE_NAME, HERO_CTA_SECONDARY } from "@/features/landing/constants/landing";
import { useScrollY } from "@/animations/scroll";
import { ROUTES } from "@/lib/constants";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function NavBar() {
  const scrollY = useScrollY();
  const prefersReduced = useReducedMotion();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isScrolled = scrollY > 60;

  // Close mobile menu on ESC
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMobileOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  // Focus trap for mobile nav
  useEffect(() => {
    if (!mobileOpen) return;
    const drawer = document.getElementById("mobile-menu");
    if (!drawer) return;

    const focusableEls = drawer.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );
    const first = focusableEls[0];
    const last = focusableEls[focusableEls.length - 1];

    const trap = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };

    document.addEventListener("keydown", trap);
    first?.focus();

    return () => document.removeEventListener("keydown", trap);
  }, [mobileOpen]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const handleNavClick = useCallback(() => setMobileOpen(false), []);

  return (
    <>
      <motion.header
        role="banner"
        className={cn(
          "fixed inset-x-0 top-0 z-50 transition-colors duration-300",
          isScrolled
            ? "border-b border-border/50 bg-background/80 backdrop-blur-xl"
            : "bg-transparent",
        )}
        initial={prefersReduced ? false : { y: -64, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        <nav
          aria-label="Main navigation"
          className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6"
        >
          {/* Wordmark */}
          <Link
            href="/"
            className="focus-ring flex items-center gap-2 rounded-lg"
            aria-label={`${SITE_NAME} home`}
          >
            <span className="text-gradient text-sm font-bold tracking-tight sm:text-base">
              {SITE_NAME}
            </span>
          </Link>

          {/* Desktop nav */}
          <motion.ul
            className="hidden items-center gap-1 md:flex"
            variants={prefersReduced ? {} : navContainer}
            initial="hidden"
            animate="visible"
          >
            {NAV_LINKS.map((link) => (
              <motion.li key={link.href} variants={prefersReduced ? {} : navItem}>
                <a
                  href={link.href}
                  className={cn(
                    "focus-ring rounded-lg px-3 py-2 text-sm font-medium",
                    "text-muted-foreground transition-colors duration-150",
                    "hover:text-foreground",
                  )}
                >
                  {link.label}
                </a>
              </motion.li>
            ))}
          </motion.ul>

          {/* Desktop actions */}
          <div className="hidden items-center gap-3 md:flex">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View on GitHub"
              className={cn(
                "focus-ring flex items-center gap-1.5 rounded-lg px-3 py-2",
                "text-sm font-medium text-muted-foreground transition-colors",
                "hover:text-foreground",
              )}
            >
              <GithubIcon size={16} />
              <span className="hidden lg:inline">{HERO_CTA_SECONDARY}</span>
            </a>
            <Link href={ROUTES.signUp}>
              <Button
                variant="primary"
                className="h-9 px-4 text-xs"
              >
                Get Started
              </Button>
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            type="button"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileOpen}
            aria-controls="mobile-menu"
            className="focus-ring flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:hidden"
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? <CloseIcon size={20} /> : <MenuIcon size={20} />}
          </button>
        </nav>
      </motion.header>

      {/* Mobile menu overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 z-40 bg-background/60 backdrop-blur-sm md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              aria-hidden="true"
            />

            {/* Drawer */}
            <motion.div
              id="mobile-menu"
              role="dialog"
              aria-label="Mobile navigation"
              aria-modal="true"
              className="fixed inset-x-0 top-16 z-50 border-b border-border bg-surface p-6 md:hidden"
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            >
              <ul className="flex flex-col gap-1">
                {NAV_LINKS.map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      className="focus-ring flex rounded-lg px-3 py-3 text-base font-medium text-muted-foreground transition-colors hover:bg-muted/40 hover:text-foreground"
                      onClick={handleNavClick}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
              <div className="mt-6 flex flex-col gap-3">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="focus-ring flex items-center gap-2 rounded-lg border border-border px-4 py-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                  onClick={handleNavClick}
                >
                  <GithubIcon size={16} />
                  {HERO_CTA_SECONDARY}
                </a>
                <Link href={ROUTES.signUp} onClick={() => setMobileOpen(false)}>
                <Button
                  variant="primary"
                  className="w-full justify-center"
                >
                  Get Started
                </Button>
              </Link>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
