"use client";

import { User, Bell, Shield, Palette } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";

const settingsGroups = [
  {
    label: "Profile",
    icon: User,
    items: [
      { label: "Account", description: "Manage your account details and preferences" },
      { label: "Notifications", description: "Configure email and in-app notifications", icon: Bell },
    ],
  },
  {
    label: "Workspace",
    icon: Shield,
    items: [
      { label: "Security", description: "API keys, tokens, and access controls" },
      { label: "Appearance", description: "Theme and display preferences", icon: Palette },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Settings"
        description="Manage your account and preferences"
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {settingsGroups.map((group) => (
          <div key={group.label} className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <group.icon size={16} className="text-muted-foreground" />
              <h2 className="text-sm font-semibold text-foreground">{group.label}</h2>
            </div>
            {group.items.map((item) => (
              <Card key={item.label} className="cursor-pointer p-4 transition-colors hover:bg-surface/80">
                <div className="flex items-start gap-3">
                  {item.icon && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                      <item.icon size={14} className="text-muted-foreground" />
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium text-foreground">{item.label}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
