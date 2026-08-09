import { useEffect, useRef, useState, useCallback } from "react";

export default function useAutoScroll({ enabled, dependency }) {
  const containerRef = useRef(null);
  const bottomSentinelRef = useRef(null);
  const shouldAutoScrollRef = useRef(true);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const scrollToBottom = useCallback((behavior = "smooth") => {
    if (bottomSentinelRef.current) {
      bottomSentinelRef.current.scrollIntoView({ behavior, block: "end" });
    } else if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior,
      });
    }
  }, []);

  // Handle scroll events to detect user manual scroll upward
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const distanceFromBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight;

      const nearBottom = distanceFromBottom < 100;
      shouldAutoScrollRef.current = nearBottom;
      setIsAtBottom(nearBottom);
    };

    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  // Trigger auto-scroll on dependency change or when streaming enabled
  useEffect(() => {
    if (!enabled) return;

    if (shouldAutoScrollRef.current) {
      scrollToBottom(dependency ? "auto" : "smooth");
    }
  }, [enabled, dependency, scrollToBottom]);

  // Initial scroll when conversation changes
  useEffect(() => {
    scrollToBottom("auto");
  }, [dependency, scrollToBottom]);

  return {
    containerRef,
    bottomSentinelRef,
    isAtBottom,
    scrollToBottom,
  };
}
