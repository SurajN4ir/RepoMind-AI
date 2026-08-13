"use client";

import { useEffect, useState, useRef } from "react";

export function useStreamingText(fullText: string, speed = 16) {
  const [displayed, setDisplayed] = useState("");
  const indexRef = useRef(0);
  const rafRef = useRef<number | null>(null);
  const lastTimeRef = useRef(0);

  useEffect(() => {
    indexRef.current = 0;
    setDisplayed("");
    lastTimeRef.current = 0;

    if (!fullText) return;

    const animate = (time: number) => {
      if (!lastTimeRef.current) lastTimeRef.current = time;
      const delta = time - lastTimeRef.current;

      if (delta >= speed) {
        const charsToAdd = Math.floor(delta / speed);
        lastTimeRef.current = time;

        const nextIndex = Math.min(indexRef.current + charsToAdd, fullText.length);
        indexRef.current = nextIndex;
        setDisplayed(fullText.slice(0, nextIndex));

        if (nextIndex < fullText.length) {
          rafRef.current = requestAnimationFrame(animate);
        }
      } else {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [fullText, speed]);

  return displayed;
}
