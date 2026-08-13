"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { motion } from "motion/react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2 border-t border-border p-4"
    >
      <div className="relative flex-1">
        <input
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder ?? "Ask a question..."}
          disabled={disabled}
          className={cn(
            "focus-ring w-full rounded-xl border border-border bg-surface px-4 py-3 pr-20 text-sm text-foreground placeholder:text-muted-foreground/60",
            disabled && "opacity-50",
          )}
        />
        <motion.kbd
          animate={{ opacity: value ? 0 : 0.6 }}
          className="pointer-events-none absolute right-3 top-1/2 hidden -translate-y-1/2 items-center gap-0.5 rounded-md border border-border bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground sm:flex"
        >
          <span className="text-[9px]">⌘</span>K
        </motion.kbd>
      </div>
      <Button
        type="submit"
        disabled={disabled || !value.trim()}
        className="h-10 w-10 p-0"
      >
        <Send size={16} />
      </Button>
    </form>
  );
}
