# Indian Sign Language (ISL) to Multilingual Translation System
## Diagrams & Editable Files Reference

All diagrams have been generated in both **Academic/IEEE Paper Style** and fully editable **Draw.io (.drawio) / Figma** format.

### 📁 Directory Location
`c:\Dev\Final_training\ISL_to_Text_Translation\diagrams\`

---

### 🎨 How to Open & Edit in Draw.io or Figma

#### Method 1: Using Draw.io (diagrams.net)
1. Open [app.diagrams.net](https://app.diagrams.net) in your browser (or VS Code with the Draw.io extension).
2. Click **File > Open From > Device**.
3. Select `all_isl_diagrams.drawio` to open **all 8 diagrams in a single file with tabs**, or select any individual `.drawio` file.
4. You can edit any text, box, arrow, style, or layout.
5. Export as **PNG**, **PDF**, or **SVG** directly.

#### Method 2: Importing into Figma
1. **Via SVG Export (Direct & Best Quality)**:
   - Open the diagram in [app.diagrams.net](https://app.diagrams.net).
   - Go to **File > Export as > SVG**.
   - Drag and drop the downloaded `.svg` file directly onto your Figma canvas.
   - All elements will import as clean, editable vector shapes, text layers, and lines.
2. **Via Draw.io Figma Plugin**:
   - In Figma, open Plugins and search for **"Draw.io"** or **"Draw.io to Figma"**.
   - Import the `.drawio` file directly into your Figma workspace.

---

### 📊 Diagram Catalog

| Figure | Diagram Name | File Name | Description |
| :--- | :--- | :--- | :--- |
| **-** | **Master (All Tabs)** | `all_isl_diagrams.drawio` | Single multi-page file with all 8 diagrams |
| **4.1** | **Architectural Diagram** | `architecture_diagram.drawio` | MediaPipe + V3 Dual Models + NLP + Google Translate API + Web Frontend |
| **4.2** | **Proposed System Flowchart** | `proposed_system_flowchart.drawio` | Real-time decision flow, buffer checks, thresholding, translation & exit |
| **4.3** | **Modular Design Diagram** | `modular_design_diagram.drawio` | 5 core modules and hierarchical sub-components |
| **4.4** | **Sequence Diagram** | `sequence_diagram.drawio` | UML sequence from gesture performance to localized translation |
| **4.5** | **Use Case Diagram** | `use_case_diagram.drawio` | UML Use Cases for Signer, Recipient, Admin, and Google Translate API |
| **4.6** | **DFD Level 0 (Context)** | `dfd_level_0.drawio` | High-level system boundary and external entities |
| **4.7** | **DFD Level 1** | `dfd_level_1.drawio` | System sub-processes (1.0 to 6.0) and data stores (D1 to D4) |
| **4.8** | **DFD Level 2** | `dfd_level_2.drawio` | In-depth decomposition of Classification (3.0) and NLP & Translation (4.0 & 5.0) |

---

### 🧠 Core Architectural Inclusions
1. **Dual-Branch V3 Inference Core**:
   - **Static Model**: Residual Dense MLP for 35 classes (A-Z, 0-9, Good).
   - **Dynamic Model**: Conv1D + BiLSTM + Bahdanau Attention for 11 temporal classes.
   - **Runtime Toggle**: Instant mode routing (`TAB`/`M` toggle) with `@tf.function` graph compilation (~2ms latency).
2. **NLP Sentence Structuring Engine**:
   - Character compounding for fingerspelled sequences.
   - ISL Subject-Object-Verb (SOV) to natural English Subject-Verb-Object (SVO) grammar restructuring.
   - Sentence capitalization, punctuation, and article/auxiliary verb synthesis.
3. **Google Cloud Translation API**:
   - Secure HTTPS client with API Key authentication.
   - Target regional language routing (Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, etc.).
   - Response parsing and Text-to-Speech (TTS) audio dispatch.
