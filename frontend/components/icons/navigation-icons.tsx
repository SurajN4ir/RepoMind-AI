/**
 * components/icons/navigation-icons.tsx
 *
 * Icon components for site navigation, header, and footer.
 */

import {
  ArrowRight,
  ExternalLink,
  Github,
  Menu,
  Moon,
  Sun,
  X,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import type { LucideProps } from "lucide-react";

// Navigation controls
export { Menu as MenuIcon, X as CloseIcon };

// Theme toggle
export { Moon as MoonIcon, Sun as SunIcon };

// Directional
export { ArrowRight as ArrowRightIcon, ChevronDown as ChevronDownIcon, ChevronRight as ChevronRightIcon };

// External
export { ExternalLink as ExternalLinkIcon, Github as GithubIcon };

// Composite — theme toggle with accessible label
interface ThemeIconProps extends LucideProps {
  theme: "dark" | "light" | "system";
}

export function ThemeIcon({ theme, ...props }: ThemeIconProps) {
  if (theme === "dark") return <Moon {...props} />;
  return <Sun {...props} />;
}
