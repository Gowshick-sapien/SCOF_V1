# ADR 008: Desktop Client Architecture — Tauri v2 + React 19 + Apple HIG vs. Electron and Pure Web App

* **Status**: Accepted
* **Date**: 2026-08-16
* **Deciders**: SCOF Core Architecture Team, Frontend Leads
* **Consulted**: UI/UX Designers, System Operators
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

Supply chain operations managers require a dedicated "control room" interface to monitor global supply lines, observe multi-agent debates in real time, inspect decision reasoning traces, run what-if simulations, and review disruption alerts.

The presentation layer needed to fulfill strict requirements:
1. It must feel like an ultra-responsive, professional enterprise desktop application rather than a generic website.
2. It must support native OS window controls, system keyboard shortcuts (`Ctrl+1` through `7`), and offline resilience.
3. It must minimize local workstation resource consumption (RAM and CPU) so operators can keep it running continuously alongside enterprise ERP systems.

---

## 2. Decision Drivers

* **Resource Footprint**: Avoid the heavy 500MB+ RAM consumption typical of multi-process Chromium wrappers.
* **Native Desktop Capabilities**: Dedicated OS windowing, window management (zoom, minimize, close), native menus, and global hotkeys.
* **Modern UI Framework**: React 19 with strong TypeScript typing and rapid component lifecycle updates.
* **Design Aesthetic**: Compliance with user-specified Apple Human Interface Guidelines (HIG) dark mode styling.

---

## 3. Considered Options

* **Option 1: Pure Browser-Based Web Application**: Standard Next.js or React SPA accessed via web browser.
* **Option 2: Electron**: Cross-platform desktop runtime bundling Node.js and Chromium.
* **Option 3: Tauri v2 + React 19 + Vite**: Lightweight desktop runtime using native OS webview (WebView2 on Windows) with a compiled Rust backend.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Tauri v2 + React 19 + Apple HIG**

### Rationale:
1. **Lightweight Native Performance**:
   * Electron bundles a full Chromium browser and Node.js runtime with every application, consuming $> 500\text{ MB}$ of RAM and creating a 150MB+ installer.
   * Tauri v2 leverages the operating system's native webview (Microsoft Edge WebView2 on Windows, WebKit on macOS), reducing idle RAM consumption to **$< 50\text{ MB}$** and executable size to $< 15\text{ MB}$.
2. **Security & Sandboxing**:
   * Tauri's Rust core enforces fine-grained capability security models (`capabilities/default.json`), strictly bounding IPC communication and network permissions.
3. **Apple HIG Dark Vibrancy Design System**:
   * Styled in [desktop/src/index.css](file:///d:/projects/SCOF_V1/SCOF/desktop/src/index.css) using official Apple system colors, multi-layer frosted acrylic glassmorphism (`backdrop-filter: blur(28px)`), and SF Pro optical typography.
4. **Dual Execution Mode**:
   * While `npm run tauri dev` launches the native desktop window, the underlying Vite architecture allows immediate browser preview via `npm run dev` (`http://localhost:1420`), offering flexibility for remote operators.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Extremely fast cold start ($< 1\text{s}$) and negligible memory consumption.
* Native window controls and keyboard shortcuts (`Ctrl+1` to `7`) for rapid view switching.
* Clean separation between native Rust IPC and React 19 presentation layer.

### Negative Consequences / Trade-offs:
* Compiling native desktop builds requires the Rust toolchain (`cargo`) installed on developer machines.

---

## 6. Implementation & Compliance Notes

* Tauri configuration in [desktop/src-tauri/tauri.conf.json](file:///d:/projects/SCOF_V1/SCOF/desktop/src-tauri/tauri.conf.json).
* React application entry point in [desktop/src/App.tsx](file:///d:/projects/SCOF_V1/SCOF/desktop/src/App.tsx).
* 7 dedicated command views: Operations, Decisions, Scenarios, Agent Command, What-If Lab, Reasoning Trace, Evaluation.
* Verified via `cmd /c npm run build` (built in 909ms with 0 errors).

---

## 7. Related Decisions & Artifacts

* [ADR 010: Real-Time State Caching with Redis](./010_redis_realtime_state_caching.md)
* [D9 Desktop Operations Console Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D09_desktop_operations_console/README.md)
