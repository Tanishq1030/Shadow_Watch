export const ANIMATION_BUDGET = {
    // Max typing terminals per page
    maxTypingTerminals: 2,

    // Max characters before fallback to line reveal
    maxTypingChars: 800,

    // Page transition duration (ms)
    pageTransitionMs: 500,

    // Typing speed (ms per character)
    typingSpeed: 40,

    // Hover effect duration (ms)
    hoverDurationMs: 200,

    // Max total motion time per page (ms)
    maxMotionTimeMs: 1200,
} as const;
