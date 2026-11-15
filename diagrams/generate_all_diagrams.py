"""
Master Generator for all ISL Draw.io Diagrams.
Produces:
1. architecture_diagram.drawio
2. modular_design_diagram.drawio
3. proposed_system_flowchart.drawio
4. sequence_diagram.drawio
5. use_case_diagram.drawio
6. dfd_level_0.drawio
7. dfd_level_1.drawio
8. dfd_level_2.drawio
9. all_isl_diagrams.drawio (Multi-page draw.io file with all diagrams)
"""

import xml.etree.ElementTree as ET
import os
from builder_base import (
    DrawIOBuilder, BOX_STYLE, ROUNDED_STYLE, DASHED_BOX, CONTAINER_STYLE,
    TITLE_STYLE, CAPTION_STYLE, ARROW_STYLE, DASHED_ARROW, DIAMOND_STYLE,
    ELLIPSE_STYLE, ACTOR_STYLE, DATASTORE_STYLE, EXTERNAL_ENTITY
)

OUTPUT_DIR = r"c:\Dev\Final_training\ISL_to_Text_Translation\diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# 1. ARCHITECTURAL DIAGRAM (4.1.1)
# ==============================================================================
def build_architecture_diagram():
    b = DrawIOBuilder("Figure 4.1 Architecture", "page_arch", width=1280, height=960)
    
    # Title
    b.add_node("FIGURE 4.1: SYSTEM ARCHITECTURE OF ISL TO MULTILINGUAL TRANSLATION SYSTEM",
               150, 20, 950, 30, TITLE_STYLE)
    
    # Layer 1: Frontend & Presentation
    c1 = b.add_node("PRESENTATION & FRONTEND CLIENT (WEB APP / UI)", 50, 70, 1160, 100, CONTAINER_STYLE)
    b.add_node("WEBCAM INPUT<br>(1280x720 @ 30 FPS)", 80, 105, 180, 50, ROUNDED_STYLE)
    b.add_node("CLIENT UI<br>(Video Canvas & HUD)", 310, 105, 180, 50, ROUNDED_STYLE)
    b.add_node("MODE SELECTOR<br>(Static / Dynamic Toggle)", 540, 105, 190, 50, ROUNDED_STYLE)
    b.add_node("LANGUAGE SELECTOR<br>(Hindi, Tamil, Telugu, etc.)", 780, 105, 200, 50, ROUNDED_STYLE)
    b.add_node("OUTPUT BANNER &<br>TTS AUDIO PLAYER", 1020, 105, 160, 50, ROUNDED_STYLE)

    # Layer 2: Feature Extraction & Pre-processing
    c2 = b.add_node("VISION & LANDMARK EXTRACTION PIPELINE", 50, 190, 1160, 110, CONTAINER_STYLE)
    n_mp = b.add_node("MEDIAPIPE HOLISTIC<br><b>Landmark Extraction</b><br>• Pose (33)<br>• Hands (21+21)<br>• Face (92)<br>Total: 534 Features", 80, 220, 260, 70, BOX_STYLE)
    n_norm = b.add_node("SHOULDER-RELATIVE NORMALIZATION<br>• Center to mid-shoulder origin<br>• Scale by Euclidean shoulder span<br>• Aspect ratio invariance", 400, 220, 320, 70, BOX_STYLE)
    n_buf = b.add_node("TEMPORAL SLIDING BUFFER<br>30-Frame FIFO Queue<br>Shape: (30, 534) Matrix", 780, 220, 220, 70, BOX_STYLE)
    n_route = b.add_node("MODE ROUTER<br>Active Branch Switch", 1040, 220, 140, 70, BOX_STYLE)

    b.add_edge(n_mp, n_norm, "534 Coords", ARROW_STYLE)
    b.add_edge(n_norm, n_buf, "Normalized Vectors", ARROW_STYLE)
    b.add_edge(n_buf, n_route, "Buffer Data", ARROW_STYLE)

    # Layer 3: Dual-Branch Model Inference Engine (V3)
    c3 = b.add_node("DUAL-BRANCH DEEP LEARNING INFERENCE CORE (V3 COMPILED ENGINE)", 50, 320, 1160, 150, CONTAINER_STYLE)
    
    n_static = b.add_node("STATIC SIGN RECOGNITION BRANCH<br><b>Residual Dense MLP (35 Classes)</b><br>• 1D Input Vector (534)<br>• Dense (512, 256, 128, 64) + Residual Skips<br>• BatchNorm, ReLU, Dropout (0.3)<br>• Latency: ~2ms via @tf.function", 100, 360, 360, 95, BOX_STYLE)
    
    n_dyn = b.add_node("DYNAMIC SIGN RECOGNITION BRANCH<br><b>Conv1D + BiLSTM + Bahdanau Attention (11 Classes)</b><br>• Temporal Input (30, 534)<br>• Conv1D (64, 128) -> BiLSTM (128, 64)<br>• Bahdanau Attention Context Pooling<br>• Latency: ~3ms via @tf.function", 520, 360, 390, 95, BOX_STYLE)

    n_debounce = b.add_node("POST-PROCESSING GATE<br>• Softmax Threshold (>85%)<br>• Debounce Consensus Filter<br>• Cooldown & Commit Lock", 950, 360, 230, 95, BOX_STYLE)

    b.add_edge(n_route, n_static, "Static Mode", ARROW_STYLE)
    b.add_edge(n_route, n_dyn, "Dynamic Mode", ARROW_STYLE)
    b.add_edge(n_static, n_debounce, "Class Prob.", ARROW_STYLE)
    b.add_edge(n_dyn, n_debounce, "Class Prob.", ARROW_STYLE)

    # Layer 4: NLP Sentence Structuring Engine
    c4 = b.add_node("NATURAL LANGUAGE PROCESSING (NLP) & SENTENCE STRUCTURING ENGINE", 50, 490, 1160, 120, CONTAINER_STYLE)
    n_gloss = b.add_node("RAW GLOSS ACCUMULATOR<br>Collects committed sign tokens<br>[ 'HELLO', 'NAME', 'YOU', ... ]", 90, 530, 240, 65, BOX_STYLE)
    n_spell = b.add_node("SPELL CHECK & COMPOUNDING<br>Merges fingerspelled letters<br>(e.g., 'R'+'O'+'O'+'P' -> 'ROOP')", 380, 530, 240, 65, BOX_STYLE)
    n_syntax = b.add_node("GLOSS-TO-SENTENCE SYNTHESIZER<br>• ISL SOV to English SVO Grammar Restructuring<br>• Auxiliary Verb & Article Insertion<br>• Synthesizes Fluent Natural English", 670, 530, 330, 65, BOX_STYLE)
    n_eng_out = b.add_node("SYNTHESIZED ENGLISH<br>\"Hello, what is your name?\"", 1040, 530, 140, 65, BOX_STYLE)

    b.add_edge(n_debounce, n_gloss, "Stable Gloss", ARROW_STYLE)
    b.add_edge(n_gloss, n_spell, "Token Stream", ARROW_STYLE)
    b.add_edge(n_spell, n_syntax, "Clean Glosses", ARROW_STYLE)
    b.add_edge(n_syntax, n_eng_out, "Grammar Fixed", ARROW_STYLE)

    # Layer 5: Multilingual Translation Engine (Google API)
    c5 = b.add_node("MULTILINGUAL TRANSLATION & LOCALIZATION ENGINE (GOOGLE TRANSLATE API)", 50, 630, 1160, 120, CONTAINER_STYLE)
    n_api_auth = b.add_node("SECURE API GATEWAY<br>Google Cloud Translation API Client<br>API Key / OAuth2 Verification", 100, 670, 280, 65, BOX_STYLE)
    n_gapi = b.add_node("GOOGLE CLOUD TRANSLATION API<br>Neural Machine Translation (NMT)<br>Language Target Code (hi, ta, te, kn, mr, bn)", 440, 670, 330, 65, DASHED_BOX)
    n_trans_resp = b.add_node("RESPONSE PARSER &<br>LOCALIZATION BUFFER<br>Caches output in selected language", 830, 670, 230, 65, BOX_STYLE)

    b.add_edge(n_eng_out, n_api_auth, "English Text", ARROW_STYLE)
    b.add_edge(n_api_auth, n_gapi, "REST HTTPS Request", DASHED_ARROW)
    b.add_edge(n_gapi, n_trans_resp, "NMT Response JSON", DASHED_ARROW)

    # Layer 6: Output & Delivery Layer
    c6 = b.add_node("OUTPUT PRESENTATION & AUDIO SYNTHESIS", 50, 770, 1160, 90, CONTAINER_STYLE)
    n_text_disp = b.add_node("MULTILINGUAL TEXT DISPLAY<br>Real-time Subtitle / Banner Overlay", 150, 805, 340, 45, ROUNDED_STYLE)
    n_tts = b.add_node("TEXT-TO-SPEECH (TTS) SYNTHESIZER<br>Native Regional Audio Output", 650, 805, 340, 45, ROUNDED_STYLE)

    b.add_edge(n_trans_resp, n_text_disp, "Native Text", ARROW_STYLE)
    b.add_edge(n_trans_resp, n_tts, "TTS Dispatch", ARROW_STYLE)

    b.add_node("Figure 4.1: Comprehensive System Architecture with V3 Dual-Models, NLP Synthesizer, and Google Cloud Translation API",
               200, 890, 850, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 2. MODULAR DESIGN DIAGRAM (4.3.1)
# ==============================================================================
def build_modular_diagram():
    b = DrawIOBuilder("Figure 4.3 Modular Design", "page_modular", width=1200, height=900)
    
    b.add_node("FIGURE 4.3: MODULAR DESIGN HIERARCHICAL DIAGRAM",
               200, 20, 800, 30, TITLE_STYLE)
    
    # Root
    root = b.add_node("ISL TO MULTILINGUAL TRANSLATION SYSTEM", 450, 70, 340, 50, BOX_STYLE)
    
    # 5 Major Modules (Level 2)
    m1 = b.add_node("1.0 FRONTEND &<br>PRESENTATION MODULE", 60, 180, 200, 50, BOX_STYLE)
    m2 = b.add_node("2.0 VISION &<br>FEATURE EXTRACTION", 290, 180, 200, 50, BOX_STYLE)
    m3 = b.add_node("3.0 DUAL-BRANCH<br>INFERENCE MODULE", 520, 180, 200, 50, BOX_STYLE)
    m4 = b.add_node("4.0 NLP & SENTENCE<br>SYNTHESIS MODULE", 750, 180, 200, 50, BOX_STYLE)
    m5 = b.add_node("5.0 GOOGLE TRANSLATE &<br>LOCALIZATION MODULE", 980, 180, 200, 50, BOX_STYLE)

    b.add_edge(root, m1, "", ARROW_STYLE)
    b.add_edge(root, m2, "", ARROW_STYLE)
    b.add_edge(root, m3, "", ARROW_STYLE)
    b.add_edge(root, m4, "", ARROW_STYLE)
    b.add_edge(root, m5, "", ARROW_STYLE)

    # Sub-modules Level 3
    # M1 Submodules
    s1_1 = b.add_node("1.1 Webcam Stream Controller", 60, 270, 200, 40, ROUNDED_STYLE)
    s1_2 = b.add_node("1.2 Real-time HUD & Visual Overlay", 60, 330, 200, 40, ROUNDED_STYLE)
    s1_3 = b.add_node("1.3 Mode Switcher (TAB / M Toggle)", 60, 390, 200, 40, ROUNDED_STYLE)
    s1_4 = b.add_node("1.4 Regional Language Selector UI", 60, 450, 200, 40, ROUNDED_STYLE)
    b.add_edge(m1, s1_1, "", ARROW_STYLE)
    b.add_edge(s1_1, s1_2, "", ARROW_STYLE)
    b.add_edge(s1_2, s1_3, "", ARROW_STYLE)
    b.add_edge(s1_3, s1_4, "", ARROW_STYLE)

    # M2 Submodules
    s2_1 = b.add_node("2.1 MediaPipe Holistic Extractor", 290, 270, 200, 40, ROUNDED_STYLE)
    s2_2 = b.add_node("2.2 Keypoint Concatenator (534 Dims)", 290, 330, 200, 40, ROUNDED_STYLE)
    s2_3 = b.add_node("2.3 Shoulder-Relative Normalizer", 290, 390, 200, 40, ROUNDED_STYLE)
    s2_4 = b.add_node("2.4 30-Frame FIFO Sliding Buffer", 290, 450, 200, 40, ROUNDED_STYLE)
    b.add_edge(m2, s2_1, "", ARROW_STYLE)
    b.add_edge(s2_1, s2_2, "", ARROW_STYLE)
    b.add_edge(s2_2, s2_3, "", ARROW_STYLE)
    b.add_edge(s2_3, s2_4, "", ARROW_STYLE)

    # M3 Submodules
    s3_1 = b.add_node("3.1 Mode Dispatch Router", 520, 270, 200, 40, ROUNDED_STYLE)
    s3_2 = b.add_node("3.2 Static Residual MLP (35 Classes)", 520, 330, 200, 40, ROUNDED_STYLE)
    s3_3 = b.add_node("3.3 Dynamic BiLSTM-Attention (11)", 520, 390, 200, 40, ROUNDED_STYLE)
    s3_4 = b.add_node("3.4 Softmax Threshold & Debounce", 520, 450, 200, 40, ROUNDED_STYLE)
    b.add_edge(m3, s3_1, "", ARROW_STYLE)
    b.add_edge(s3_1, s3_2, "", ARROW_STYLE)
    b.add_edge(s3_2, s3_3, "", ARROW_STYLE)
    b.add_edge(s3_3, s3_4, "", ARROW_STYLE)

    # M4 Submodules
    s4_1 = b.add_node("4.1 Raw Sign Gloss Tokenizer", 750, 270, 200, 40, ROUNDED_STYLE)
    s4_2 = b.add_node("4.2 Spell Compounding & Lexicon", 750, 330, 200, 40, ROUNDED_STYLE)
    s4_3 = b.add_node("4.3 ISL SOV to SVO Grammar Engine", 750, 390, 200, 40, ROUNDED_STYLE)
    s4_4 = b.add_node("4.4 Natural English Synthesizer", 750, 450, 200, 40, ROUNDED_STYLE)
    b.add_edge(m4, s4_1, "", ARROW_STYLE)
    b.add_edge(s4_1, s4_2, "", ARROW_STYLE)
    b.add_edge(s4_2, s4_3, "", ARROW_STYLE)
    b.add_edge(s4_3, s4_4, "", ARROW_STYLE)

    # M5 Submodules
    s5_1 = b.add_node("5.1 Google Cloud Translation Gateway", 980, 270, 200, 40, ROUNDED_STYLE)
    s5_2 = b.add_node("5.2 API Key Auth & Token Manager", 980, 330, 200, 40, ROUNDED_STYLE)
    s5_3 = b.add_node("5.3 Multi-Language Response Parser", 980, 390, 200, 40, ROUNDED_STYLE)
    s5_4 = b.add_node("5.4 Regional Text-to-Speech (TTS)", 980, 450, 200, 40, ROUNDED_STYLE)
    b.add_edge(m5, s5_1, "", ARROW_STYLE)
    b.add_edge(s5_1, s5_2, "", ARROW_STYLE)
    b.add_edge(s5_2, s5_3, "", ARROW_STYLE)
    b.add_edge(s5_3, s5_4, "", ARROW_STYLE)

    b.add_node("Figure 4.3: Modular Decomposition Diagram showing Top-Level Modules and Functional Sub-Components",
               200, 540, 800, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 3. PROPOSED SYSTEM FLOWCHART (4.2)
# ==============================================================================
def build_flowchart():
    b = DrawIOBuilder("Figure 4.2 Flowchart", "page_flowchart", width=1100, height=1300)
    
    b.add_node("FIGURE 4.2: PROPOSED SYSTEM WORKFLOW FLOWCHART",
               150, 20, 800, 30, TITLE_STYLE)
    
    start = b.add_node("START", 475, 70, 150, 40, ROUNDED_STYLE)
    n_init = b.add_node("Initialize Webcam Stream (1280x720)<br>Load Static MLP & Dynamic BiLSTM Models<br>Initialize NLP Tokenizer & Google API Client",
                        350, 140, 400, 50, BOX_STYLE)
    n_cap = b.add_node("Capture Live Video Frame", 450, 220, 200, 40, BOX_STYLE)
    d_detect = b.add_node("Signer Hands /<br>Body Detected?", 475, 290, 150, 70, DIAMOND_STYLE)
    n_wait = b.add_node("Display 'Stand In Frame' /<br>Wait for Detection", 730, 305, 180, 40, BOX_STYLE)
    
    n_extract = b.add_node("Extract MediaPipe Holistic Landmarks<br>(Pose: 33, Hands: 42, Face: 92 = 534 Features)", 380, 390, 340, 45, BOX_STYLE)
    n_norm = b.add_node("Apply Shoulder-Relative Normalization<br>Center origin + Euclidean scale invariant", 400, 465, 300, 45, BOX_STYLE)
    n_buf = b.add_node("Update 30-Frame FIFO Temporal Window Buffer", 400, 540, 300, 40, BOX_STYLE)
    
    d_mode = b.add_node("Active Mode<br>Selection?", 475, 610, 150, 70, DIAMOND_STYLE)
    
    # Static Branch
    n_static_exec = b.add_node("Extract Current Frame (534 Dims)<br>Run Static Residual MLP (@tf.function)<br>Predict from 35 Classes", 180, 710, 260, 55, BOX_STYLE)
    
    # Dynamic Branch
    d_buf_full = b.add_node("Buffer Full<br>(30 Frames)?", 710, 705, 140, 65, DIAMOND_STYLE)
    n_dyn_exec = b.add_node("Pass (30, 534) Sequence<br>Run Conv1D + BiLSTM + Attention<br>Predict from 11 Dynamic Classes", 650, 800, 260, 55, BOX_STYLE)

    d_conf = b.add_node("Confidence >= 85% &<br>Passed Debounce Filter?", 460, 890, 180, 70, DIAMOND_STYLE)
    n_discard = b.add_node("Discard / Maintain Buffer", 730, 905, 170, 40, BOX_STYLE)

    n_commit = b.add_node("Commit Detected Gloss to Buffer<br>Display Live Gloss Ribbon on HUD", 430, 990, 240, 45, BOX_STYLE)
    
    d_end_seq = b.add_node("Sentence End<br>Triggered?", 475, 1065, 150, 65, DIAMOND_STYLE)
    
    n_nlp = b.add_node("NLP Engine: Tokenize & Compound Letters<br>Apply ISL Grammar -> Synthesize Fluent English", 380, 1160, 340, 45, BOX_STYLE)
    
    d_trans = b.add_node("Regional Language<br>Selected?", 475, 1235, 150, 65, DIAMOND_STYLE)
    
    n_gapi = b.add_node("Call Google Cloud Translation API (Secure Key)<br>Receive Native Translation (Hindi, Tamil, etc.)", 690, 1245, 310, 45, DASHED_BOX)
    
    n_out = b.add_node("Render Translated Output Banner<br>Play Native Text-to-Speech (TTS) Audio", 380, 1330, 340, 45, ROUNDED_STYLE)
    
    d_exit = b.add_node("User Pressed<br>'Q' (Exit)?", 475, 1405, 150, 65, DIAMOND_STYLE)
    stop = b.add_node("STOP / RELEASE WEBCAM", 475, 1500, 150, 40, ROUNDED_STYLE)

    # Connections
    b.add_edge(start, n_init, "", ARROW_STYLE)
    b.add_edge(n_init, n_cap, "", ARROW_STYLE)
    b.add_edge(n_cap, d_detect, "", ARROW_STYLE)
    b.add_edge(d_detect, n_wait, "NO", ARROW_STYLE)
    b.add_edge(n_wait, n_cap, "", ARROW_STYLE)
    b.add_edge(d_detect, n_extract, "YES", ARROW_STYLE)
    b.add_edge(n_extract, n_norm, "", ARROW_STYLE)
    b.add_edge(n_norm, n_buf, "", ARROW_STYLE)
    b.add_edge(n_buf, d_mode, "", ARROW_STYLE)

    b.add_edge(d_mode, n_static_exec, "STATIC", ARROW_STYLE)
    b.add_edge(d_mode, d_buf_full, "DYNAMIC", ARROW_STYLE)
    b.add_edge(d_buf_full, n_dyn_exec, "YES", ARROW_STYLE)
    b.add_edge(d_buf_full, n_cap, "NO", ARROW_STYLE)

    b.add_edge(n_static_exec, d_conf, "", ARROW_STYLE)
    b.add_edge(n_dyn_exec, d_conf, "", ARROW_STYLE)

    b.add_edge(d_conf, n_discard, "NO", ARROW_STYLE)
    b.add_edge(n_discard, n_cap, "", ARROW_STYLE)
    b.add_edge(d_conf, n_commit, "YES", ARROW_STYLE)

    b.add_edge(n_commit, d_end_seq, "", ARROW_STYLE)
    b.add_edge(d_end_seq, n_cap, "NO (Continue)", ARROW_STYLE)
    b.add_edge(d_end_seq, n_nlp, "YES (Finalize)", ARROW_STYLE)

    b.add_edge(n_nlp, d_trans, "", ARROW_STYLE)
    b.add_edge(d_trans, n_gapi, "YES", ARROW_STYLE)
    b.add_edge(n_gapi, n_out, "", ARROW_STYLE)
    b.add_edge(d_trans, n_out, "NO (English)", ARROW_STYLE)

    b.add_edge(n_out, d_exit, "", ARROW_STYLE)
    b.add_edge(d_exit, stop, "YES", ARROW_STYLE)
    b.add_edge(d_exit, n_cap, "NO (Next)", ARROW_STYLE)

    b.add_node("Figure 4.2: Comprehensive Execution Flowchart of Real-Time Detection, Inference, NLP Structuring, and Multilingual Translation",
               150, 1560, 800, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 4. SEQUENCE DIAGRAM (4.3.2)
# ==============================================================================
def build_sequence_diagram():
    b = DrawIOBuilder("Figure 4.4 Sequence Diagram", "page_sequence", width=1280, height=850)
    
    b.add_node("FIGURE 4.4: UML SEQUENCE DIAGRAM OF REAL-TIME ISL RECOGNITION & TRANSLATION PIPELINE",
               150, 20, 980, 30, TITLE_STYLE)
    
    # Actors / Objects (Lifeline heads)
    actors = [
        ("User (Signer)", 70, 70),
        ("Frontend Client", 250, 70),
        ("Vision Backend", 430, 70),
        ("V3 Inference Core", 620, 70),
        ("NLP Synthesizer", 820, 70),
        ("Google Translate API", 1010, 70),
    ]
    
    lifeline_x = []
    for name, x, y in actors:
        b.add_node(name, x, y, 140, 40, BOX_STYLE)
        lx = x + 70
        lifeline_x.append(lx)
        # Lifeline vertical line
        b.add_edge(
            b.add_node("", lx, 110, 1, 1, "text;strokeColor=none;fillColor=none;"),
            b.add_node("", lx, 720, 1, 1, "text;strokeColor=none;fillColor=none;"),
            "",
            "endArrow=none;dashed=1;strokeColor=#666666;strokeWidth=1;"
        )

    # Sequence Messages
    msgs = [
        (0, 1, 150, "1. Select Mode & Perform Gesture", ARROW_STYLE),
        (1, 2, 190, "2. Stream Video Frame (OpenCV/Webcam)", ARROW_STYLE),
        (2, 2, 230, "3. MediaPipe Holistic Landmark Extraction", ARROW_STYLE),
        (2, 2, 270, "4. Shoulder-Relative Normalization", ARROW_STYLE),
        (2, 3, 310, "5. Send Normalized Features (30x534 or 1x534)", ARROW_STYLE),
        (3, 3, 350, "6. Execute Compiled @tf.function Graph", ARROW_STYLE),
        (3, 2, 390, "7. Return Predicted Sign Gloss & Confidence", DASHED_ARROW),
        (2, 1, 430, "8. Render Debounced Sign Gloss on HUD", DASHED_ARROW),
        (0, 1, 470, "9. Trigger End-of-Sentence / Commit", ARROW_STYLE),
        (1, 4, 510, "10. Send Accumulated Gloss Sequence", ARROW_STYLE),
        (4, 4, 550, "11. Restructure SOV Grammar -> Fluent English", ARROW_STYLE),
        (4, 1, 590, "12. Return Synthesized English Sentence", DASHED_ARROW),
        (1, 5, 630, "13. Call Translation API (English Text, Target Lang, API Key)", ARROW_STYLE),
        (5, 1, 670, "14. Return Translated Regional Text JSON", DASHED_ARROW),
        (1, 0, 710, "15. Display Native Subtitle & Play TTS Audio", ARROW_STYLE),
    ]

    for s_idx, t_idx, y, text, style in msgs:
        sx = lifeline_x[s_idx]
        tx = lifeline_x[t_idx]
        if s_idx == t_idx:
            # Self call
            b.add_node(text, sx + 10, y - 10, 240, 25, "text;html=1;fontSize=10;fontFamily=Times New Roman;fontStyle=1;align=left;")
            p1 = b.add_node("", sx, y, 1, 1, "text;strokeColor=none;fillColor=none;")
            p2 = b.add_node("", sx + 30, y + 10, 1, 1, "text;strokeColor=none;fillColor=none;")
            p3 = b.add_node("", sx, y + 20, 1, 1, "text;strokeColor=none;fillColor=none;")
            b.add_edge(p1, p2, "", "endArrow=none;strokeColor=#000000;strokeWidth=1.5;")
            b.add_edge(p2, p3, "", ARROW_STYLE)
        else:
            w = abs(tx - sx)
            mx = min(sx, tx)
            b.add_node(text, mx + (w/2) - 130, y - 18, 260, 20, "text;html=1;fontSize=10;fontFamily=Times New Roman;fontStyle=1;align=center;")
            p1 = b.add_node("", sx, y, 1, 1, "text;strokeColor=none;fillColor=none;")
            p2 = b.add_node("", tx, y, 1, 1, "text;strokeColor=none;fillColor=none;")
            b.add_edge(p1, p2, "", style)

    b.add_node("Figure 4.4: UML Sequence Diagram depicting Inter-Component Communication across Client, Vision Engine, NLP, and Google API",
               200, 760, 880, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 5. USE CASE DIAGRAM (4.3.3)
# ==============================================================================
def build_use_case_diagram():
    b = DrawIOBuilder("Figure 4.5 Use Case Diagram", "page_usecase", width=1200, height=900)
    
    b.add_node("FIGURE 4.5: UML USE CASE DIAGRAM FOR ISL MULTILINGUAL TRANSLATION SYSTEM",
               150, 20, 900, 30, TITLE_STYLE)
    
    # System Boundary Box
    sys_box = b.add_node("ISL to Multilingual Translation System Boundary", 300, 70, 600, 750, CONTAINER_STYLE)
    
    # Actors
    act_user = b.add_node("Signer<br>(Deaf/Mute User)", 80, 260, 60, 100, ACTOR_STYLE)
    act_viewer = b.add_node("Recipient<br>(Hearing Audience)", 1050, 260, 60, 100, ACTOR_STYLE)
    act_admin = b.add_node("System Admin /<br>Developer", 80, 600, 60, 100, ACTOR_STYLE)
    act_gapi = b.add_node("Google Cloud<br>Translation API", 1050, 600, 60, 100, ACTOR_STYLE)

    # Use cases inside boundary
    uc1 = b.add_node("Start Live Webcam Stream", 360, 110, 220, 45, ELLIPSE_STYLE)
    uc2 = b.add_node("Toggle Recognition Mode<br>(Static / Dynamic)", 360, 180, 220, 50, ELLIPSE_STYLE)
    uc3 = b.add_node("Perform Sign Gesture", 360, 255, 220, 45, ELLIPSE_STYLE)
    uc4 = b.add_node("View Real-Time Detected Gloss", 360, 325, 220, 45, ELLIPSE_STYLE)
    uc5 = b.add_node("Synthesize English Sentence<br>(NLP Grammar Correction)", 360, 395, 240, 50, ELLIPSE_STYLE)
    uc6 = b.add_node("Select Target Regional Language<br>(Hindi, Tamil, Telugu, etc.)", 640, 430, 230, 50, ELLIPSE_STYLE)
    uc7 = b.add_node("Translate to Native Language<br>(via Google Cloud API)", 460, 500, 260, 50, ELLIPSE_STYLE)
    uc8 = b.add_node("View Multilingual Subtitle Display", 640, 280, 230, 45, ELLIPSE_STYLE)
    uc9 = b.add_node("Listen to Native Speech Audio (TTS)", 640, 355, 230, 45, ELLIPSE_STYLE)
    uc10 = b.add_node("Manage Dataset & Retrain Models", 360, 610, 240, 45, ELLIPSE_STYLE)
    uc11 = b.add_node("Configure Google Translation API Key", 400, 690, 260, 45, ELLIPSE_STYLE)
    uc12 = b.add_node("Execute NMT Translation Service", 680, 630, 210, 45, ELLIPSE_STYLE)

    # Edges from Signer
    b.add_edge(act_user, uc1, "", ARROW_STYLE)
    b.add_edge(act_user, uc2, "", ARROW_STYLE)
    b.add_edge(act_user, uc3, "", ARROW_STYLE)
    b.add_edge(act_user, uc4, "", ARROW_STYLE)
    b.add_edge(act_user, uc6, "", ARROW_STYLE)

    # Includes relationships
    b.add_edge(uc4, uc5, "<<include>>", DASHED_ARROW)
    b.add_edge(uc5, uc7, "<<include>>", DASHED_ARROW)
    b.add_edge(uc6, uc7, "<<include>>", DASHED_ARROW)
    b.add_edge(uc7, uc8, "<<include>>", DASHED_ARROW)
    b.add_edge(uc7, uc9, "<<include>>", DASHED_ARROW)

    # Edges to Recipient
    b.add_edge(uc8, act_viewer, "", ARROW_STYLE)
    b.add_edge(uc9, act_viewer, "", ARROW_STYLE)

    # Edges from Admin
    b.add_edge(act_admin, uc10, "", ARROW_STYLE)
    b.add_edge(act_admin, uc11, "", ARROW_STYLE)

    # Edges to Google API
    b.add_edge(uc7, uc12, "<<delegate>>", DASHED_ARROW)
    b.add_edge(uc12, act_gapi, "", ARROW_STYLE)
    b.add_edge(uc11, act_gapi, "", ARROW_STYLE)

    b.add_node("Figure 4.5: UML Use Case Diagram showing Primary Actors (Signer, Recipient, Admin, Google API) and System Capabilities",
               200, 840, 800, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 6. DFD LEVEL 0 (CONTEXT DIAGRAM)
# ==============================================================================
def build_dfd_level_0():
    b = DrawIOBuilder("Figure 4.6 DFD Level 0", "page_dfd0", width=1100, height=750)
    
    b.add_node("FIGURE 4.6: DATA FLOW DIAGRAM (DFD) LEVEL 0 — CONTEXT DIAGRAM",
               150, 20, 800, 30, TITLE_STYLE)
    
    # Central Process
    p0 = b.add_node("0.0<br><br><b>INDIAN SIGN LANGUAGE TO<br>MULTILINGUAL TEXT & SPEECH<br>TRANSLATION SYSTEM</b>",
                    420, 230, 260, 160, ROUNDED_STYLE)
    
    # External Entities
    ent_user = b.add_node("SIGNER<br>(DEAF/MUTE USER)", 80, 250, 180, 100, EXTERNAL_ENTITY)
    ent_viewer = b.add_node("RECIPIENT<br>(HEARING AUDIENCE)", 840, 120, 180, 100, EXTERNAL_ENTITY)
    ent_gapi = b.add_node("GOOGLE CLOUD<br>TRANSLATION API", 840, 380, 180, 100, DASHED_BOX)
    ent_admin = b.add_node("SYSTEM ADMIN /<br>DEVELOPER", 460, 560, 180, 90, EXTERNAL_ENTITY)

    # Flows: Signer -> System
    b.add_edge(ent_user, p0, "1. Live Video Stream (30 FPS)<br>2. Mode Selection (Static/Dynamic)<br>3. Target Language Choice", ARROW_STYLE)
    b.add_edge(p0, ent_user, "Real-Time Visual HUD Feedback<br>& Detected Sign Glosses", DASHED_ARROW)

    # Flows: System -> Recipient
    b.add_edge(p0, ent_viewer, "1. Fluent Multilingual Subtitle Text<br>2. Synthesized Regional Voice Speech", ARROW_STYLE)

    # Flows: System <-> Google API
    b.add_edge(p0, ent_gapi, "Synthesized English Sentence +<br>Target Language Code + API Key", ARROW_STYLE)
    b.add_edge(ent_gapi, p0, "Translated Regional Text Response", DASHED_ARROW)

    # Flows: Admin <-> System
    b.add_edge(ent_admin, p0, "Model Hyperparameters, Dataset Updates, & API Keys", ARROW_STYLE)
    b.add_edge(p0, ent_admin, "System Health Logs & Accuracy Reports", DASHED_ARROW)

    b.add_node("Figure 4.6: Level 0 DFD (Context Diagram) illustrating Information Boundaries and External Data Exchanges",
               150, 690, 800, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 7. DFD LEVEL 1
# ==============================================================================
def build_dfd_level_1():
    b = DrawIOBuilder("Figure 4.7 DFD Level 1", "page_dfd1", width=1280, height=950)
    
    b.add_node("FIGURE 4.7: DATA FLOW DIAGRAM (DFD) LEVEL 1 — SYSTEM DECOMPOSITION",
               150, 20, 950, 30, TITLE_STYLE)
    
    # Entities
    ent_signer = b.add_node("SIGNER", 50, 120, 130, 70, EXTERNAL_ENTITY)
    ent_viewer = b.add_node("RECIPIENT", 1100, 730, 130, 70, EXTERNAL_ENTITY)
    ent_gapi = b.add_node("GOOGLE TRANSLATE<br>API", 1080, 480, 150, 70, DASHED_BOX)

    # Processes
    p1 = b.add_node("1.0<br>Video Capture &<br>Landmark Extraction", 260, 120, 170, 75, ROUNDED_STYLE)
    p2 = b.add_node("2.0<br>Coordinate Normalization<br>& Buffer Queuing", 520, 120, 180, 75, ROUNDED_STYLE)
    p3 = b.add_node("3.0<br>Dual-Branch Sign<br>Gesture Recognition", 520, 300, 180, 75, ROUNDED_STYLE)
    p4 = b.add_node("4.0<br>NLP Sentence Structuring<br>& Grammar Synthesis", 520, 480, 180, 75, ROUNDED_STYLE)
    p5 = b.add_node("5.0<br>Multilingual Translation<br>& Speech Generation", 790, 480, 180, 75, ROUNDED_STYLE)
    p6 = b.add_node("6.0<br>Output Presentation &<br>Audio Rendering", 790, 730, 180, 75, ROUNDED_STYLE)

    # Data Stores
    ds1 = b.add_node("D1 | Landmark Sliding Buffer (30x534)", 820, 130, 260, 45, DATASTORE_STYLE)
    ds2 = b.add_node("D2 | Trained V3 Keras Model Weights", 210, 315, 250, 45, DATASTORE_STYLE)
    ds3 = b.add_node("D3 | ISL Grammar Lexicon & Dictionary", 210, 495, 250, 45, DATASTORE_STYLE)
    ds4 = b.add_node("D4 | Translation Cache & Session Logs", 520, 660, 260, 45, DATASTORE_STYLE)

    # Data Flows
    b.add_edge(ent_signer, p1, "Raw Video Stream", ARROW_STYLE)
    b.add_edge(p1, p2, "534 Unnormalized Coordinates", ARROW_STYLE)
    b.add_edge(p2, ds1, "Store Normalized Vectors", ARROW_STYLE)
    b.add_edge(ds1, p3, "30-Frame Sequence / 1-Frame Vector", ARROW_STYLE)
    b.add_edge(ds2, p3, "Model Weights & Graph", ARROW_STYLE)
    b.add_edge(p3, p4, "Debounced Sign Gloss Stream", ARROW_STYLE)
    b.add_edge(ds3, p4, "Syntax & Compounding Rules", ARROW_STYLE)
    b.add_edge(p4, p5, "Synthesized English Sentence", ARROW_STYLE)
    b.add_edge(p5, ent_gapi, "HTTPS Translation Request", DASHED_ARROW)
    b.add_edge(ent_gapi, p5, "Regional Text JSON Response", DASHED_ARROW)
    b.add_edge(p5, ds4, "Log Translated Output", ARROW_STYLE)
    b.add_edge(p5, p6, "Localized Text & Audio Dispatch", ARROW_STYLE)
    b.add_edge(p6, ent_viewer, "Subtitles & Spoken Audio", ARROW_STYLE)

    # User Feedback Flow
    b.add_edge(p3, ent_signer, "Real-Time Detected Gloss", DASHED_ARROW)

    b.add_node("Figure 4.7: Level 1 DFD illustrating Main Sub-Processes, Inter-Process Data Pipelines, and System Data Stores",
               200, 870, 880, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# 8. DFD LEVEL 2 (DECOMPOSITION OF CLASSIFICATION & TRANSLATION PIPELINES)
# ==============================================================================
def build_dfd_level_2():
    b = DrawIOBuilder("Figure 4.8 DFD Level 2", "page_dfd2", width=1280, height=980)
    
    b.add_node("FIGURE 4.8: DATA FLOW DIAGRAM (DFD) LEVEL 2 — DETAILED PROCESS DECOMPOSITION",
               150, 20, 980, 30, TITLE_STYLE)
    
    # Section A: Decomposition of Process 3.0 (Sign Classification)
    b.add_node("DECOMPOSITION OF PROCESS 3.0: DUAL-BRANCH CLASSIFICATION & DEBOUNCING",
               50, 70, 1180, 390, CONTAINER_STYLE)
    
    in_feat = b.add_node("Normalized Features<br>(from D1)", 70, 160, 140, 50, BOX_STYLE)
    p3_1 = b.add_node("3.1<br>Mode Routing<br>Dispatcher", 270, 150, 140, 70, ROUNDED_STYLE)
    
    p3_2 = b.add_node("3.2<br>Static Sign Inference<br>(Residual Dense MLP)", 480, 110, 190, 65, ROUNDED_STYLE)
    p3_3 = b.add_node("3.3<br>Dynamic Sign Inference<br>(BiLSTM + Attention)", 480, 200, 190, 65, ROUNDED_STYLE)
    
    p3_4 = b.add_node("3.4<br>Confidence Gate &<br>Threshold Filter (>85%)", 740, 150, 180, 70, ROUNDED_STYLE)
    p3_5 = b.add_node("3.5<br>Consecutive Frame<br>Debounce & Commit", 980, 150, 180, 70, ROUNDED_STYLE)

    b.add_edge(in_feat, p3_1, "Feature Vectors", ARROW_STYLE)
    b.add_edge(p3_1, p3_2, "Single Vector (534) [Static Mode]", ARROW_STYLE)
    b.add_edge(p3_1, p3_3, "Sequence Matrix (30, 534) [Dynamic Mode]", ARROW_STYLE)
    b.add_edge(p3_2, p3_4, "Raw Softmax Probs", ARROW_STYLE)
    b.add_edge(p3_3, p3_4, "Raw Softmax Probs", ARROW_STYLE)
    b.add_edge(p3_4, p3_5, "High-Confidence Label", ARROW_STYLE)

    # Section B: Decomposition of Process 4.0 & 5.0 (NLP & Google Translation)
    b.add_node("DECOMPOSITION OF PROCESS 4.0 & 5.0: NLP SYNTHESIS & GOOGLE TRANSLATION PIPELINE",
               50, 480, 1180, 420, CONTAINER_STYLE)
    
    p4_1 = b.add_node("4.1<br>Gloss Buffer Tokenizer<br>& Character Compounding", 100, 560, 190, 70, ROUNDED_STYLE)
    p4_2 = b.add_node("4.2<br>ISL Grammar Syntax<br>Restructuring Engine", 360, 560, 190, 70, ROUNDED_STYLE)
    p4_3 = b.add_node("4.3<br>Natural English<br>Sentence Synthesizer", 620, 560, 190, 70, ROUNDED_STYLE)
    
    p5_1 = b.add_node("5.1<br>Google API Request<br>Formatter & Auth Header", 880, 560, 190, 70, DASHED_BOX)
    
    ext_gapi2 = b.add_node("GOOGLE CLOUD<br>TRANSLATE NMT", 1090, 720, 130, 60, EXTERNAL_ENTITY)
    
    p5_2 = b.add_node("5.2<br>Multi-Language JSON<br>Response Parser", 880, 720, 170, 65, ROUNDED_STYLE)
    p5_3 = b.add_node("5.3<br>Regional TTS Audio<br>& Subtitle Dispatcher", 580, 720, 190, 65, ROUNDED_STYLE)

    b.add_edge(p3_5, p4_1, "Committed Sign Gloss Stream", ARROW_STYLE)
    b.add_edge(p4_1, p4_2, "Tokenized Word Sequence", ARROW_STYLE)
    b.add_edge(p4_2, p4_3, "Reordered SVO Structure", ARROW_STYLE)
    b.add_edge(p4_3, p5_1, "Fluent English String", ARROW_STYLE)
    b.add_edge(p5_1, ext_gapi2, "HTTPS POST (Payload + API Key)", DASHED_ARROW)
    b.add_edge(ext_gapi2, p5_2, "Translated JSON String", DASHED_ARROW)
    b.add_edge(p5_2, p5_3, "Localized Native Text", ARROW_STYLE)

    b.add_node("Figure 4.8: Level 2 DFD depicting Granular Sub-Process Workflows for Classification (3.0), NLP (4.0), and Translation (5.0)",
               200, 920, 880, 30, CAPTION_STYLE)

    return b


# ==============================================================================
# MAIN EXECUTION: Generate individual .drawio files and Master multi-page file
# ==============================================================================
def main():
    builders = [
        ("architecture_diagram.drawio", build_architecture_diagram()),
        ("modular_design_diagram.drawio", build_modular_diagram()),
        ("proposed_system_flowchart.drawio", build_flowchart()),
        ("sequence_diagram.drawio", build_sequence_diagram()),
        ("use_case_diagram.drawio", build_use_case_diagram()),
        ("dfd_level_0.drawio", build_dfd_level_0()),
        ("dfd_level_1.drawio", build_dfd_level_1()),
        ("dfd_level_2.drawio", build_dfd_level_2()),
    ]

    # Save individual .drawio files
    for filename, b in builders:
        filepath = os.path.join(OUTPUT_DIR, filename)
        xml_content = b.export_drawio_xml()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"Generated: {filepath}")

    # Generate master multi-page all_isl_diagrams.drawio file
    master_root = ET.Element("mxfile", host="app.diagrams.net", version="21.0.0")
    for _, b in builders:
        diag_el = b.to_diagram_element()
        master_root.append(diag_el)
    
    master_path = os.path.join(OUTPUT_DIR, "all_isl_diagrams.drawio")
    master_xml = ET.tostring(master_root, encoding="utf-8", xml_declaration=True).decode("utf-8")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_xml)
    print(f"Generated Master Multi-Page File: {master_path}")

if __name__ == "__main__":
    main()
