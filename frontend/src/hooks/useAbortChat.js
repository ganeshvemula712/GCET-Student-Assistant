import { useCallback, useRef } from "react";

export default function useAbortChat() {
  const controllerRef = useRef(null);

  const createController = useCallback(() => {
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    return controller;
  }, []);

  const abortActiveRequest = useCallback(() => {
    if (controllerRef.current) {
      controllerRef.current.abort();
      controllerRef.current = null;
    }
  }, []);

  const clearController = useCallback(() => {
    controllerRef.current = null;
  }, []);

  return {
    createController,
    abortActiveRequest,
    clearController,
  };
}
