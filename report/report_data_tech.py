# -*- coding: utf-8 -*-
"""
Technical content for Chapters 1, 3, 4, 5, 6, 7 and Appendices.
Filled with comprehensive, rigorous academic text tailored specifically for the
Indian Sign Language to Multilingual Translation System.
"""

CH1_CONTENT = {
    "background": """Communication is a fundamental aspect of human interaction, yet nearly 63 million people in India who are deaf or hard-of-hearing face daily challenges due to the limited understanding of Indian Sign Language (ISL) among the general population. ISL is a sophisticated, naturally evolved visual-spatial language that utilizes simultaneous hand gestures, manual fingerspelling, body kinematics, and facial expressions to convey syntactic and semantic meaning. However, the severe shortage of certified sign language interpreters and minimal societal familiarity with ISL establish persistent communication barriers in essential public spheres including primary healthcare, education, legal proceedings, and public administration.

With recent breakthroughs in Artificial Intelligence (AI), Machine Learning (ML), and Computer Vision, assistive technologies can now bridge this societal divide. Modern vision pipelines enable non-intrusive landmark extraction directly from ordinary monocular camera streams without requiring costly specialized sensors or electronic data gloves. Concurrently, advancements in deep neural networks and Natural Language Processing (NLP) facilitate accurate sequence-to-sequence modeling, grammatical re-ordering, and neural machine translation into regional languages, making assistive communication truly inclusive in a multilingual subcontinent like India.

This project operates at the confluence of deep learning, computer vision, and social empowerment. It focuses on engineering an accessible, real-time communication platform that translates both static and dynamic ISL gestures into fluent English text and localized Indian regional speech, empowering the deaf community with autonomous, barrier-free interaction.""",

    "motivation": """Communication is an intrinsic human right, yet deaf and hard-of-hearing individuals frequently encounter disenfranchisement due to widespread communication mismatches. In a linguistically diverse country like India with 22 officially recognized constitutional languages, bridging this gap is further compounded by regional dialect barriers. While sign language systems developed in Western contexts focus predominantly on American Sign Language (ASL), Indian Sign Language possesses distinctive grammatical structures, two-handed manual alphabets, and culture-specific idiomatic expressions that cannot be interpreted by ASL models.

Traditional sign translation approaches either rely on cumbersome sensor-instrumented gloves that hinder natural signing movement or are confined to isolated static alphabet classification under artificial laboratory lighting. There is an urgent imperative for an intelligent, non-invasive, vision-based framework capable of recognizing both static letters and continuous dynamic phrases in real time. The system must process continuous webcam input, synthesize fluent natural sentences conforming to standard grammatical conventions, translate the synthesized text into native regional languages, and synthesize spoken audio on commodity, low-cost consumer hardware without necessitating high-end discrete GPUs.""",

    "objectives": [
        ("Empower the Deaf Community", "Engineer an accessible, real-time assistive translation system converting Indian Sign Language gestures into clear, fluent text and regional voice audio to foster seamless bidirectional dialogue."),
        ("Dual-Branch Gesture Recognition", "Design and train a decoupled V3 neural architecture comprising a Residual Dense MLP for 35 static handshapes and a Bidirectional LSTM with Bahdanau Temporal Attention for 11 continuous dynamic phrases."),
        ("Multi-Tier NLP Grammar Synthesis", "Implement an intelligent text restructuring engine that transforms raw ISL Subject-Object-Verb (SOV) gloss sequences and fingerspelled tokens into coherent, grammatically sound English sentences."),
        ("Regional Multilingual Localization", "Integrate cloud-based Neural Machine Translation (NMT) via the Google Cloud Translation API to localize synthesized English into major Indian languages including Hindi, Kannada, Tamil, Telugu, and Malayalam."),
        ("Low-Cost, CPU-Optimized Deployment", "Optimize feature extraction pipelines and deep learning graphs using TensorFlow Graph compilation to achieve real-time throughput (>30 FPS) on standard consumer laptops and smartphones without requiring dedicated GPU hardware.")
    ],

    "scope_limitations": """The scope of this project encompasses the end-to-end design, implementation, and empirical evaluation of an interactive, web-based ISL translation studio. The vision pipeline leverages MediaPipe Holistic to extract 534 spatial landmark coordinates encompassing pose, hand joints, and facial contours. The static recognition branch covers 35 classes including the complete English alphabets (A–Z) and numerals (1–9). The dynamic sequence branch models 11 temporal conversational gestures spanning daily interactions (e.g., 'Hello', 'Thank You', 'Welcome', 'Good Morning', 'How are you', 'Please', 'Help', 'Name', 'What'). A temporal debounce filtering mechanism and confidence gating threshold ensure jitter-free recognition. The application delivers real-time Heads-Up Display (HUD) feedback, dynamic subtitle banners, and regional voice synthesis via the Web Speech API.

The system's operational constraints include sensitivity to extreme ambient illumination variations (below 100 lux), substantial camera motion blur during overly rapid signing transitions, and severe physical occlusion of hand joints. Additionally, grammatical translation currently focuses on conversational phrase structures and isolated compound expressions rather than extensive paragraph-length discourse. Dynamic classification relies on a 30-frame temporal window, which requires signers to execute gestures at relatively uniform temporal tempos.""",

    "relevance_type": """This project addresses critical United Nations Sustainable Development Goals (SDGs), notably Reduced Inequalities (SDG 10) and Quality Education (SDG 4). By providing a free, low-barrier, browser-accessible translation interface, it enables deaf students to engage actively in conventional classrooms and allows hard-of-hearing citizens to navigate public service kiosks, healthcare triage counters, and bank transactions independently.

The project is classified as an Applied Engineering and Research project. It combines original machine learning research—specifically landmark-space temporal attention mechanisms and Euclidean shoulder-span invariance—with comprehensive full-stack software engineering, deploying an asynchronous FastAPI backend and a responsive React/Vite web studio.""",

    "organization": """This report is systematically structured into seven comprehensive chapters:
Chapter 1 introduces the project background, motivation, research objectives, scope, limitations, and societal relevance.
Chapter 2 presents a rigorous literature survey reviewing 20 recent peer-reviewed publications, identifying critical research gaps and providing a comparative synthesis.
Chapter 3 outlines the Software Requirements Specification (SRS), formalizing functional, non-functional, interface, hardware, and software requirements.
Chapter 4 details the System Design, encompassing the architectural diagram, proposed execution flowchart, modular design, UML sequence and use case diagrams, control flow activity diagrams, and multi-level Data Flow Diagrams (DFD Level 0, 1, and 2).
Chapter 5 elaborates the Implementation phase, detailing software tools, hardware configurations, core mathematical algorithms, programming styles, coding standards, and pseudocode specifications.
Chapter 6 analyzes experimental Results and Discussions, software testing methodologies, verification criteria tables, and comparative benchmark evaluations.
Chapter 7 presents final Conclusions and outlines prospective Future Work, followed by comprehensive References and formal Appendices."""
}

CH3_CONTENT = {
    "functional": [
        ("a) Gesture Recognition Module", "The vision pipeline must acquire continuous monocular RGB video feeds at 30 FPS, extract 534 spatial holistic landmarks (pose, hands, face), and execute normalized feature routing to classify both static handshapes and temporal dynamic sequences with high confidence."),
        ("b) Real-Time Inference & Debouncing", "The inference engine must process incoming feature vectors within 35 ms, utilizing a temporal consensus debounce filter across consecutive frames to eliminate spurious transition flickers before committing recognized sign glosses."),
        ("c) Text Conversion & Grammar Module", "The NLP engine must accumulate committed glosses, compound consecutive fingerspelled alphabetic characters into complete lexical words, and restructure ISL SOV syntax into grammatically fluent SVO English sentences."),
        ("d) Multilingual Translation Module", "The system must communicate securely with the Google Cloud Translation API to localize generated English sentences into target Indian languages (Hindi, Kannada, Tamil, Telugu, Malayalam) with round-trip latency under 300 ms."),
        ("e) Text-to-Speech (TTS) Module", "The web presentation tier must invoke the client-side Web Audio / Speech Synthesis API to verbalize the translated native text in natural speech corresponding to the selected regional language."),
        ("f) Interactive User Interface", "The web studio must render an accessible, high-contrast Heads-Up Display (HUD) overlay displaying bounding landmarks, live confidence metrics, a running gloss ribbon, and a localized subtitle banner."),
        ("g) System Reliability & Fail-Safe", "The application must maintain exceptional runtime stability, gracefully handling missing hand detections, network translation drops, and camera disconnection without application crash.")
    ],
    "non_functional": [
        ("Safety Requirements", "The application handles all video processing in local volatile memory. No video streams or raw facial frames are permanently stored or uploaded to third-party cloud servers, guaranteeing absolute biometric privacy for signers. In accordance with data protection mandates, only text strings are dispatched to translation endpoints via secure TLS/HTTPS."),
        ("Performance Requirements", "Inference throughput must sustain a minimum of 25 FPS on commodity multi-core CPUs. Deep learning forward-pass latency must remain below 10 ms for the static MLP and below 15 ms for the dynamic BiLSTM. Translation turnaround time must not exceed 500 ms under standard 4G/broadband connectivity."),
        ("Usability & Accessibility", "The graphic interface must adhere to WCAG 2.1 AA accessibility standards, featuring high-contrast color palettes, intuitive icon buttons, keyboard shortcuts, and clear visual indicators for deaf signers."),
        ("Portability & Scalability", "The application must be completely platform-agnostic, functioning across modern web browsers (Chrome, Edge, Firefox, Safari) and containerized backends on Windows, Linux, and macOS platforms.")
    ],
    "ui_design": """The user interface is engineered as an accessible, high-performance web dashboard featuring a dark-mode glassmorphic theme. Key UI components include:
1. Live Video Canvas: Displays real-time camera feed overlaid with MediaPipe skeletal keypoint skeletons and posture alignment guides.
2. Mode & Status Banner: Visually indicates active inference mode (STATIC vs DYNAMIC), frame rate (FPS), and system connection health.
3. Detected Gloss Ribbon: Displays chronological sequence of verified sign tokens awaiting sentence finalization.
4. Output Subtitle Banner: Prominently renders synthesized English text and native language translation with font scaling for distance viewing.
5. Control & Language Bar: Provides one-click language selection dropdown, speech audio replay button, sentence commit trigger, and session reset button.""",

    "hw_sw_requirements": {
        "hardware": [
            "Processor: Dual-Core Intel Core i3 / AMD Ryzen 3 or higher (Intel Core i5 / Ryzen 5 recommended)",
            "Memory: 4 GB DDR4 RAM minimum (8 GB DDR4 recommended)",
            "Camera: Standard integrated or external USB Webcam (720p @ 30 FPS minimum)",
            "Storage: 1 GB available SSD/HDD storage space",
            "Network: Active broadband/Wi-Fi connection (required only for cloud translation API)"
        ],
        "software": [
            "Operating System: Windows 10/11 (64-bit), Ubuntu 20.04/22.04 LTS, or macOS 12+",
            "Backend Runtime: Python 3.10 or 3.11 with FastAPI and Uvicorn ASGI server",
            "Deep Learning Libraries: TensorFlow 2.19, Keras, NumPy, Scikit-learn",
            "Computer Vision: OpenCV-Python, MediaPipe Holistic",
            "Frontend Framework: React 18, Vite, HTML5 Canvas API, Web Speech API",
            "Cloud Services: Google Cloud Translation API (REST HTTPS v2)"
        ]
    }
}
