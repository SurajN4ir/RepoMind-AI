import { BarChart3, GitBranch, Home, Search, Settings, type LucideIcon } from "lucide-react";

export type NavLink = {
  label: string;
  href: string;
  icon?: LucideIcon;
};

export type NavGroup = {
  label: string;
  items: NavLink[];
};

export const sidebarNav: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { label: "Home", href: "/repositories", icon: Home },
      { label: "Search", href: "/search", icon: Search },
    ],
  },
  {
    label: "Workspace",
    items: [
      { label: "Repositories", href: "/repositories", icon: GitBranch },
    ],
  },
  {
    label: "Insights",
    items: [
      { label: "Analytics", href: "/analytics", icon: BarChart3 },
    ],
  },
  {
    label: "Resources",
    items: [
      { label: "Settings", href: "/settings", icon: Settings },
    ],
  },
];
