# FormSaathi — Design Direction

## Personality
**Friendly, cheerful, trustworthy — "Pastel Pro".** Soft pastel colour and cute illustrations on a clean, professional
structure. Think "a calm senior who has filled these forms before", not "a government portal" and not "a toy app".

## Colour tokens

| Token | Value | Use |
|-------|-------|-----|
| `--fs-primary` | `#6A4CF0` violet | Primary actions, links, active nav (5.4:1 with white) |
| `--fs-grad` | `#6A4CF0 → #9B4DEB → #CF3570` | Surfaces that carry white text: hero CTA band, auth panel, welcome banner, gradient headline text. Every stop is ≥ 4.5:1 with white. |
| `--fs-grad-candy` | `#7C5CFC → #B86BFF → #FF8FB1` | Decoration only (no text on top): progress bars, card accent strips, logo, illustrations |
| `--fs-grad-soft` | lavender → lilac → blush mist | Section backgrounds, footer |
| `--fs-bg` | `#FBFAFF` | App background (lavender-white) |
| `--fs-surface` | `#FFFFFF` | Cards, modals |
| `--fs-text` / `--fs-muted` | `#1B1740` / `#6B6887` | Body text (16:1) / secondary text (5.1:1) |
| `--fs-border` | `#ECE8F8` | Hairlines |
| success / warning / danger | `#097554` / `#A15C00` / `#C02A33` on their tints | Status — always with icon + label |

Pastel category tints (background / ink, all ink-on-tint pairs ≥ 4.5:1): lavender `#EFEAFF/#5338D6`, sky `#E3F4FF/#0B6BA8`,
lilac `#F6E8FF/#8A2EC0`, mint `#E1F8EF/#097554`, peach `#FFE8EE/#C2255C`, butter `#FFF4D6/#8A4E00`, sand `#FFEBDD/#A8430B`.
Each category also has a candy accent (`--accent-*`) used for the 5px strip on opportunity cards.

All text pairs were checked with a WCAG contrast calculation, not by eye.

**Dark mode:** bg `#0E0C1F`, surface `#17142E`, text `#EEEBFF`, muted `#A9A4C9`, primary lifts to `#A08CFF`; tints become
translucent; illustration colours switch through `--ill-*` variables.

**Status badges** — always text + icon, never colour alone:
- `Verified` ✓ mint · `Demo` flask lilac · `Pending verification` clock butter · `Expired` muted · `AI guidance` sparkles violet.

## Illustrations
Custom inline SVG (no stock images, no licensing issues), coloured through `--ill-*` CSS variables so they adapt to dark mode:
`components/art/HeroScene.vue` (student with laptop + floating scholarship / eligibility / deadline / checklist cards) and
`components/art/SpotArt.vue` (profile, discover, checklist, track, student, jobseeker, family, celebrate). Gentle float and
twinkle animations respect `prefers-reduced-motion`.

## Typography
- **Plus Jakarta Sans** for headings (600/700/800); **Inter** for UI & body (400/500/600).
- Scale (rem): 3.5 / 2.75 / 2 / 1.5 / 1.25 / 1.0625 (body) / 0.9375 / 0.8125. Fluid `clamp()` for hero.
- Line-height 1.6 body, 1.15 display. Hindi/Marathi fallback: **Noto Sans Devanagari**, with +0.05 line-height.

## Shape, depth, motion
- Radius: 13 (inputs), 14 (buttons; pills for hero CTAs), 20 (cards), 28 (banners), 999 (chips).
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
A rounded-square **violet → orchid → pink gradient** mark containing a **white document with a violet check and a yellow spark** — the document = forms, the spark = "the opportunity you found", the rounded shape = friendliness. Wordmark "Form**Saathi**" in Plus Jakarta Sans 800 with "Saathi" in indigo. Delivered as SVG (Phase 2) + favicon set.

## Components (built in Phase 2)
Button (primary/secondary/ghost/danger, sizes, loading), IconButton, Badge/StatusBadge, Chip, Card, OpportunityCard, StatCard, ProgressRing, Stepper, Input/Select/Textarea with help + error text, SearchBar, FilterPanel / BottomSheet, Modal, Tabs, Accordion (FAQ), Toast, Tooltip, Skeleton, EmptyState (with illustration), ErrorState, Avatar, Timeline, KanbanColumn, Sidebar, TopBar, MobileTabBar, LanguageSwitcher, ThemeToggle.

## Accessibility
WCAG 2.2 AA: contrast checked on every token pair, visible focus ring (`0 0 0 3px rgba(55,48,163,.35)`), semantic landmarks, labelled form controls, `aria-live` for toasts and chat, full keyboard navigation for board/tabs/modals, `lang` attribute switched with language.
