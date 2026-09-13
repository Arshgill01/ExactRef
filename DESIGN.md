# Design

## Scene
Records clerk under cool fluorescent light. The only color that earns its keep is the mismatch mark.

## Color strategy
Restrained. Pure white surface. Brand hue 140 (moss) for verified / primary action only. Mismatch uses a separate crimson, not a tinted green.

```css
:root {
  --bg: oklch(1 0 0);
  --surface: oklch(0.965 0.004 140);
  --ink: oklch(0.22 0.018 140);
  --muted: oklch(0.46 0.02 140);
  --line: oklch(0.88 0.012 140);
  --primary: oklch(0.36 0.09 140);
  --primary-ink: oklch(0.99 0.005 140);
  --accent: oklch(0.44 0.16 25);
  --accent-ink: oklch(0.99 0.01 25);
  --warn: oklch(0.5 0.12 75);
  --ok: oklch(0.4 0.08 140);
}
```

## Typography
IBM Plex Sans for UI. IBM Plex Mono for identifiers and diffs. Fixed rem scale (14 / 16 / 18 / 22). Identifiers at 22–28px mono. No display fonts. No Inter, Roboto, or Arial.

## Layout
Top bar 48px. Case list 240px. Workspace fills the rest. Identifier pair is the largest object. Evidence is a single quoted span, not a card stack. No hero. No metric tiles.

## Motion
160ms color/opacity only. Character-diff marks appear instantly under reduced motion.

## Components
Text buttons and one solid primary. 8px radius. 1px borders. Native dialog for live confirm. Focus ring 2px `--primary`.
