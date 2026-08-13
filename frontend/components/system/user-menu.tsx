"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useClerk } from "@clerk/nextjs";
import { LogOut, Settings } from "lucide-react";
import Link from "next/link";

import { Avatar } from "./avatar";

type UserMenuProps = {
  userInitials: string;
  isSignedIn: boolean;
  isLoaded: boolean;
};

export function UserMenu({ userInitials, isSignedIn, isLoaded }: UserMenuProps) {
  const { signOut, openSignIn } = useClerk();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
      setOpen(false);
    }
  }, []);

  const handleEscape = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") setOpen(false);
  }, []);

  useEffect(() => {
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleEscape);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open, handleClickOutside, handleEscape]);

  if (!isLoaded) {
    return (
      <div className="h-8 w-8 animate-pulse rounded-full bg-muted" aria-hidden="true" />
    );
  }

  if (!isSignedIn) {
    return (
      <button
        onClick={() => openSignIn()}
        className="focus-ring flex h-8 items-center gap-2 rounded-xl bg-primary/10 px-3 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
      >
        Sign in
      </button>
    );
  }

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="focus-ring flex items-center gap-2 rounded-xl p-1 transition-colors hover:bg-muted"
        aria-label="User menu"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <Avatar initials={userInitials} />
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-48 origin-top-right rounded-xl border border-border bg-surface p-1 shadow-card">
          <div className="flex flex-col gap-0.5">
            <Link
              href="/settings"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <Settings size={14} />
              Settings
            </Link>
            <button
              onClick={() => signOut()}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-danger"
            >
              <LogOut size={14} />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
