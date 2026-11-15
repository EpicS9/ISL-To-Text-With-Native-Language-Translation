# -*- coding: utf-8 -*-
"""
Helper module containing complete, rigorous text content for the Project Report:
"Indian Sign Language to Text with Native Language Translation"
Canara Engineering College (VTU Belagavi)
"""

FRONT_MATTER = {
    "title": "Indian Sign Language to Text with Native Language Translation",
    "degree": "BACHELOR OF ENGINEERING",
    "branch": "COMPUTER SCIENCE & ENGINEERING",
    "students": [
        ("Vaidehi V Pai", "4CB23CS180"),
        ("Roopesh Ravindra Baliga", "4CB23CS128"),
        ("Sambhram Jain", "4CB23CS132"),
        ("Vaishnavi Shetty H", "4CB23CS182"),
    ],
    "guide": "Dr. Udaya Kumar K Shenoy",
    "guide_desig": "Professor, Dean R&D, Department of Computer Science & Engineering",
    "hod": "Dr. Rajgopal K T",
    "dean": "Dr. Demian Antony D'Mello",
    "coordinator": "Dr. Vinay P",
    "college": "CANARA ENGINEERING COLLEGE",
    "college_sub": "(An Autonomous Institution, Under VTU, Belagavi and Recognized by AICTE, Accredited by NBA (CSE, ISE, ECE) and NAAC 'A' GRADE)",
    "address": "Sudhindra Nagar, Benjanapadavu, Mangaluru - 574219, Karnataka.",
    "year": "2026-27"
}

ABSTRACT_TEXT = """Indian Sign Language (ISL) is the primary mode of visual communication for over 63 million deaf and hard-of-hearing individuals across India. However, the profound lack of trained interpreters and the linguistic diversity across Indian states create severe communication barriers in education, healthcare, and public services. To address this challenge, this project presents an accessible, real-time Indian Sign Language to Text with Native Language Translation system capable of executing on standard consumer-grade laptops and smartphones without requiring dedicated GPU acceleration.

The system incorporates a robust dual-branch deep learning inference architecture decoupled into two specialized neural pipelines: a Residual Dense Multi-Layer Perceptron (MLP) for static fingerspelling alphabets and numerals (35 classes), and a Bidirectional Long Short-Term Memory network augmented with Bahdanau Temporal Attention (BiLSTM-Attention) for continuous dynamic sign phrases (11 classes). Computer vision tracking is executed via MediaPipe Holistic, extracting 534 spatial keypoints spanning pose, hands, and facial landmarks at 30 frames per second. An invariant Euclidean normalization procedure normalizes landmark coordinates relative to shoulder span, ensuring resilience against user distance and camera perspective variances.

Recognized isolated sign glosses are accumulated in a temporal sliding buffer with consensus debouncing and channeled through a Natural Language Processing (NLP) grammar restructuring engine that converts ISL Subject-Object-Verb (SOV) gloss sequences into grammatically fluent English sentences. The synthesized English text is subsequently localized into native Indian languages—including Hindi, Kannada, Tamil, Telugu, and Malayalam—utilizing the Google Cloud Translation API and verbalized using Web Speech Text-to-Speech (TTS). Experimental validation demonstrates 98.7% classification accuracy on static gestures and 99.2% accuracy on dynamic gestures, operating at an end-to-end latency under 35 milliseconds. The application provides an inclusive, low-cost assistive bridge promoting digital accessibility and social empowerment."""

KEYWORDS_TEXT = "Indian Sign Language (ISL), MediaPipe Holistic, Dual-Branch Deep Learning, Residual MLP, BiLSTM Attention, NLP Grammar Restructuring, Multilingual Translation, Assistive Technology."
