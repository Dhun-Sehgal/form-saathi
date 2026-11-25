# FormSaathi — Design Direction

## Personality
**Calm, warm, trustworthy — "Warm Neutral".** Cream pages, beige and taupe surfaces, warm brown accents and deep
charcoal text and buttons, with soft illustrations. Think "a calm senior who has filled these forms before", not "a
government portal" and not "a toy app".

## Colour palette
All values live in `frontend/src/styles/_palette.scss`. Components only use role variables (`--fs-bg`, `--fs-primary`,
`--tint-mint`, `--status-applied` …), so changing the palette never touches component styles.

**Brand colours** (the base of every page):

| Name | Hex | Used for |
|------|-----|----------|
| Warm Cream | `#F3F0EC` | Page background (light); text (dark mode) |
| Soft Beige | `#E1DAD1` | Hairlines, tints, banners; buttons in dark mode |
| Taupe | `#C9B8AA` | Decoration, dividers; secondary text in dark mode |
| Warm Brown | `#A89480` | Accents, card strips, illustrations — decoration only (2.6:1 on cream, too light for text) |
| Deep Charcoal | `#6B6258` | Buttons, secondary text, icons, focus ring (5.3:1 on cream) |

**Derived shades** (needed because the brand colours alone don't reach readable contrast for body text):
text `#2F2B27` (charcoal darkened, 12.4:1 on cream) · links and active nav `#735A41` (deep warm brown, 5.7:1) ·
secondary text on banners `#4F4941` · secondary surface `#EBE6E0` · card surface `#FDFCFA` · input edge `#8F8377` (3.6:1).

**Earth tones** — used only where colour carries meaning (status) or to tell categories apart; each has a tint
(background), an ink (text on that tint, ≥ 4.5:1) and an accent (dots, strips, illustration):

| Tone | Tint / ink / accent | Meaning |
|------|---------------------|---------|
| sage | `#E4EADD` / `#46603C` / `#7D9570` | success: eligible, verified, approved |
| ochre | `#F4E9D2` / `#725515` / `#C49A43` | warning: pending, possibly eligible, reminders |
| clay (terracotta) | `#F4E1D9` / `#96412D` / `#C2735B` | danger: not eligible, urgent deadlines |
| slate | `#E2E7EA` / `#405565` / `#7A8E9B` | info |
| mauve, sand | `#EEE2E2` / `#74505A`, `#EDE5DB` / `#6A5643` | category variety only |

Category colour slots keep their stored names (lavender → brand beige/brown, sky → slate, lilac → mauve, mint → sage,
peach → clay, butter → ochre, sand → sand).

**Dark mode** is a warm espresso version: page `#1D1A17`, cards `#26221F`, text Warm Cream, secondary text Taupe,
buttons Soft Beige with dark text, links `#E3CDB4`; earth tones switch to light inks on deep tints.

- **Buttons:** Deep Charcoal (`#7A6F62 → #6B6258`) with near-white text (≥ 4.8:1).
- **Banners** (dashboard welcome, auth panel, home CTA): Soft Beige → Taupe wash with dark text.
- **Gradient text** (headline highlight, wordmark): `#735A41 → #96412D`, text-safe at every stop in both modes.
- **Application status dots** (always next to their label): interested slate-ink, saved Warm Brown, preparing
  ochre-ink, ready slate, applied deep brown, under review mauve, approved sage-ink, rejected clay. Chosen by testing
  every assignment with the dataviz palette validator: neighbouring statuses ≥ 12 ΔE apart under simulated
  colour-blindness and ≥ 16 for normal vision, in light and dark mode. "Application progress" bars use one colour.

**Contrast:** every text/background pair above was computed (WCAG 2.x), not judged by eye — all ≥ 4.5:1 in both
modes; UI edges (focus ring, input borders, progress fills) ≥ 3:1.

**Status badges** — always text + icon, never colour alone:
- `Verified` ✓ sage · `Demo` flask mauve · `Pending verification` clock ochre · `Expired` muted · `AI guidance` sparkles brown.

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
- Shadows (warm, soft): `sm 0 1px 2px rgba(47,43,39,.05)`, `md 0 14px 34px -18px rgba(107,98,88,.38)`, `lg 0 30px 70px -28px rgba(47,43,39,.34)`.
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
A rounded-square **Deep Charcoal → Warm Brown gradient** mark containing a **white document with a charcoal check and a cream spark** — the document = forms, the spark = "the opportunity you found", the rounded shape = friendliness. The mark uses fixed palette hexes so it looks the same in light and dark mode. Wordmark "Form**Saathi**" in Plus Jakarta Sans 700 with "Saathi" in the warm brown → terracotta gradient. Delivered as SVG + favicon.

## Components (built in Phase 2)
Button (primary/secondary/ghost/danger, sizes, loading), IconButton, Badge/StatusBadge, Chip, Card, OpportunityCard, StatCard, ProgressRing, Stepper, Input/Select/Textarea with help + error text, SearchBar, FilterPanel / BottomSheet, Modal, Tabs, Accordion (FAQ), Toast, Tooltip, Skeleton, EmptyState (with illustration), ErrorState, Avatar, Timeline, KanbanColumn, Sidebar, TopBar, MobileTabBar, LanguageSwitcher, ThemeToggle.

## Accessibility
WCAG 2.2 AA: contrast checked on every token pair, visible focus ring (3px Deep Charcoal outline, 5.3:1 on cream; Taupe in dark mode), semantic landmarks, labelled form controls, `aria-live` for toasts and chat, full keyboard navigation for board/tabs/modals, `lang` attribute switched with language.
