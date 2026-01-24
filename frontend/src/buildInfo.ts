/**
 * Purpose: Expose build metadata in the UI.
 * Why: Makes it obvious the deployed site is running the newest pushed code.
 */
export const BUILD_SHA = (import.meta.env.VITE_BUILD_SHA || "dev").slice(0, 7);
export const BUILD_TIME_UTC = import.meta.env.VITE_BUILD_TIME_UTC || "dev";
