# FormSaathi — Design Direction

## Personality
**Friendly, intelligent, trustworthy.** Think "a calm senior who has filled these forms before", not "a government portal" and not "a toy app". Clean, airy surfaces; small warm moments (micro-illustrations, a coral accent on the one action that matters).

## Colour tokens

| Token | Hex | Use |
|-------|-----|-----|
| `--fs-primary` | `#3730A3` Deep Indigo | Primary buttons, active nav, links, logo |
| `--fs-primary-600` | `#4338CA` | Hover |
| `--fs-primary-50` | `#EEF2FF` | Subtle fills, selected rows |
| `--fs-secondary` | `#EDE9FE` Soft Lavender | Card tints, chips, illustration backgrounds |
| `--fs-accent` | `#FB7185` Warm Coral | **One** highlight per view: deadlines-soon, "new", key CTA flourish |
| `--fs-bg` | `#F8FAFC` | App background |
| `--fs-surface` | `#FFFFFF` | Cards, modals |
| `--fs-text` | `#172033` | Body text |
| `--fs-muted` | `#64748B` | Secondary text |
| `--fs-border` | `#E2E8F0` | Hairlines |
| `--fs-success` | `#16A34A` | Eligible, verified, approved |
| `--fs-warning` | `#F59E0B` | Possibly eligible, deadline ≤ 7 days |
| `--fs-danger` | `#DC2626` | Not eligible, errors (used sparingly) |

Pastel support tints for category cards (each paired with a darker icon colour for contrast ≥ 4.5:1): lavender, mint `#DCFCE7`, sky `#E0F2FE`, peach `#FFE4E6`, butter `#FEF3C7`, lilac `#F3E8FF`, sand `#F5F5F4`.

**Dark mode:** bg `#0B1020`, surface `#121933`, text `#E6E8F2`, muted `#94A3B8`, primary lifts to `#818CF8` for contrast; lavender tints become `rgba(129,140,248,.12)`.

**Status badges** — always text + icon, never colour alone:
- `Verified` ✓ green · `Demo` flask-icon lavender · `Pending verification` clock amber · `Expired` muted grey · `AI guidance` sparkles indigo.

## Typography
- **Plus Jakarta Sans** for headings (600/700/800); **Inter** for UI & body (400/500/600).
- Scale (rem): 3.5 / 2.75 / 2 / 1.5 / 1.25 / 1.0625 (body) / 0.9375 / 0.8125. Fluid `clamp()` for hero.
- Line-height 1.6 body, 1.15 display. Hindi/Marathi fallback: **Noto Sans Devanagari**, with +0.05 line-height.

## Shape, depth, motion
- Radius: 8 (inputs), 12 (buttons), 16 (cards), 24 (hero panels), 999 (chips).
- Shadows (indigo-tinted, soft): `sm 0 1px 2px rgba(23,32,51,.06)`, `md 0 4px 16px -4px rgba(55,48,163,.10)`, `lg 0 16px 40px -12px rgba(55,48,163,.18)`.
- Motion: 150 ms (hover), 220 ms (panels), `cubic-bezier(.2,.8,.2,1)`. Cards lift 2px on hover. Respects `prefers-reduced-motion`.
- No heavy gradients, no glassmorphism beyond a 1-layer translucent navbar on scroll, no neon.

## Spacing & layout
- 4-px base grid; section padding 96px desktop / 56px mobile.
- Container max 1200px (marketing), app content max 1280px.
- Breakpoints tested: **360, 390, 768, 1024, 1440**.
  - < 768: bottom tab bar (Home, Discover, Tracker, Saathi, More), filters in a bottom sheet, tables become stacked cards, modals become full-height sheets.
  - 768–1023: collapsed icon sidebar.
  - ≥ 1024: full sidebar (collapsible).
- Touch targets ≥ 44 px.

## Logo concept
A rounded-square indigo mark containing a **stylised form/document whose top-right corner folds into a coral spark** — the document = forms, the spark = "the opportunity you found", the rounded shape = friendliness. Wordmark "Form**Saathi**" in Plus Jakarta Sans 800 with "Saathi" in indigo. Delivered as SVG (Phase 2) + favicon set.

## Components (built in Phase 2)
Button (primary/secondary/ghost/danger, sizes, loading), IconButton, Badge/StatusBadge, Chip, Card, OpportunityCard, StatCard, ProgressRing, Stepper, Input/Select/Textarea with help + error text, SearchBar, FilterPanel / BottomSheet, Modal, Tabs, Accordion (FAQ), Toast, Tooltip, Skeleton, EmptyState (with illustration), ErrorState, Avatar, Timeline, KanbanColumn, Sidebar, TopBar, MobileTabBar, LanguageSwitcher, ThemeToggle.

## Accessibility
WCAG 2.2 AA: contrast checked on every token pair, visible focus ring (`0 0 0 3px rgba(55,48,163,.35)`), semantic landmarks, labelled form controls, `aria-live` for toasts and chat, full keyboard navigation for board/tabs/modals, `lang` attribute switched with language.
