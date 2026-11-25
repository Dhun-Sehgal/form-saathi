# FormSaathi — Design Direction

## Personality
**Friendly, calm, trustworthy — "Paper & Pastel".** Warm paper background, ink text, five soft pastel hues and cute
illustrations on a clean, professional structure. Think "a calm senior who has filled these forms before", not "a
government portal" and not "a toy app".

## Colour palette
All values live in `frontend/src/styles/_palette.scss`, emitted as CSS variables with the same names as the design's
Tailwind `@theme` (`--color-paper`, `--color-lavender-500`, …). Every other style reads those variables.

| Name | Light | Dark |
|------|-------|------|
| paper / ink | `#fbf9f6` / `#211f2e` | `#18151f` / `#f8f5ef` |
| muted / line | `#6b6879` / `#ebe6df` | `#b7b1c2` / `#393442` |
| lavender 50·100·300·500·700 | `#f4f1ff` `#ebe5ff` `#c3b5fb` `#7c68ee` `#5440c4` | `#28233a` `#352e50` `#796ab3` `#a391ef` `#c2b5ff` |
| peach 50·100·300·500·700 | `#fff4ee` `#ffe6da` `#fbbfa3` `#ec7f58` `#b9502c` | `#352720` `#4a3428` `#df9b79` `#ec9b78` `#ffc2a4` |
| mint 50·100·300·500·700 | `#eefaf4` `#d9f3e6` `#96dcbb` `#2fa676` `#1d7a54` | `#1c3229` `#284838` `#74bf9d` `#57bd91` `#9be1c1` |
| sky 50·100·300·500·700 | `#eef6ff` `#dcecff` `#a6cbf6` `#3f86d8` `#285fa3` | `#1d2a3a` `#27384d` `#7ca8d3` (500 unchanged) `#aecdf1` |
| butter 50·100·300·500·700 | `#fffaea` `#fff2c7` `#f6d77a` `#d9a514` `#94700a` | `#3a3321` `#4c4227` `#dbc27d` (500 unchanged) `#efd992` |

**Roles** (they hold in both modes because the dark palette is inverted): paper = page, ink = text, muted = secondary
text, line = hairlines; X-50/100 = tinted surfaces; X-300 = decoration; X-500 = accents, icons, focus; X-700 = text on
paper or on its own tint, and solid buttons (text in `--fs-on-primary`: white in light mode, paper in dark mode).

- **Brand** is lavender: links and active states `lavender-700`, primary buttons a `lavender-500/700 → 700` gradient.
- **Status**: success mint-700 on mint-50, warning butter-ink on butter-50, danger peach-ink on peach-50, info sky-700 on sky-50 — always with icon + label.
- **Banners** (dashboard welcome, auth panel, home CTA): `lavender-100 → peach-100` wash with ink text.
- **Gradient text** (headline highlight, wordmark): `lavender-700 → peach-700`, text-safe at every stop in both modes.
- **Derived colours** (computed at build time, no runtime `color-mix()`): `--ink-peach` (peach-700 85% + ink) and
  `--ink-butter` (butter-700 75% + ink), because the plain 700s fall just under 4.5:1 on their own tints; category
  blends `lilac` = lavender × peach and `sand` = peach × butter so all categories stay distinct; dark card surfaces
  (paper + 6% / 10% ink); `--fs-muted-strong` for secondary text on banners; `--fs-border-input` (3:1 field edges).
- **Application status dots** (always next to their label): interested lavender-700, saved sky-500, preparing
  butter-700, ready mint-500, applied lavender-500, under review butter-500, approved mint-700, rejected peach-500.
  Chosen by testing every assignment with the dataviz palette validator: adjacent pairs ΔE ≥ 10.5 under simulated
  colour-blindness and ≥ 17 for normal vision, in light and dark mode. Bars in "Application progress" use one colour
  (lavender-500); the dots carry status.

**Contrast:** every text/background pair above was computed (WCAG 2.x), not judged by eye — all ≥ 4.5:1 in both modes
(e.g. muted on paper 5.2, lavender-700 on paper 6.9, button text 5.3–7.2, peach ink on its tint 5.0, butter ink on its
tint 5.7; dark mode 5.6–16.6).

**Status badges** — always text + icon, never colour alone:
- `Verified` ✓ mint · `Demo` flask lilac · `Pending verification` clock butter · `Expired` muted · `AI guidance` sparkles lavender.

## Illustrations
Custom inline SVG (no stock images, no licensing issues), coloured through `--ill-*` CSS variables so they adapt to dark mode:
`components/art/HeroScene.vue` (student with laptop + floating scholarship / eligibility / deadline / checklist cards) and
`components/art/SpotArt.vue` (profile, discover, checklist, track, student, jobseeker, family, celebrate). Gentle float and
twinkle animations respect `prefers-reduced-motion`.

## Typography
- **Plus Jakarta Sans** (variable, 200–800) for UI, body and section headings; **Instrument Serif** (regular + italic)
  for display: hero, section and page titles, stat numbers; **JetBrains Mono** (variable) for small uppercase labels
  and code. All self-hosted through Fontsource — no requests to Google Fonts.
- Instrument Serif has one weight, so display styles never use bold. `.lead` is set to 400 (the variable font's real
  300 reads too thin in muted grey).
- Scale (rem): 3.5 / 2.75 / 2 / 1.5 / 1.25 / 1.0625 (body) / 0.9375 / 0.8125. Fluid `clamp()` for hero.
- Line-height 1.6 body, 1.15 display. Hindi/Marathi fallback: **Noto Sans Devanagari**, with +0.05 line-height.

## Shape, depth, motion
- Radius: 13 (inputs), 14 (buttons; pills for hero CTAs), 20 (cards), 28 (banners), 999 (chips).
- Shadows (ink- and lavender-tinted, soft): `sm 0 1px 2px rgba(33,31,46,.05)`, `md 0 14px 34px -18px rgba(84,64,196,.28)`, `lg 0 30px 70px -28px rgba(33,31,46,.34)`.
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
A rounded-square **lavender-500 → peach-500 gradient** mark containing a **white document with a lavender-700 check and a butter spark** — the document = forms, the spark = "the opportunity you found", the rounded shape = friendliness. The mark uses fixed palette hexes so it looks the same in light and dark mode. Wordmark "Form**Saathi**" in Plus Jakarta Sans 700 with "Saathi" in the lavender → peach gradient. Delivered as SVG + favicon.

## Components (built in Phase 2)
Button (primary/secondary/ghost/danger, sizes, loading), IconButton, Badge/StatusBadge, Chip, Card, OpportunityCard, StatCard, ProgressRing, Stepper, Input/Select/Textarea with help + error text, SearchBar, FilterPanel / BottomSheet, Modal, Tabs, Accordion (FAQ), Toast, Tooltip, Skeleton, EmptyState (with illustration), ErrorState, Avatar, Timeline, KanbanColumn, Sidebar, TopBar, MobileTabBar, LanguageSwitcher, ThemeToggle.

## Accessibility
WCAG 2.2 AA: contrast checked on every token pair, visible focus ring (3px `lavender-500` outline, 3.9:1 on paper), semantic landmarks, labelled form controls, `aria-live` for toasts and chat, full keyboard navigation for board/tabs/modals, `lang` attribute switched with language.
