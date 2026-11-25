# FormSaathi — Design Direction

## Personality
**Calm, warm, professional — "Paper & Pastel cards".** A warm photographic homepage, paper and ink neutrals,
and white cards with a soft pastel top and a deep-coloured number. Simple enough for a first-time user, polished
enough to trust with an application. Think "a calm senior who has filled these forms before", not "a government
portal" and not "a toy app".

## Homepage
1. **Photo hero** — a sunlit desk (laptop, notebook, cane chair, window light on the wall) behind a centred serif
   headline with an italic accent word, a short line, and a pill search bar. The navbar is transparent over the photo
   until the page scrolls. A cream wash keeps the text readable (headline ≥ 13:1, accent ≥ 4.1:1 at the photo's
   darkest point). Images: `src/assets/hero/hero-desk-1920.webp` (66 KB) and `hero-desk-900.webp` (19 KB, mobile).
2. **Band** — dark ink strip: "Discover | Check | Apply" and a "Join FormSaathi" outline button.
3. **About** — "*About* FormSaathi" and four plates. Every number is live: verified listings open today (from the
   API), kinds of eligibility rules checked and ATS checks (counted from the code), languages.
4. **Categories**, **How it works** (01–04), **Open right now** (featured listings), **FAQ**, closing call to action.

**Photo credit:** "Chair and Table in a Room with Shadow of Window on Wall" by Hanna Pad on Pexels
(https://www.pexels.com/photo/chair-and-table-in-a-room-with-shadow-of-window-on-wall-8534460/), used under the
Pexels License (free to use and modify; attribution not required but given here).

## Colour palette
All values live in `frontend/src/styles/_palette.scss`, emitted as CSS variables with the same names as the design's
Tailwind `@theme` (`--color-paper`, `--color-lavender-500` …). Components only use role variables (`--fs-bg`,
`--fs-primary`, `--top-mint`, `--status-applied` …), so changing the palette never touches component styles.

| Name | Light | Dark |
|------|-------|------|
| paper / ink | `#fbf9f6` / `#211f2e` | `#18151f` / `#f8f5ef` |
| muted / line | `#6b6879` / `#ebe6df` | `#b7b1c2` / `#393442` |
| lavender 50·100·300·500·700 | `#f4f1ff` `#ebe5ff` `#c3b5fb` `#7c68ee` `#5440c4` | `#28233a` `#352e50` `#796ab3` `#a391ef` `#c2b5ff` |
| peach 50·100·300·500·700 | `#fff4ee` `#ffe6da` `#fbbfa3` `#ec7f58` `#b9502c` | `#352720` `#4a3428` `#df9b79` `#ec9b78` `#ffc2a4` |
| mint 50·100·300·500·700 | `#eefaf4` `#d9f3e6` `#96dcbb` `#2fa676` `#1d7a54` | `#1c3229` `#284838` `#74bf9d` `#57bd91` `#9be1c1` |
| sky 50·100·300·500·700 | `#eef6ff` `#dcecff` `#a6cbf6` `#3f86d8` `#285fa3` | `#1d2a3a` `#27384d` `#7ca8d3` (500 unchanged) `#aecdf1` |
| butter 50·100·300·500·700 | `#fffaea` `#fff2c7` `#f6d77a` `#d9a514` `#94700a` | `#3a3321` `#4c4227` `#dbc27d` (500 unchanged) `#efd992` |

**Roles:** paper = page, ink = text, muted = secondary text, line = hairlines. Each colour family gives a card
**top** wash (50), a **tint** for badges, icon tiles and card borders (100), an **ink** for text on that tint (700)
and an **accent** for dots and strips (500). lilac (lavender × peach) and sand (peach × butter) are blends so all
eight categories differ.

- **Buttons:** dark ink with white text (light mode); cream with dark text (dark mode).
- **Links, active nav, focus:** lavender-700 text, lavender-500 focus ring.
- **Hero accent:** peach-700 italic with a peach-300 hand-drawn underline.
- **Plates (cards):** white, 24 px radius, soft family-coloured top, tinted 1 px border, big number in the family's
  ink (lavender `#5440c4`, mint `#1d7a54`, sky `#285fa3`, butter `#775c13`), white pill tags, dark ink button.
- **Status:** success mint, warning butter, danger peach, info sky — always with icon + label. peach-700 and
  butter-700 lean slightly towards ink for text (`#a2492c`, `#775c13`) because the plain 700s dip under 4.5:1 on
  their own tints.
- **Application status dots** (always next to their label): interested lavender-700, saved sky-500, preparing
  butter-700, ready mint-500, applied lavender-500, under review butter-500, approved mint-700, rejected peach-500 —
  checked with the dataviz palette validator (neighbours ≥ 10 ΔE apart under simulated colour-blindness, ≥ 17 for
  normal vision). "Application progress" bars use one colour; the dots carry the status.

**Contrast:** every text/background pair was computed (WCAG 2.x), not judged by eye — all ≥ 4.5:1 in both modes
(large display text ≥ 3:1); UI edges (focus ring, input borders, progress fills) ≥ 3:1.

**Status badges** — always text + icon, never colour alone:
- `Verified` ✓ mint · `Demo` flask lilac · `Pending verification` clock butter · `Expired` muted · `AI guidance` sparkles lavender.

## Illustrations
The homepage uses one licensed photo (see Homepage). Inside the app, small custom SVG spot illustrations
(`components/art/SpotArt.vue`: profile, discover, checklist, track, student, celebrate …) are coloured through
`--ill-*` variables so they adapt to dark mode. Gentle float animations respect `prefers-reduced-motion`.

## Typography
- **Plus Jakarta Sans** (variable, 200–800) for UI, body text, card titles and big card numbers.
- **Fraunces** (variable, with optical sizes) for display: hero, section and page titles, at a semibold weight, with
  its italic for the accent word ("Starts Here.", "About"). Both self-hosted through Fontsource — no requests to
  Google Fonts. Hindi/Marathi fall back to **Noto Sans Devanagari**, with +0.05 line-height.
- `.lead` is set to 400 (the variable font's real 300 reads too thin in muted grey).
- Fluid `clamp()` sizes; line-height 1.6 body, 1.05–1.15 display.

## Shape, depth, motion
- Radius: 13 (inputs), 14 (buttons; pills for hero CTAs), 20 (cards), 28 (banners), 999 (chips).
- Shadows (soft, ink-tinted): `sm 0 1px 2px rgba(33,31,46,.05)`, `md 0 18px 40px -22px rgba(33,31,46,.28)`, `lg 0 30px 70px -28px rgba(33,31,46,.34)`.
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
A rounded-square **dark ink** mark containing a **white document with a lavender check and a butter spark** — the document = forms, the spark = "the opportunity you found", the rounded shape = friendliness. Fixed hexes, so it looks the same in light and dark mode. Wordmark "Form**Saathi**" in Fraunces 600 with "Saathi" in the lavender → peach gradient. Delivered as SVG + favicon.

## Components (built in Phase 2)
Button (primary/secondary/ghost/danger, sizes, loading), IconButton, Badge/StatusBadge, Chip, Card, OpportunityCard, StatCard, ProgressRing, Stepper, Input/Select/Textarea with help + error text, SearchBar, FilterPanel / BottomSheet, Modal, Tabs, Accordion (FAQ), Toast, Tooltip, Skeleton, EmptyState (with illustration), ErrorState, Avatar, Timeline, KanbanColumn, Sidebar, TopBar, MobileTabBar, LanguageSwitcher, ThemeToggle.

## Accessibility
WCAG 2.2 AA: contrast checked on every token pair, visible focus ring (3px lavender-500 outline, 3.9:1 on paper), semantic landmarks, labelled form controls, `aria-live` for toasts and chat, full keyboard navigation for board/tabs/modals, `lang` attribute switched with language.
