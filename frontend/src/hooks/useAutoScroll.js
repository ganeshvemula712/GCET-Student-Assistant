import { useEffect, useRef, useState, useCallback, useLayoutEffect } from "react";

export default function useAutoScroll({ enabled, dependency, messageCount }) {
  const containerRef = useRef(null);
  const bottomSentinelRef = useRef(null);
  const userHasScrolledUpRef = useRef(false);
  const isProgrammaticScrollRef = useRef(false);
  const programmaticTimeoutRef = useRef(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  // Deterministic scroll function targeting exact maxScroll of containerRef
  const scrollToBottom = useCallback((behavior = "auto") => {
    const container = containerRef.current;
    if (!container) return;

    isProgrammaticScrollRef.current = true;
    if (programmaticTimeoutRef.current) {
      clearTimeout(programmaticTimeoutRef.current);
    }

    const maxScroll = Math.max(0, container.scrollHeight - container.clientHeight);
    if (maxScroll > 0) {
      if (behavior === "smooth") {
        container.scrollTo({ top: maxScroll, behavior: "smooth" });
      } else {
        container.scrollTop = maxScroll;
      }
    }

    // Keep programmatic guard active for 300ms to absorb layout reflows & browser scroll clamping
    programmaticTimeoutRef.current = setTimeout(() => {
      isProgrammaticScrollRef.current = false;
    }, 300);
  }, []);

  // Monitor scroll events: Only mark userHasScrolledUp on genuine manual upward user scrolls
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let prevScrollTop = container.scrollTop;

    const handleScroll = () => {
      // Ignore all scroll events during programmatic scrolling
      if (isProgrammaticScrollRef.current) {
        prevScrollTop = container.scrollTop;
        userHasScrolledUpRef.current = false;
        setIsAtBottom(true);
        return;
      }

      const currentScrollTop = container.scrollTop;
      const distanceFromBottom =
        container.scrollHeight - currentScrollTop - container.clientHeight;

      const nearBottom = distanceFromBottom < 60;

      // User manually scrolled UP if scrollTop decreased significantly away from bottom
      if (currentScrollTop < prevScrollTop - 25 && !nearBottom) {
        userHasScrolledUpRef.current = true;
        setIsAtBottom(false);
      } else if (nearBottom) {
        userHasScrolledUpRef.current = false;
        setIsAtBottom(true);
      }

      prevScrollTop = currentScrollTop;
    };

    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  // Force scroll to bottom and clear locks when a new question is submitted or messageCount changes
  useEffect(() => {
    userHasScrolledUpRef.current = false;
    setIsAtBottom(true);
    scrollToBottom("auto");
  }, [messageCount, scrollToBottom]);

  // Force scroll to bottom when streaming state starts
  useEffect(() => {
    if (enabled) {
      userHasScrolledUpRef.current = false;
      setIsAtBottom(true);
      scrollToBottom("auto");
    }
  }, [enabled, scrollToBottom]);

  // Synchronous layout effect for live streaming chunks & ResizeObserver for DOM renders
  useLayoutEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    if (!userHasScrolledUpRef.current) {
      scrollToBottom("auto");
    }

    const resizeObserver = new ResizeObserver(() => {
      if (!userHasScrolledUpRef.current) {
        scrollToBottom("auto");
      }
    });

    Array.from(container.children).forEach((child) => {
      resizeObserver.observe(child);
    });
    resizeObserver.observe(container);

    return () => resizeObserver.disconnect();
  }, [enabled, dependency, scrollToBottom]);

  return {
    containerRef,
    bottomSentinelRef,
    isAtBottom,
    scrollToBottom: (behavior = "smooth") => {
      userHasScrolledUpRef.current = false;
      setIsAtBottom(true);
      scrollToBottom(behavior);
    },
  };
}
