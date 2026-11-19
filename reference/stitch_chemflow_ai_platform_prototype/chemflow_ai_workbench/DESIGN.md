---
name: ChemFlow AI Workbench
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e17'
  surface-container-low: '#171c25'
  surface-container: '#1b2029'
  surface-container-high: '#262a34'
  surface-container-highest: '#31353f'
  on-surface: '#dfe2f0'
  on-surface-variant: '#bac9cc'
  inverse-surface: '#dfe2f0'
  inverse-on-surface: '#2c303b'
  outline: '#849396'
  outline-variant: '#3b494c'
  surface-tint: '#00daf3'
  primary: '#c3f5ff'
  on-primary: '#00363d'
  primary-container: '#00e5ff'
  on-primary-container: '#00626e'
  inverse-primary: '#006875'
  secondary: '#7dffa2'
  on-secondary: '#003918'
  secondary-container: '#05e777'
  on-secondary-container: '#00622e'
  tertiary: '#f1e9ff'
  on-tertiary: '#370096'
  tertiary-container: '#d6c9ff'
  on-tertiary-container: '#622be5'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#9cf0ff'
  primary-fixed-dim: '#00daf3'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f58'
  secondary-fixed: '#62ff96'
  secondary-fixed-dim: '#00e475'
  on-secondary-fixed: '#00210b'
  on-secondary-fixed-variant: '#005226'
  tertiary-fixed: '#e8deff'
  tertiary-fixed-dim: '#cdbdff'
  on-tertiary-fixed: '#20005f'
  on-tertiary-fixed-variant: '#4f00d0'
  background: '#0f131d'
  on-background: '#dfe2f0'
  surface-variant: '#31353f'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Geist
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.06em
  data-metric:
    fontFamily: JetBrains Mono
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  gutter-desktop: 1rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style

This design system establishes a high-precision, mission-critical digital twin and autonomous simulation environment tailored for senior chemical process engineers, plant operators, and industrial ML researchers. The emotional tone is authoritative, composed, and analytically sharp—eliminating decorative ambiguity in favor of computational transparency and deep optical focus.

The visual direction merges **Technical Precision** with **Restrained Glassmorphism**:
- **Atmospheric Depth:** Deep-space obsidian and calibrated navy foundations mitigate long-shift eye strain across control rooms and command centers.
- **Instrument Luminescence:** High-vibrancy cyan and electric green accents act as active laser telemetry lines and verified state indicators rather than simple decorative fills.
- **Physical Telemetry Clarity:** Crisp 1-pixel border lines, directional micro-radiance, and structural monospaced readouts evoke the tactile density of physical industrial racks integrated with next-generation algorithmic compute engines.

## Colors

The palette is engineered for visual hierarchy under sustained high-concentration workflows:

- **Primary (`#00E5FF` - Cyan Telemetry):** Represents continuous AI activity, dynamic stream flows, selected topological nodes, and forward state progression.
- **Secondary (`#00E676` - Electric Steady-State):** Dedicated strictly to verified telemetry, thermodynamic convergence, operational safety compliance, and live plant synchronization.
- **Tertiary (`#7C4DFF` - Synthetic Neural Engine):** Highlights predictive model uncertainty bounds, Pareto front optimizations, and generative chemical synthesis routes.
- **Neutral Foundation (`#070B14` - Slate Obsidian):** Deep non-pure black with slate undertones that grounds the canvas. Intermediate tiers include:
  - Surface Foundation: `#070B14`
  - Panel Elevation 1: `#0B132B` at 70% opacity
  - Panel Elevation 2 (Active/Hover): `#111E3D` at 85% opacity
  - Surface Border Muted: `rgba(0, 229, 255, 0.12)`
  - Surface Border Highlight: `rgba(0, 229, 255, 0.40)`
- **Functional Semantics:**
  - Dynamic Alert / Exothermic Runaway: `#FF3D71`
  - Cautionary Drift / Latent Mass Balance Deviation: `#FFB300`

## Typography

The type scale orchestrates crisp geometric headings with systematic, dense data interpretation:

- **Headlines (Space Grotesk):** Provides structural character for workspace titles, process module headers, and equipment tags without sacrificing executive clarity.
- **Body (Geist):** Handles contextual engineering briefs, agent logs, parameter descriptions, and conversational reasoning tracks with uniform rendering.
- **Labels & Numeric Data (JetBrains Mono):** Governs engineering units ($kg/h$, $kPa$, $kJ/mol$), stoichiometry fractions, coordinate readouts, matrix coordinates, and discrete pipeline state indicators. Tabular figures (`tnum`) must remain strictly enforced across all data grids.

## Layout & Spacing

The layout is built upon an ultra-dense, multi-pane docking architecture that maximizes usable interactive telemetry area:

- **Docked Multi-Pane Grid:** Standard viewports deploy a 12-column variable flex-dock framework. Default view: 64px collapsed icon rail, 280px left configuration drawer, flexible central process canvas/Pareto visualizer, and 360px right live-telemetry inspector.
- **Rhythm & Compaction:** Spacing tokens employ a condensed 4px modular base. Dense information displays utilize `space-xs` and `space-sm` for element pairings (unit markers adjacent to numerical values), reserving `space-lg` and `space-xl` solely for major workstation module delimiters.
- **Viewport Adaptation:**
  - **Desktop/Multi-Monitor (>1440px):** Simultaneous tri-panel orchestration (Process Flow Canvas, High-Density Table, Pareto Optimization).
  - **Standard Laptop (1024px - 1439px):** Dynamic panel collapse into tabbed side-sheets; data grids enter virtual scrolling modes.
  - **Tablet/Mobile (<1023px):** Single-column stacked monitoring mode; secondary inspectors convert to bottom-pinned sliding sheets with sticky status tickers.

## Elevation & Depth

Visual hierarchy is maintained via translucent optical tiers and luminous perimeter definitions rather than heavy drop shadows:

- **Base Canvas:** Solid `#070B14` textured with an ultra-faint 24px isometric mechanical grid pattern rendered at 3% opacity.
- **Level 1 (Docked Containers & Sidebars):** Background `rgba(11, 19, 43, 0.65)`, backdrop filter blur `16px`, bordered with `1px solid rgba(0, 229, 255, 0.08)`.
- **Level 2 (Active Cards & Overlay Inspectors):** Background `rgba(17, 30, 61, 0.75)`, backdrop filter blur `24px`, bordered with `1px solid rgba(0, 229, 255, 0.22)`, elevated with an inner glow `inset 0 1px 0 0 rgba(255, 255, 255, 0.06)`.
- **Level 3 (Modal Alerts & Critical Focus States):** Background `rgba(9, 16, 35, 0.94)`, backdrop blur `32px`, bordered with `1px solid rgba(0, 229, 255, 0.50)`, reinforced with a radial atmospheric ambient halo: `0 8px 32px -4px rgba(0, 229, 255, 0.15)`.
- **Pipeline Edge Glow:** Active streaming pipelines on process flow canvases leverage dynamic CSS/SVG drop-shadow filters: `drop-shadow(0 0 6px rgba(0, 229, 255, 0.55))`.

## Shapes

The interface employs a disciplined, industrial-grade semi-angular geometry:

- **Base Radius (0.25rem / 4px):** Applied to telemetry chips, data cells, input fields, and pipeline steps to reflect robust, rack-mounted instrumentation.
- **Component Enclosures (`rounded-lg` / 0.5rem / 8px):** Applied to floating workbench cards, graph containment hulls, and dialog windows.
- **Structural Integrity:** Radii above 0.75rem are strictly prohibited except for micro circular status pings to retain a technical, high-integrity laboratory finish.

## Components

### Buttons & Operational Switches
- **Primary Cyber-Action:** Filled cyan `#00E5FF` with `#070B14` bold typography. Micro-radiance hover state with `box-shadow: 0 0 12px rgba(0, 229, 255, 0.45)`.
- **Secondary Instrumentation Action:** Background `rgba(0, 229, 255, 0.06)`, border `1px solid rgba(0, 229, 255, 0.28)`, text color `#00E5FF`. Hover expands to background `rgba(0, 229, 255, 0.14)`.
- **Emergency Halt / Override:** Background `rgba(255, 61, 113, 0.12)`, border `1px solid rgba(255, 61, 113, 0.4)`, text `#FF3D71`.

### Status Badges & Agent Tickers
- **Agent Active:** Pinned pill container (`rgba(0, 229, 255, 0.1)`) with a 6px pulsating `#00E5FF` LED dot, displaying `label-sm` monospaced type: `AGENT_ACTIVE // 84 TFLOPS`.
- **Data Verified:** Forest-slate container with `#00E676` static indicator and micro-check icon: `STATE_CONVERGED`.
- **Simulation Pending:** Subdued amber container with an intermittent scanning sweep animation: `QUEUE_JOB #8029`.

### 9-Step Industrial Engineering Stepper
- Compact horizontal pipeline track featuring 9 modular milestones (e.g., Feed Prep, Flash Evap, Kinetic Rx, Heat Exch, Distill 1, Distill 2, Recycle Loop, Carbon Capture, Final Product).
- Nodes render as 20px chamfered or softly radiused numeric badges connected by 1px fiber paths. Completed steps trigger `#00E676` line illumination; the running stage pulses `#00E5FF`; unreached nodes show faint muted borders (`rgba(255, 255, 255, 0.15)`).

### Interactive High-Density Engineering Data Tables
- Condensed 28px row height with alternating row translucency (`rgba(255, 255, 255, 0.01)` and `rgba(255, 255, 255, 0.03)`).
- Sticky header cells with integrated column-sort glyphs, units defined in `label-sm` muted text, and live inline sparkline columns.
- Cell selection invokes a persistent cyan perimeter outline (`1px solid #00E5FF`) with instantaneous telemetry readouts in the inspector rail.

### Pareto Multi-Objective Optimization Cards
- Dedicated visualization card framing 2D/3D scatter topologies with trade-off curves (e.g., Capital Cost vs. Energy Purity).
- Optimal frontier coordinates are highlighted in `#00E5FF` and `#00E676` points with interactive hover crosshairs rendering exact coordinate tags (`JetBrains Mono`, 11px) alongside AI-selected confidence intervals.

### Process Flow Canvas Controls
- Docked floating toolbar with mini HUD zoom/pan controls, stream injection buttons, thermodynamic balance validation toggles, and coordinate tracking HUD.