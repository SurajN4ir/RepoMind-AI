"use client";

/**
 * features/landing/index.ts
 *
 * Public API for the landing feature module.
 *
 * app/page.tsx imports LandingPage from here — it never reaches into
 * internal section or component files directly.
 */

import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { AnimatedBackground } from "./components/animated-background";
import { NavBar } from "./components/nav-bar";
import { HeroSection } from "./sections/hero-section";
import { PipelineSection } from "./sections/pipeline-section";
import { FeaturesSection } from "./sections/features-section";
import { ArchitectureSection } from "./sections/architecture-section";
import { WhySection } from "./sections/why-section";
import { MockDemoSection } from "./sections/mock-demo-section";
import { TechStackSection } from "./sections/tech-stack-section";
import { CTASection } from "./sections/cta-section";
import { FooterSection } from "./sections/footer-section";

// ---------------------------------------------------------------------------
// Composed landing page
// ---------------------------------------------------------------------------

export function LandingPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.replace("/repositories");
    }
  }, [isLoaded, isSignedIn, router]);
  return (
    <>
      <AnimatedBackground />
      <NavBar />

      <main id="main-content" tabIndex={-1}>
        {/* Skip-to-content target — improves keyboard navigation */}
        <HeroSection />
        <PipelineSection />
        <FeaturesSection />
        <ArchitectureSection />
        <WhySection />
        <MockDemoSection />
        <TechStackSection />
        <CTASection />
      </main>

      <FooterSection />
    </>
  );
}

// Named re-exports for direct use in tests or Storybook
export {
  AnimatedBackground,
  NavBar,
  HeroSection,
  PipelineSection,
  FeaturesSection,
  ArchitectureSection,
  WhySection,
  MockDemoSection,
  TechStackSection,
  CTASection,
  FooterSection,
};
