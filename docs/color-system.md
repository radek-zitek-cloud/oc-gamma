# Color System Specification

> Design token reference for implementing light and dark themes. This document defines which tokens to use on every component type to achieve a consistent, polished UI across both modes.

---

## 1. Token Architecture

The palette uses HSL values as CSS custom properties. Every color is defined twice — once for `:root` (light) and once for `.dark` (dark). Components reference tokens, never raw values, so theme switching is automatic.

### 1.1 Token Categories

| Category | Tokens | Purpose |
|---|---|---|
| **Surface** | `background`, `card`, `popover`, `secondary`, `muted` | Page and container backgrounds |
| **Content** | `foreground`, `card-foreground`, `popover-foreground`, `secondary-foreground`, `muted-foreground` | Text and icon colors |
| **Brand** | `primary`, `primary-foreground`, `accent`, `accent-foreground` | Interactive elements, emphasis |
| **Semantic** | `destructive`, `success`, `warning`, `info` + their `-foreground` pairs | Status, feedback, alerts |
| **Form** | `input`, `border`, `ring` | Input fields, dividers, focus states |

### 1.2 Light Mode Values

```css
:root {
  --background: 0 0% 100%;         /* #FFFFFF — page background */
  --foreground: 345 6% 13%;        /* #221F20 — primary text */
  --card: 0 0% 100%;               /* #FFFFFF — card surfaces */
  --card-foreground: 345 6% 13%;   /* #221F20 — card text */
  --popover: 0 0% 100%;            /* #FFFFFF — dropdown/popover bg */
  --popover-foreground: 345 6% 13%;/* #221F20 — popover text */
  --primary: 45 73% 65%;           /* #E2B94E — gold, primary actions */
  --primary-foreground: 345 6% 13%;/* #221F20 — text on primary */
  --secondary: 0 0% 96%;           /* #F5F5F5 — secondary surfaces */
  --secondary-foreground: 345 6% 13%; /* #221F20 — text on secondary */
  --muted: 0 0% 96%;               /* #F5F5F5 — muted backgrounds */
  --muted-foreground: 0 0% 45%;    /* #737373 — subdued text */
  --accent: 0 0% 96%;              /* #F5F5F5 — accent surface */
  --accent-foreground: 45 73% 40%; /* #B18A1D — accent text/icons */
  --destructive: 0 84% 60%;        /* #EF4444 — error/danger */
  --destructive-foreground: 0 0% 98%; /* #FAFAFA — text on destructive */
  --success: 142 71% 29%;          /* #15803D — success */
  --success-foreground: 0 0% 98%;  /* #FAFAFA — text on success */
  --warning: 38 92% 50%;           /* #F59E0B — warning */
  --warning-foreground: 0 0% 98%;  /* #FAFAFA — text on warning */
  --info: 210 100% 50%;            /* #0066FF — informational */
  --info-foreground: 0 0% 98%;     /* #FAFAFA — text on info */
  --border: 0 0% 90%;              /* #E5E5E5 — dividers, borders */
  --input: 0 0% 90%;               /* #E5E5E5 — input borders */
  --ring: 45 73% 65%;              /* #E2B94E — focus ring */
  --radius: 0.5rem;                /* default border-radius */
}
```

### 1.3 Dark Mode Values

```css
.dark {
  --background: 345 6% 7%;         /* #121011 — page background */
  --foreground: 0 0% 98%;          /* #FAFAFA — primary text */
  --card: 345 6% 10%;              /* #1A1718 — card surfaces */
  --card-foreground: 0 0% 98%;     /* #FAFAFA — card text */
  --popover: 345 6% 10%;           /* #1A1718 — dropdown/popover bg */
  --popover-foreground: 0 0% 98%;  /* #FAFAFA — popover text */
  --primary: 45 73% 65%;           /* #E2B94E — gold, stays constant */
  --primary-foreground: 345 6% 7%; /* #121011 — dark text on gold */
  --secondary: 345 6% 13%;         /* #221F20 — secondary surfaces */
  --secondary-foreground: 0 0% 98%;/* #FAFAFA — text on secondary */
  --muted: 345 5% 15%;             /* #272324 — muted backgrounds */
  --muted-foreground: 0 0% 64%;    /* #A3A3A3 — subdued text */
  --accent: 45 73% 40%;            /* #B18A1D — deeper gold accent */
  --accent-foreground: 0 0% 98%;   /* #FAFAFA — text on accent */
  --destructive: 0 84% 65%;        /* #F87171 — error (lighter for dark bg) */
  --destructive-foreground: 0 0% 98%;
  --success: 142 71% 45%;          /* #22C55E — success (lighter) */
  --success-foreground: 0 0% 98%;
  --warning: 38 92% 55%;           /* #F6A723 — warning (lighter) */
  --warning-foreground: 0 0% 98%;
  --info: 210 100% 55%;            /* #3388FF — info (lighter) */
  --info-foreground: 0 0% 98%;
  --border: 345 5% 20%;            /* #343031 — dividers */
  --input: 345 5% 20%;             /* #343031 — input borders */
  --ring: 45 73% 65%;              /* #E2B94E — focus ring */
}
```

### 1.4 Design Principles

The palette has three distinctive characteristics that must be preserved:

1. **Warm neutrals** — Dark mode backgrounds and borders carry `hsl(345, 5-6%, …)`, giving them a slight rosy warmth instead of pure gray. Never substitute pure gray (`0, 0%, …`) in dark mode surfaces.
2. **Constant gold primary** — `--primary` is the same value in both modes (`45 73% 65%`). It is the hero color and should be used sparingly for maximum impact.
3. **Semantic lightness shift** — Semantic colors (destructive, success, warning, info) are 5–16% lighter in dark mode to maintain perceived contrast against dark backgrounds.

---

## 2. CSS Usage Pattern

Always reference tokens via `hsl()`:

```css
.element {
  background: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border: 1px solid hsl(var(--border));
}
```

For alpha transparency, use `hsl()` with `/`:

```css
.overlay {
  background: hsl(var(--primary) / 0.12);
}

.glass-panel {
  background: hsl(var(--card) / 0.8);
  backdrop-filter: blur(12px);
}
```

---

## 3. Component Token Mapping

### 3.1 Page Layout

| Element | Background | Text | Border |
|---|---|---|---|
| Page body | `--background` | `--foreground` | — |
| Top navigation bar | `--card` | `--foreground` | `--border` (bottom) |
| Sidebar | `--card` | `--foreground` | `--border` (right) |
| Section dividers | — | — | `--border` |
| Footer | `--secondary` | `--muted-foreground` | `--border` (top) |

### 3.2 Cards and Containers

| Element | Background | Text | Border |
|---|---|---|---|
| Card surface | `--card` | `--card-foreground` | `--border` |
| Card title | — | `--foreground` (font-weight 600) | — |
| Card subtitle / description | — | `--muted-foreground` | — |
| Nested container / well | `--muted` | `--foreground` | — |
| Elevated card | `--card` | `--card-foreground` | `--border` + shadow |

Card shadow recipe:
- Light mode: `box-shadow: 0 1px 3px hsl(var(--foreground) / 0.08)`
- Dark mode: `box-shadow: 0 1px 3px hsl(0 0% 0% / 0.3)`

### 3.3 Typography

| Element | Color | Notes |
|---|---|---|
| Headings (h1–h3) | `--foreground` | Weight 600–700, tight letter-spacing |
| Body text | `--foreground` | Weight 400, standard line-height |
| Secondary / helper text | `--muted-foreground` | Smaller font size (11–12px) |
| Labels | `--muted-foreground` | Weight 500, uppercase optional |
| Links | `--accent-foreground` | Underline on hover |
| Monospace / code values | `--foreground` | Use monospace font family |
| Disabled text | `--muted-foreground` | Opacity 0.5 |

### 3.4 Buttons

#### Primary Button (call-to-action)
```
background: --primary
color: --primary-foreground
border: none
shadow: 0 1px 3px hsl(var(--primary) / 0.4)
hover: opacity 0.85
active: opacity 0.75
```

#### Secondary Button
```
background: --secondary
color: --secondary-foreground
border: 1px solid --border
hover: opacity 0.75
```

#### Ghost Button
```
background: transparent
color: --foreground
border: none
hover background: --muted
```

#### Destructive Button
```
background: --destructive
color: --destructive-foreground
border: none
hover: opacity 0.85
```

#### Outline Button
```
background: transparent
color: --foreground
border: 1px solid --border
hover background: --muted
```

All buttons use `border-radius: var(--radius)`.

### 3.5 Form Inputs

#### Text Input / Number Input / Textarea / Date Picker
```
background: --background
color: --foreground
border: 1px solid --input
border-radius: var(--radius)
placeholder-color: --muted-foreground
```

Focus state:
```
border-color: --ring
box-shadow: 0 0 0 3px hsl(var(--ring) / 0.2)
```

#### Select / Dropdown
Same as text input plus:
```
caret/chevron icon: --muted-foreground
option-hover background: --muted
```

#### Input Labels
```
color: --muted-foreground
font-size: 12px
font-weight: 500
margin-bottom: 4–6px
```

#### Input with Icon (e.g., search)
```
icon color: --muted-foreground
icon position: absolute, inside left padding
input padding-left: increased to accommodate icon
```

#### Error State
```
border-color: --destructive
box-shadow: 0 0 0 3px hsl(var(--destructive) / 0.15)
error message color: --destructive
```

#### Disabled State
```
background: --muted
color: --muted-foreground
opacity: 0.5
cursor: not-allowed
```

### 3.6 Toggle Switch

```
Track OFF:  background --input
Track ON:   background --primary
Thumb OFF:  background --muted-foreground
Thumb ON:   background --primary-foreground
Transition: 200ms on left position and background
```

### 3.7 Checkbox

```
Unchecked:  border 1.5px solid --input, background transparent
Checked:    background --primary, border none
Checkmark:  stroke --primary-foreground, weight 3
```

### 3.8 Radio / Segmented Control / Pill Selector

```
Inactive:   border 1px solid --border, background transparent, color --muted-foreground
Active:     border 2px solid --primary, background hsl(var(--primary) / 0.08–0.12), color --primary
```

### 3.9 Filter Chips / Tags

```
Inactive:   border 1px solid --border, background transparent, color --muted-foreground
Active:     background --primary, color --primary-foreground, border none
```

### 3.10 Range Slider

```
Track filled:   --primary
Track unfilled: --input
Thumb:          --primary (with --primary-foreground for inner dot if applicable)
```

### 3.11 Dropdowns and Popovers

```
background: --popover
color: --popover-foreground
border: 1px solid --border
shadow: 0 4px 16px hsl(var(--foreground) / 0.08) [light]
        0 4px 16px hsl(0 0% 0% / 0.4) [dark]
item-hover background: --muted
separator: --border
```

### 3.12 Tables

| Element | Background | Text | Border |
|---|---|---|---|
| Table header row | — | `--muted-foreground` | `--border` (bottom) |
| Table header text | — | `--muted-foreground`, weight 600, uppercase, 11px, letter-spacing 0.04em | — |
| Table body row | — | `--foreground` | `--border` (bottom, except last) |
| Row hover | `--muted` | — | — |
| Monospace values (amounts, IDs) | — | `--foreground`, monospace font | — |

### 3.13 Status Badges

Pattern: Low-opacity background of the semantic color, full-opacity text.

```
background: hsl(var(--{status}) / 0.08–0.12)
color: --{status}
padding: 2px 8px
border-radius: 6px
font-size: 11px
font-weight: 600
```

Where `{status}` is one of: `success`, `warning`, `destructive`, `info`.

Examples:
- Active: `background: hsl(var(--success) / 0.1)`, `color: --success`
- Review: `background: hsl(var(--warning) / 0.1)`, `color: --warning`
- Blocked: `background: hsl(var(--destructive) / 0.1)`, `color: --destructive`
- Pending: `background: hsl(var(--info) / 0.1)`, `color: --info`

### 3.14 Status Indicators (Dots)

```
color: --success | --warning | --destructive | --info
width/height: 7–8px
border-radius: 50%
box-shadow: 0 0 6px hsl(var(--{status}) / 0.4)   /* subtle glow */
```

Accompanying label: `--muted-foreground`, 12px.

### 3.15 Charts and Data Visualization

| Chart Element | Color(s) |
|---|---|
| Primary bars / lines / arcs | `--primary` |
| Secondary data series | `--info` |
| Tertiary series | `--success` |
| Quaternary series | `--warning` |
| Bar alternation (same series) | `--primary` at 100% and 60% opacity |
| Axis labels / tick marks | `--muted-foreground` |
| Grid lines | `--border` |
| Tooltip background | `--popover` |
| Tooltip text | `--popover-foreground` |
| Sparklines | `--primary` stroke, no fill |

For donut / pie charts, use this order: `--primary`, `--info`, `--success`, `--warning`, then `--accent-foreground` if more segments are needed.

### 3.16 Heatmaps and Activity Grids

```
Empty / zero cells:  --muted at 50% opacity
Low intensity:       hsl(45, 73%, 30%) at 40% opacity
Medium intensity:    hsl(45, 73%, 50%) at 65% opacity
High intensity:      hsl(45, 73%, 70%) at 90% opacity
```

Build from the primary hue (45) and saturation (73%) with varying lightness and opacity.

### 3.17 Navigation & Branding

| Element | Styling |
|---|---|
| Logo container | `background: --primary`, `color: --primary-foreground`, border-radius 8px |
| App name | `--foreground`, weight 600 |
| Nav badge / label | `background: hsl(var(--primary) / 0.12–0.15)`, `color: --accent-foreground` |
| Avatar ring | `border: 2px solid --border` |
| Avatar gradient | `linear-gradient(135deg, --primary, --accent-foreground)` |

### 3.18 Alerts and Toasts

Full-width alert pattern:

```
background: hsl(var(--{status}) / 0.08)
border-left: 4px solid --{status}
color: --foreground
icon color: --{status}
```

Toast / notification:

```
background: --card
border: 1px solid --border
shadow: elevated
icon color: --{status}
title: --foreground
description: --muted-foreground
```

### 3.19 Modals and Dialogs

```
Overlay:     hsl(0 0% 0% / 0.5) [light], hsl(0 0% 0% / 0.7) [dark]
Dialog:      background --card, border --border, border-radius calc(var(--radius) * 2)
Title:       --foreground, weight 600
Description: --muted-foreground
Divider:     --border
```

### 3.20 Skeleton / Loading States

```
background: --muted
shimmer: linear-gradient(90deg, transparent, hsl(var(--primary) / 0.06), transparent)
border-radius: var(--radius)
```

### 3.21 Scrollbars (WebKit)

```
track: --muted
thumb: --border
thumb:hover: --muted-foreground
width: 6–8px
```

---

## 4. Opacity and Alpha Conventions

When you need transparent variants of any token, use consistent alpha levels:

| Purpose | Alpha | Example |
|---|---|---|
| Subtle tint / badge background | 0.08–0.12 | `hsl(var(--primary) / 0.1)` |
| Hover highlight | 0.06–0.10 | `hsl(var(--primary) / 0.08)` |
| Focus ring glow | 0.15–0.25 | `hsl(var(--ring) / 0.2)` |
| Button shadow | 0.30–0.40 | `hsl(var(--primary) / 0.4)` |
| Card shadow (light) | 0.06–0.10 | `hsl(var(--foreground) / 0.08)` |
| Card shadow (dark) | 0.25–0.40 | `hsl(0 0% 0% / 0.3)` |
| Overlay / scrim | 0.50–0.70 | `hsl(0 0% 0% / 0.5)` |
| Disabled | 0.50 | Applied via `opacity: 0.5` on the element |

---

## 5. Spacing and Radius

- **Border radius**: Use `var(--radius)` (0.5rem / 8px) as the base. Double it for modals and larger containers. Halve it for small badges and chips.
- **Card padding**: 16–20px.
- **Form field padding**: 9–12px vertical, 12px horizontal.
- **Grid gap**: 12–16px between cards, 8–12px between form fields.
- **Section margin-bottom**: 24px.

---

## 6. Dark Mode–Specific Rules

1. **Never use pure black** (`#000000`) for backgrounds. The darkest surface is `--background` at `345 6% 7%`.
2. **Elevation = lightness** in dark mode. Raised elements are *lighter* than their parent:
   - Page: `--background` (7% lightness)
   - Card: `--card` (10% lightness)
   - Muted / well: `--muted` (15% lightness)
   - Border / input: `--border` / `--input` (20% lightness)
3. **Shadows are deeper** in dark mode. Increase shadow opacity by ~2× compared to light mode.
4. **Text is never pure white.** Maximum is `--foreground` at `0 0% 98%`.
5. **Semantic colors are boosted.** They shift 5–16 lightness points brighter to maintain legibility against dark surfaces.
6. **The primary gold does not change** between modes. If it visually dominates too much in dark mode, reduce its area rather than its saturation.

---

## 7. Accessibility Notes

- **Contrast ratios**: `--foreground` on `--background` meets WCAG AAA in both modes. `--muted-foreground` on `--background` meets AA. Verify `--primary` on `--background` for large text only (it passes AA Large).
- **Focus indicators**: The `--ring` focus glow must be visible in both themes. The 3px spread at 20% opacity is tuned for this.
- **Color alone**: Never convey status by color alone. Pair status colors with icons, labels, or patterns.
- **Motion**: All state transitions should respect `prefers-reduced-motion`.

---

## 8. Anti-Patterns — Do Not

1. ❌ Use `--primary` for large background fills (cards, sections, pages). It is too saturated. Use it only for buttons, badges, focus rings, chart accents, and small highlights.
2. ❌ Mix raw hex/hsl values alongside tokens. Everything must go through `var(--token)` for theme switching to work.
3. ❌ Use `--foreground` where `--muted-foreground` is appropriate (labels, timestamps, secondary info). This creates visual noise.
4. ❌ Use `--border` for text or `--muted-foreground` for borders. Each token has a specific purpose.
5. ❌ Apply `--destructive` for non-error purposes. Reserve semantic colors strictly for their semantic meaning.
6. ❌ Put light text on `--primary` in light mode. The primary-foreground in light mode is dark (`345 6% 13%`), not white.
7. ❌ Use pure gray (`0 0% X%`) for dark mode surfaces. Always use the warm hue `345 5–6%` to preserve palette warmth.
8. ❌ Apply the same shadow values in both modes. Dark mode needs higher opacity, and optionally slightly larger spread.
9. ❌ Forget the focus ring on interactive elements. Every focusable element must show `--ring` with a glow on `:focus-visible`.
10. ❌ Use `--accent-foreground` interchangeably with `--primary`. In light mode, `accent-foreground` is a deeper gold (`40%` lightness vs `65%`) — use it for text on neutral backgrounds where `--primary` would be too light to read.