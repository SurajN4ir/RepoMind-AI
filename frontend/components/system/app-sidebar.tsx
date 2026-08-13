"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PanelLeftClose, PanelLeft, ChevronDown } from "lucide-react";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";
import { NAV } from "@/lib/constants";
import { sidebarNav } from "@/config/navigation";
import { useUiStore } from "@/stores/ui-store";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";

export function AppSidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <motion.aside
      layout
      className={cn(
        "hidden border-r border-border bg-surface md:flex md:flex-col",
        sidebarCollapsed ? "items-center" : "",
      )}
      style={{
        width: sidebarCollapsed ? NAV.sidebarCollapsedWidth : NAV.sidebarWidth,
        minWidth: sidebarCollapsed ? NAV.sidebarCollapsedWidth : NAV.sidebarWidth,
      }}
      transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
    >
      <div
        className={cn(
          "flex h-14 items-center border-b border-border px-4",
          sidebarCollapsed && "justify-center px-0",
        )}
      >
        {!sidebarCollapsed && (
          <Link
            href="/"
            className="text-lg font-semibold tracking-tight text-foreground"
          >
            RepoMind
          </Link>
        )}
        <Button
          variant="ghost"
          onClick={toggleSidebar}
          className={cn("h-8 w-8 p-0", sidebarCollapsed ? "" : "ml-auto")}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {sidebarCollapsed ? <PanelLeft size={16} /> : <PanelLeftClose size={16} />}
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="flex flex-col gap-6">
          {sidebarNav.map((group) => (
            <div key={group.label} className="flex flex-col gap-1">
              {!sidebarCollapsed && (
                <span className="flex items-center gap-1 px-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {group.label}
                  <ChevronDown size={12} />
                </span>
              )}
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors highlight-hover",
                      sidebarCollapsed && "justify-center px-2",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground",
                    )}
                    title={sidebarCollapsed ? item.label : undefined}
                  >
                    {Icon && <Icon size={18} />}
                    {!sidebarCollapsed && <span>{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
      </ScrollArea>
    </motion.aside>
  );
}
