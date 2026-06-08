// @journeyos/shared/ui-tokens — Wave-0 API surface (stub).
// Design tokens da plataforma (a migrar dos tokens de design do projeto). Fonte única de valores.

export const tokens = {
  color: {
    surface: 'var(--jos-color-surface, #ffffff)',
    text: 'var(--jos-color-text, #1a1a1a)',
    primary: 'var(--jos-color-primary, #3b5bdb)',
    success: 'var(--jos-color-success, #2f9e44)',
    warning: 'var(--jos-color-warning, #f08c00)',
    error: 'var(--jos-color-error, #e03131)',
  },
  space: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
} as const;

export type Tokens = typeof tokens;
