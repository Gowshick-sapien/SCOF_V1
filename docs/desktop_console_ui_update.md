3. Brand and visual personality
3.1 Brand essence
Complexity, connected. Decisions, coordinated.

SCOF should feel composed, credible, analytical, and dependable. It should not try to look "intelligent" through visual effects. Its intelligence should be communicated by the quality of the information hierarchy, evidence presentation, comparison tools, and operational feedback.

3.2 Brand palette
Use these as the canonical brand colours:

Token Hex Role

brand.navy #0B2545 Primary identity, selected navigation emphasis, headings in brand moments

brand.blue #0E82D6 Interactive accent, focus, links, selection, primary actions

brand.teal #16A67E Positive resolution, resilience, successful outcomes where semantically appropriate

brand.slate #CBD5E1 Neutral supporting detail, dividers, inactive visual structure
Brand colours are accents, not page backgrounds. The majority of the interface should use neutral surfaces. Never colour every card, panel, or chart with the brand palette.

3.3 Recommended semantic palette
The following are design-system starting points. Validate contrast in implementation and adjust only through shared tokens.

Token Light theme Dark theme Usage

surface.canvas #F5F7FA #11161D App workspace background

surface.sidebar #F0F3F7 #171D26 Sidebar / navigation region

surface.panel #FFFFFF #1B232E Cards, inspectors, sheets

surface.raised #FFFFFF #222C39 Popovers, menus, raised surfaces

surface.subtle #EEF2F6 #252F3C Quiet grouping and table headers

text.primary #172334 #F2F5F8 Main content

text.secondary #586779 #AAB6C4 Supporting text

text.muted #748295 #8492A3 Timestamps, tertiary metadata

border.default #DCE3EA #303B49 Panel boundaries and separators

border.strong #C3CED9 #455264 Emphasized boundaries

interactive.primary #0E82D6 #45A9F3 Links, primary button, focus

interactive.hover #E7F3FC #1B354A Hover surface

status.success #16835F #48C69A Completed / healthy / verified

status.warning #A9680A #E9B45C Caution / needs attention

status.critical #C43D4B #F0747E Critical risk / failed / blocked

status.info #0E82D6 #45A9F3 Informational / in progress
Do not use status colour alone to convey meaning. Pair it with a text label and, where useful, an icon. Red and green should be reserved for semantic states, not decorative branding.

3.4 Colour rules
Navy anchors the brand and high-level identity; it should not dominate every screen.
Blue is the primary interactive colour.
Teal-green indicates positive or resilient outcomes only when the underlying state supports that meaning.
Slate is structural and neutral.
Orange/amber signals caution or a threshold requiring attention.
Red signals criticality, failure, or a blocked state.
Avoid rainbow heatmaps. Prefer a neutral sequential scale for magnitude and a clear diverging scale only when comparing positive/negative deltas.
Charts must remain readable in monochrome and colour-vision-deficiency conditions.
4. macOS-inspired design language
The application should borrow the best parts of macOS Human Interface Guidelines: clarity, hierarchy, restrained materials, predictable controls, keyboard support, clear window structure, and content-first design. It must still feel like SCOF, not a web page pretending to be Finder.

4.1 Overall frame
Use a stable desktop shell:

Native title bar / window chrome: respect platform conventions and Tauri window behavior.
App sidebar: primary destinations, compact and scannable.
Main workspace: page title, contextual actions, filters, and page content.
Optional inspector panel: selected entity, decision, event, or evidence detail.
Status area: backend connection, active profile/environment, and background activity.
The shell should support resizable windows and remain useful at narrower widths. Avoid permanently forcing a three-column layout when a two-column or full-width view is more appropriate.

4.2 Visual materials
Prefer opaque or lightly tinted surfaces over heavy glassmorphism.
Use translucency only for native-feeling overlays where it improves hierarchy.
Avoid large gradients, neon glows, strong drop shadows, and decorative blur.
Use thin borders and subtle elevation to distinguish surfaces.
Keep corners consistent. Suggested radius scale: 6 px (small controls), 9 px (standard cards), 12 px (larger sheets/panels). Avoid pill-shaped everything.
Use shadow sparingly for popovers, menus, and floating inspectors---not every card.
4.3 Typography
Use the system font stack where possible for a native desktop feel. In CSS, a suitable starting point is:

-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif

Use a consistent type scale:

Style Size Weight Use

Page title 24--28 px 600 One per page

Section title 16--18 px 600 Content sections

Panel title 14--16 px 600 Cards and inspectors

Body 13--14 px 400 Main interface copy

Secondary 12--13 px 400 Supporting context

Caption / 11--12 px 400--500 Timestamps, metadata IDs, source labels

Numeric KPI 26--34 px 600 Only when a number is genuinely important
Do not use all-caps as a general heading style. Use tabular numerals for aligned numeric data. Reserve bold weight for hierarchy, not emphasis everywhere.

4.4 Spacing and layout
Use an 8 px base spacing system, with 4 px increments for compact details.

4 px: icon/text micro-spacing
8 px: tight control grouping
12 px: compact component padding
16 px: standard component padding
24 px: section spacing
32 px: major page grouping
40--48 px: spacious empty states or top-level separation
Avoid excessive empty space that hides useful operational context, but do not compress every page into a dense wall of information. Density should follow task urgency and information complexity.

4.5 Icons
Use one consistent outline icon family. Icons should be simple, familiar, and paired with text labels for primary navigation. Do not use emoji as interface icons. Do not create bespoke icons for every data type unless a domain-specific distinction genuinely helps.

4.6 Motion
Use short transitions for navigation, disclosure, and state changes.
Prefer approximately 120--200 ms for common transitions.
Avoid animated backgrounds, pulsing decorative nodes, spinning "thinking" symbols, or continuous motion.
Real operational changes may animate subtly when doing so helps the operator locate a changed value.
Respect reduced-motion preferences.
5. Information architecture
The V2 architecture's canonical console direction is seven primary views. Use these as the initial top-level navigation; supporting pages should be nested within the relevant workspace rather than all being placed in the sidebar.

5.1 Primary navigation
Operations Overview --- current operational situation, active alerts, system health, key outcome metrics.
Decision Center --- decision queue, candidate actions, evidence, trade-offs, approval/authorization state.
Scenario Launcher --- create, configure, validate, and start a disruption scenario.
Agent Command --- specialist activity, execution status, claims, failures, and service health.
What-If Simulation Lab --- isolated scenario exploration, adjustable assumptions, candidate interventions, counterfactual results.
Reasoning Traces --- event sequence, evidence lineage, deliberation record, replay and audit details.
Evaluation Matrix --- benchmark comparisons, quality metrics, latency, calibration, and outcome measures.
Suggested keyboard shortcuts: Ctrl/Cmd+1 through Ctrl/Cmd+7 for the seven primary views, with shortcuts discoverable in menus and help. Ensure they do not override essential platform shortcuts.

5.2 Supporting destinations
Supply Chain Map: accessible from Operations Overview and relevant entity/impact details.
Scenario Comparison: within the Simulation Lab.
Risk Heatmap: within Operations Overview or the map/impact workspace.
Recommendation Timeline: within Decision Center and decision details.
Meeting / Deliberation Log: within Reasoning Traces and individual decision detail.
Settings: a persistent utility destination, not an operational primary view.
Connection and environment details: status-area popover and Settings.
Natural-language operational query: optional contextual utility. Do not make a chat panel the visual centerpiece or call it "AI Chat" in prominent navigation; a restrained label such as Ask SCOF or Query is preferable if the capability is implemented.
Do not show features as active navigation items until the backend contract and functionality exist. Use disabled/coming-soon states only when they serve a real roadmap need and are clearly labelled.

6. Global shell specification
6.1 Sidebar
Include: - SCOF emblem and wordmark in a restrained header. - Seven primary navigation items. - Optional small badge for a real count of unresolved critical items. - Settings at the bottom. - A compact environment/profile label where it cannot be mistaken for page content.

Sidebar behavior: - Selected destination gets a subtle blue-tinted background and clear label weight. - Do not use a full saturated blue block behind every selected item. - Support collapse/expand if required, but retain accessible labels/tooltips. - Do not encode severity solely through a tiny coloured dot.

6.2 Page header
Each primary page should have: - Page title. - One-line contextual description where needed. - Breadcrumbs only when they add real navigation value. - Contextual primary action at the right. - Secondary actions in a menu when they are infrequent. - Filters and time range below the title when relevant.

There should be one obvious primary action per page. Multiple competing primary buttons create ambiguity.

6.3 Global status area
Show: - Backend connection: Connected / Reconnecting / Offline. - Active domain profile or environment. - Active scenario/run only when applicable. - A link to details, logs, or diagnostics.

Connection state must be based on actual health checks, not merely whether a WebSocket object exists. Distinguish API availability from event-stream availability if the architecture exposes them separately.

6.4 Inspector panels
Use a right-side inspector for contextual details when the operator should preserve their current list/map/table context. Examples: a selected facility, affected SKU, candidate action, evidence item, or trace event.

Inspectors should: - Have a clear title and close behavior. - Keep a stable width where practical. - Scroll independently if long. - Preserve the selection when the operator returns from a detail view, when feasible. - Offer "Open full details" for complex objects rather than cramming everything into the panel.

7. Page design specifications
7.1 Operations Overview
Primary question: What needs attention right now?

Recommended hierarchy: 1. Page header and time window. 2. Critical active disruptions / alerts, sorted by impact and urgency. 3. A compact row of operational indicators, such as fill rate, at-risk demand, affected facilities, and open decisions---only when these metrics are backed by reliable data. 4. Supply-chain impact map or network view. 5. Recent significant events and decision outcomes. 6. System health in a secondary area, not competing with operational risk.

Design guidance: - Keep KPI count small; 4--6 is a useful starting point. - Every KPI should have a clear definition, time window, and comparison basis. - Do not use arbitrary gauges or decorative charts. - Map markers should reveal a meaningful entity or event on selection. - Risk heatmaps must state what the colour represents and the time horizon. - Empty state should say the system is healthy only when the backend confirms that state. Otherwise say no events are currently available or data could not be loaded.

7.2 Decision Center
Primary question: Which decisions need review, and what is the evidence?

Recommended layout: - A queue/list of decisions with status, priority, affected scope, age, and latest update. - Main detail area for the selected decision. - Optional right inspector for evidence or affected entities.

Decision detail sections: 1. Summary of the operational issue. 2. Proposed action and intended outcome. 3. Evidence and source authority. 4. Expected impact and trade-offs. 5. Alternatives considered. 6. Specialist claims, agreement, and disagreement. 7. Counterfactual result if simulation is required or available. 8. Policy constraints and unresolved assumptions. 9. Lifecycle status and allowed next action. 10. Audit / trace links.

Use explicit lifecycle labels such as Proposed, Under review, Approved, Authorized, Executing, Completed, Rejected, Blocked, and Failed where these states exist in the actual API. Do not collapse approval and execution authorization into one status. Do not show an Execute button unless the backend explicitly permits that operation and the current state passes the required checks.

7.3 Scenario Launcher
Primary question: What disruption or operating condition should be tested?

Recommended flow: 1. Choose a scenario type from supported types. 2. Select affected entity/entities using bounded search. 3. Configure severity, duration, start time, and supported parameters. 4. Review the impact scope and scenario assumptions. 5. Validate the configuration. 6. Start the scenario. 7. Navigate to the resulting run.

Design guidance: - Use a step-by-step form only when the task truly has ordered dependencies. - Keep advanced parameters collapsed by default. - Provide clear units and valid ranges for every numeric field. - Show a final summary before starting. - Make it explicit that a scenario creates an isolated runtime snapshot/overlay and does not mutate frozen ground truth or the baseline state. - If scenario creation fails, retain the form values and display a useful error. - Disable repeat submission while a request is pending and use idempotency protections if provided by the API.

7.4 Agent Command
Primary question: What work is the orchestration runtime performing, and where is it blocked?

Use a calm operations table/list, not a sci-fi "agent network."

Suggested columns: - Specialist / component - Current task - Status - Scenario/run - Started / elapsed time - Last event - Error or escalation indicator

Selecting an item should open a detail inspector containing: - Current stage and recent stage transitions. - Claims emitted and their schema/status. - Tool/service calls with bounded summaries. - Failure and fallback details. - Relevant correlation, scenario, and trace IDs. - Links to the decision and reasoning trace.

Do not display fictional agent avatars or animate nodes as if they were physically moving. Activity indicators should reflect real events. Distinguish idle, running, waiting, completed, degraded, and failed states where supported.

7.5 What-If Simulation Lab
Primary question: How do plausible actions compare under the same scenario assumptions?

Recommended structure: - Scenario and snapshot context at the top. - Baseline outcome panel. - Alternative action/configuration controls. - Run simulation action. - Comparison table or aligned result cards. - Impact breakdown by relevant dimensions. - Assumptions, constraints, and limitations. - Link to the full decision record.

Design rules: - Make baseline versus alternative unmistakable. - Keep the same baseline snapshot and evaluation window across comparisons unless the operator explicitly changes them. - Display deltas as absolute and relative changes when both are meaningful. - State whether a result is simulated, forecast, measured, or historical. - Never present simulated outcomes as real operational outcomes. - Sliders should show numeric values and units; support keyboard entry and reset. - Do not re-run expensive simulations on every slider movement. Use an explicit Run/Compare action or a carefully debounced preview only if supported. - Make scenario isolation visible through a scenario/run identifier and snapshot label.

7.6 Reasoning Traces
Primary question: How did the system arrive at this decision?

Recommended layout: - A chronological event timeline. - Stage filter and event-type filters. - A central event/detail pane. - Evidence/source panel or inspector. - Links back to the originating scenario and decision.

Display a clear progression through the actual runtime stages. Where the architecture uses OBSERVE → SCOPE → RETRIEVE → ANALYZE → CHECK → PROPOSE → VALIDATE → EMIT, show those stages as a trace of the implemented pipeline---not as decorative steps that imply success when the stage failed or was skipped.

Each event should show: - Timestamp and stage. - Component/source. - Event type and outcome. - Evidence references. - Relevant input/output summary. - Correlation, decision, scenario, and run IDs. - Error details and fallback status when relevant.

Provide a human-readable summary first, with structured payloads available on demand. Do not render raw JSON as the default interface. Preserve exact underlying values and source links for auditability. A replay view must clearly distinguish historical replay from a live run.

7.7 Evaluation Matrix
Primary question: Is SCOF producing better, reliable, and reproducible decisions?

Recommended sections: 1. Evaluation run metadata and dataset/profile version. 2. Overall benchmark summary. 3. Comparison of CD²F with configured baselines. 4. Decision quality and consensus metrics. 5. Latency distribution and fast/slow-path breakdown where applicable. 6. Operational outcomes such as fill rate, cost, or risk measures. 7. Calibration and reliability metrics. 8. Scenario-level drill-down. 9. Export/report action.

Design guidance: - Show sample size, scenario set, date/run, and version alongside headline metrics. - Use consistent metric definitions and units across comparisons. - Show distributions or confidence intervals where available; do not imply statistical certainty from a single aggregate. - Label missing metrics as unavailable rather than zero. - Use the same scale when comparing like-for-like metrics. - Distinguish research benchmark performance from live operational performance. - Allow drill-down to the underlying run and decision evidence.

7.8 Settings and system diagnostics
Settings should be secondary and organized into clear sections: - Appearance: system/light/dark theme. - Connection: API endpoint and connection diagnostics, with sensitive values handled appropriately. - Active profile/environment. - Notifications. - Keyboard shortcuts. - Logs and diagnostics. - About/version information.

Do not place secrets or credentials in plain text. Confirm changes that can interrupt a running session. Provide a useful diagnostics view for API, WebSocket/event stream, and service readiness when those checks are available.