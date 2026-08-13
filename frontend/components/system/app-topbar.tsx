"use client";

import { Menu } from "lucide-react";

import { cn } from "@/lib/utils";
import { NAV } from "@/lib/constants";
import { useUiStore } from "@/stores/ui-store";
import { useSyncAuthStore } from "@/stores/auth-store";
import { ThemeToggle } from "./theme-toggle";
import { UserMenu } from "./user-menu";
import { Button } from "@/components/ui/button";

type AppTopbarProps = {
  title?: string;
  className?: string;
};

export function AppTopbar({ title, className }: AppTopbarProps) {
  const { sidebarCollapsed, setMobileSidebarOpen } = useUiStore();
  const auth = useSyncAuthStore();

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-xl",
        className,
      )}
      style={{
        marginLeft: sidebarCollapsed ? NAV.sidebarCollapsedWidth : NAV.sidebarWidth,
      }}
    >
      <Button
        variant="ghost"
        className="md:hidden"
        onClick={() => setMobileSidebarOpen(true)}
        aria-label="Open menu"
      >
        <Menu size={18} />
      </Button>

      {title && (
        <h1 className="text-sm font-semibold text-foreground">{title}</h1>
      )}

      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        <UserMenu
          userInitials={auth.userInitials}
          isSignedIn={auth.isSignedIn}
          isLoaded={auth.isLoaded}
        />
      </div>
    </header>
  );
}
