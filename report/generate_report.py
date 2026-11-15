# -*- coding: utf-8 -*-
"""
Master Report Generator for:
"Indian Sign Language to Text with Native Language Translation"
Visvesvaraya Technological University (VTU) / Canara Engineering College
Compiles both ISL_Project_Report.html -> ISL_Project_Report.pdf and ISL_Project_Report.docx.
"""

import os
import sys
import subprocess
import pymupdf
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_data_front import FRONT_MATTER, ABSTRACT_TEXT, KEYWORDS_TEXT
from report_data_lit import LITERATURE_ARTICLES, COMPARISON_TABLES, SUMMARY_CH2, REFERENCES
from report_data_tech import CH1_CONTENT, CH3_CONTENT
from report_data_design import CH4_CONTENT, CH5_CONTENT, CH6_CONTENT, CH7_CONTENT, APPENDICES_CONTENT

OUTPUT_DIR = r"c:\Dev\Final_training\ISL_to_Text_Translation\report"
HTML_PATH = os.path.join(OUTPUT_DIR, "ISL_Project_Report.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "ISL_Project_Report.pdf")
DOCX_PATH = os.path.join(OUTPUT_DIR, "ISL_Project_Report.docx")
IMG_DIR = os.path.join(OUTPUT_DIR, "images")

def p_split(txt):
    if not txt:
        return ['', '', '', '', '']
    res = txt.split('\n\n')
    while len(res) < 5:
        res.append('')
    return res


def build_html():
    print("Generating complete academic HTML report...")
    
    html = []
    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Indian Sign Language to Text with Native Language Translation - Project Report</title>
<style>
@page {
  size: A4 portrait;
  margin: 20mm 20mm 20mm 25mm;
}

body {
  font-family: 'Times New Roman', Times, 'TeX Gyre Termes', serif;
  font-size: 11.5pt;
  line-height: 1.55;
  color: #111;
  background-color: #fff;
  margin: 0;
  padding: 0;
  text-align: justify;
}

.page {
  page-break-after: always;
  /* no min-height */
  position: relative;
  box-sizing: border-box;
}

.running-header {
  border-bottom: 1px solid #777;
  font-size: 9pt;
  font-style: italic;
  display: flex;
  justify-content: space-between;
  padding-bottom: 3px;
  margin-bottom: 20px;
}

.running-footer {
  border-top: 1px solid #777;
  font-size: 8.5pt;
  display: flex;
  justify-content: space-between;
  padding-top: 3px;
  margin-top: 25px;
}

h1.chapter-title {
  font-size: 18pt;
  font-weight: bold;
  margin-top: 30px;
  margin-bottom: 20px;
  text-align: left;
}

h1.prelim-title {
  font-size: 18pt;
  font-weight: bold;
  margin-top: 30px;
  margin-bottom: 25px;
  text-align: left;
}

h2 {
  font-size: 13pt;
  font-weight: bold;
  margin-top: 18px;
  margin-bottom: 10px;
}

h3 {
  font-size: 12pt;
  font-weight: bold;
  margin-top: 14px;
  margin-bottom: 6px;
}

p {
  margin-top: 0;
  margin-bottom: 10px;
  text-indent: 1.5em;
}

.no-indent {
  text-indent: 0 !important;
}

/* Title Page styling */
.title-page {
  text-align: center;
  padding-top: 10px;
}
.title-page h2 {
  font-size: 13pt;
  font-weight: normal;
  margin-bottom: 12px;
}
.title-page .vtu-logo {
  width: 90px;
  height: auto;
  margin: 10px auto;
}
.title-page .project-report-title {
  font-size: 12pt;
  font-weight: bold;
  letter-spacing: 1px;
  margin-top: 20px;
  margin-bottom: 5px;
}
.title-page .project-main-title {
  font-size: 15pt;
  font-weight: bold;
  margin: 10px 0;
  line-height: 1.3;
}
.title-page .sub-text {
  font-size: 11pt;
  font-style: italic;
  margin: 12px 0 4px 0;
}
.title-page .degree-title {
  font-size: 12.5pt;
  font-weight: bold;
  margin: 4px 0;
}
.title-page .dept-name {
  font-size: 11.5pt;
  font-weight: bold;
  margin-bottom: 15px;
}
.title-page .submitted-by {
  font-size: 11.5pt;
  font-style: italic;
  margin-top: 12px;
  margin-bottom: 8px;
}
.title-page .students-table {
  width: 65%;
  margin: 0 auto;
  font-size: 11.5pt;
  border-collapse: collapse;
}
.title-page .students-table td {
  padding: 3px 8px;
  border: none;
}
.title-page .guidance-text {
  font-size: 11.5pt;
  font-style: italic;
  margin-top: 16px;
  margin-bottom: 4px;
}
.title-page .guide-name {
  font-size: 11.5pt;
  font-weight: bold;
  margin: 0;
}
.title-page .guide-desig {
  font-size: 10pt;
  margin: 0;
}
.title-page .college-logo {
  width: 75px;
  height: auto;
  margin: 12px auto;
}
.title-page .college-dept {
  font-size: 11.5pt;
  font-weight: bold;
  margin: 2px 0;
}
.title-page .college-name {
  font-size: 13.5pt;
  font-weight: bold;
  margin: 4px 0;
}
.title-page .college-sub {
  font-size: 9pt;
  margin: 2px 0;
  line-height: 1.25;
}
.title-page .college-address {
  font-size: 10.5pt;
  font-weight: bold;
  margin: 4px 0;
}
.title-page .academic-year {
  font-size: 12pt;
  font-weight: bold;
  margin-top: 12px;
}

/* Certificate & Declaration */
.cert-header {
  text-align: center;
  margin-bottom: 20px;
}
.cert-header h2 {
  margin: 0;
  font-size: 13pt;
}
.cert-header p {
  margin: 2px 0;
  font-size: 9pt;
  text-indent: 0;
}
.cert-title {
  text-align: center;
  font-size: 14pt;
  font-weight: bold;
  letter-spacing: 2px;
  margin: 25px 0 15px 0;
}
.sign-grid {
  display: flex;
  justify-content: space-between;
  margin-top: 35px;
  text-align: left;
}
.sign-grid div {
  width: 45%;
}
.ext-viva {
  margin-top: 35px;
}

/* Tables */
table.academic-table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 9.5pt;
  line-height: 1.35;
}
table.academic-table th, table.academic-table td {
  border: 1px solid #444;
  padding: 5px 7px;
  vertical-align: top;
}
table.academic-table th {
  background-color: #f4f4f4;
  font-weight: bold;
  text-align: left;
}

/* Figures */
.figure-container {
  text-align: center;
  margin: 16px 0;
  page-break-inside: avoid;
}
.figure-container img {
  max-width: 96%;
  max-height: 460px;
  border: 1px solid #ccc;
  padding: 3px;
  background: #fff;
  border-radius: 3px;
}
.figure-caption {
  font-size: 10pt;
  margin-top: 6px;
  font-weight: normal;
}

/* Code block */
pre.code-block {
  background: #f8f9fa;
  border: 1px solid #ccc;
  padding: 8px 12px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 9pt;
  line-height: 1.35;
  border-radius: 4px;
  page-break-inside: avoid;
  white-space: pre-wrap;
}

/* TOC lines */
.toc-line {
  display: flex;
  justify-content: space-between;
  margin: 3px 0;
  font-size: 10.5pt;
}
.toc-line .title {
  text-align: left;
}
.toc-line .dots-leader {
  flex-grow: 1;
  border-bottom: 1px dotted #888;
  margin: 0 5px 3px 5px;
}
.toc-line .pnum {
  text-align: right;
  min-width: 20px;
}
.toc-section {
  padding-left: 20px;
}
.toc-subsection {
  padding-left: 40px;
  font-size: 10pt;
}
</style>
</head>
<body>
""")

    # Helper for page headers/footers
    def header_footer(chap_num="", pnum=""):
        return f"""
<div class="running-header">
  <span>Indian Sign Language to Text with Native Language Translation.</span>
  <span>{f'Chapter {chap_num}' if chap_num else ''}</span>
</div>
<div class="running-footer">
  <span>Department of Computer Science & Engineering, CEC, Benjanapadavu,Mangaluru</span>
  <span>{f'Page {pnum}' if pnum else ''}</span>
</div>
"""

    # PAGE 1: TITLE PAGE
    html.append(f"""
<div class="page title-page">
  <h2>Visvesvaraya Technological University, Belagavi – 590018.</h2>
  <img src="images/logo_1.jpeg" class="vtu-logo" alt="VTU Emblem" />
  <div class="project-report-title">PROJECT REPORT<br>ON</div>
  <div class="project-main-title">{FRONT_MATTER['title']}</div>
  <div class="sub-text">Submitted in partial fulfillment for the award of degree of</div>
  <div class="degree-title">{FRONT_MATTER['degree']}</div>
  <div class="sub-text">in</div>
  <div class="dept-name">{FRONT_MATTER['branch']}</div>
  <div class="submitted-by">Submitted by</div>
  <table class="students-table">
    <tr><td>{FRONT_MATTER['students'][0][0]}</td><td style="text-align:right;">{FRONT_MATTER['students'][0][1]}</td></tr>
    <tr><td>{FRONT_MATTER['students'][1][0]}</td><td style="text-align:right;">{FRONT_MATTER['students'][1][1]}</td></tr>
    <tr><td>{FRONT_MATTER['students'][2][0]}</td><td style="text-align:right;">{FRONT_MATTER['students'][2][1]}</td></tr>
    <tr><td>{FRONT_MATTER['students'][3][0]}</td><td style="text-align:right;">{FRONT_MATTER['students'][3][1]}</td></tr>
  </table>
  <div class="guidance-text">Under the Guidance of</div>
  <div class="guide-name">{FRONT_MATTER['guide']}</div>
  <div class="guide-desig">{FRONT_MATTER['guide_desig']}</div>
  <img src="images/logo_2.jpeg" class="college-logo" alt="Canara College Logo" />
  <div class="college-dept">DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</div>
  <div class="college-name">{FRONT_MATTER['college']}</div>
  <div class="college-sub">{FRONT_MATTER['college_sub']}</div>
  <div class="college-address">{FRONT_MATTER['address']}</div>
  <div class="academic-year">{FRONT_MATTER['year']}</div>
</div>
""")

    # PAGE 2: CERTIFICATE
    html.append(f"""
<div class="page">
  <div class="cert-header">
    <div style="font-size: 14pt; font-weight: bold;">{FRONT_MATTER['college']}</div>
    <p>{FRONT_MATTER['college_sub']}</p>
    <p style="font-weight: bold;">{FRONT_MATTER['address']}</p>
    <div style="font-size: 12pt; font-weight: bold; margin-top: 10px;">DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</div>
    <img src="images/logo_2.jpeg" style="width: 70px; height: auto; margin: 12px auto;" alt="Canara Emblem" />
  </div>
  <div class="cert-title">CERTIFICATE</div>
  <p>Certified that the project work entitled <strong>“{FRONT_MATTER['title']}”</strong> carried out by</p>
  <table style="width: 70%; margin: 12px auto; font-size: 11pt;">
    <tr><td><strong>{FRONT_MATTER['students'][0][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][0][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][1][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][1][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][2][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][2][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][3][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][3][1]}</strong></td></tr>
  </table>
  <p>the bonafide students of VII semester Department of Computer Science &amp; Engineering in partial fulfillment for the award of Bachelor of Engineering in Department of Computer Science &amp; Engineering of the Visvesvaraya Technological University, Belagavi during the year {FRONT_MATTER['year']}. It is certified that all corrections/suggestions indicated for Internal Assessment as indicated during internal assessment. The project report has been approved as it satisfies the academic requirements in respect of project work prescribed for the said degree.</p>
  <div class="sign-grid">
    <div><strong>{FRONT_MATTER['guide']}</strong><br>Project Guide</div>
    <div style="text-align: right;"><strong>{FRONT_MATTER['hod']}</strong><br>HoD</div>
  </div>
  <div class="sign-grid" style="margin-top: 30px;">
    <div><strong>Dean-Academics</strong></div>
    <div style="text-align: right;"><strong>Principal</strong></div>
  </div>
  <div class="ext-viva">
    <div style="text-align: center; font-weight: bold; font-size: 12pt; margin-bottom: 12px;">External Viva:</div>
    <table style="width: 100%; font-size: 11pt;">
      <tr><td style="width: 50%;"><strong>Examiner's Name</strong></td><td style="width: 50%; text-align: right;"><strong>Signature with Date</strong></td></tr>
      <tr><td style="padding-top: 15px;">1. ....................................................</td><td style="padding-top: 15px; text-align: right;">....................................................</td></tr>
      <tr><td style="padding-top: 15px;">2. ....................................................</td><td style="padding-top: 15px; text-align: right;">....................................................</td></tr>
    </table>
  </div>
</div>
""")

    # PAGE 3: DECLARATION
    html.append(f"""
<div class="page">
  <div class="cert-header">
    <div style="font-size: 14pt; font-weight: bold;">{FRONT_MATTER['college']}</div>
    <p>{FRONT_MATTER['college_sub']}</p>
    <p style="font-weight: bold;">{FRONT_MATTER['address']}</p>
    <div style="font-size: 12pt; font-weight: bold; margin-top: 10px;">DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</div>
    <img src="images/logo_2.jpeg" style="width: 70px; height: auto; margin: 15px auto;" alt="Canara Emblem" />
  </div>
  <div class="cert-title">DECLARATION</div>
  <p>We hereby declare that our entire work embodied in this Project Report titled <strong>“{FRONT_MATTER['title']}”</strong> has been carried out at CANARA ENGINEERING COLLEGE, Mangaluru under the supervision of <strong>{FRONT_MATTER['guide']}</strong>, for the award of <strong>Bachelor of Engineering in Computer Science &amp; Engineering</strong>. This report has not been submitted to this or any other University for the award of any other degree.</p>
  <table style="width: 70%; margin: 40px auto 0 auto; font-size: 11pt;">
    <tr><td><strong>{FRONT_MATTER['students'][0][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][0][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][1][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][1][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][2][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][2][1]}</strong></td></tr>
    <tr><td><strong>{FRONT_MATTER['students'][3][0]}</strong></td><td style="text-align:right;"><strong>{FRONT_MATTER['students'][3][1]}</strong></td></tr>
  </table>
</div>
""")

    # PAGE 4: ACKNOWLEDGEMENT
    html.append(f"""
<div class="page">
  <h1 class="prelim-title">Acknowledgement</h1>
  <p>We dedicate this page to acknowledge and thank those responsible for the shaping of the project. Without their guidance and help, the experience while constructing the dissertation would not have been so smooth and efficient.</p>
  <p>We sincerely thank our Project guide <strong>{FRONT_MATTER['guide']}</strong>, Professor, Dean R&amp;D, Computer Science &amp; Engineering for his/her guidance and valuable suggestions which helped us to complete this project.</p>
  <p>We also thank our Project coordinators <strong>{FRONT_MATTER['coordinator']}</strong>, Dept of Computer Science &amp; Engineering, for their constant encouragement.</p>
  <p>We owe a profound gratitude to <strong>{FRONT_MATTER['hod']}</strong>, Head of the Department, Computer Science &amp; Engineering, whose kind support and guidance helped us to complete this work successfully. We also take this opportunity to thank our Dean Academics <strong>{FRONT_MATTER['dean']}</strong> and We are extremely thankful to our Principal, for their support and encouragement.</p>
  <p>We would like to thank all faculty and staff of the Department of Computer Science &amp; Engineering who have always been with us extending their support, precious suggestions, guidance, and encouragement through the project. We also express our gratitude to our beloved friends and parents for their constant encouragement and support.</p>
  <div style="margin-top: 40px; line-height: 1.8;">
    <strong>{FRONT_MATTER['students'][0][0]}</strong><br>
    <strong>{FRONT_MATTER['students'][1][0]}</strong><br>
    <strong>{FRONT_MATTER['students'][2][0]}</strong><br>
    <strong>{FRONT_MATTER['students'][3][0]}</strong>
  </div>
  <div style="text-align: center; margin-top: 50px; font-size: 11pt;">i</div>
</div>
""")

    # PAGE 5: ABSTRACT
    html.append(f"""
<div class="page">
  <h1 class="prelim-title">Abstract</h1>
  <p>{p_split(ABSTRACT_TEXT)[0]}</p>
  <p>{p_split(ABSTRACT_TEXT)[1]}</p>
  <p>{p_split(ABSTRACT_TEXT)[2]}</p>
  <p class="no-indent" style="margin-top: 25px;"><strong>Keywords :</strong> {KEYWORDS_TEXT}</p>
  <div style="text-align: center; margin-top: 60px; font-size: 11pt;">ii</div>
</div>
""")

    # PAGE 6-12: TABLE OF CONTENTS
    html.append("""
<div class="page">
  <h1 class="prelim-title">Table of Contents</h1>
  <div class="toc-line"><strong>Acknowledgement</strong><span class="dots-leader"></span><span class="pnum">i</span></div>
  <div class="toc-line"><strong>Abstract</strong><span class="dots-leader"></span><span class="pnum">ii</span></div>
  <div class="toc-line"><strong>Table of Contents</strong><span class="dots-leader"></span><span class="pnum">iii</span></div>
  <div class="toc-line"><strong>List of Figures</strong><span class="dots-leader"></span><span class="pnum">x</span></div>
  <div class="toc-line"><strong>List of Tables</strong><span class="dots-leader"></span><span class="pnum">xi</span></div>
  
  <div class="toc-line" style="margin-top: 15px;"><strong>1 &nbsp; Introduction</strong><span class="dots-leader"></span><span class="pnum">1</span></div>
  <div class="toc-line toc-section">1.1 &nbsp; Background<span class="dots-leader"></span><span class="pnum">1</span></div>
  <div class="toc-line toc-section">1.2 &nbsp; Motivation and Problem statement<span class="dots-leader"></span><span class="pnum">2</span></div>
  <div class="toc-line toc-section">1.3 &nbsp; Objectives<span class="dots-leader"></span><span class="pnum">2</span></div>
  <div class="toc-line toc-section">1.4 &nbsp; Scope and limitations<span class="dots-leader"></span><span class="pnum">3</span></div>
  <div class="toc-line toc-section">1.5 &nbsp; Relevance and Type<span class="dots-leader"></span><span class="pnum">4</span></div>
  <div class="toc-line toc-section">1.6 &nbsp; Organization of the report<span class="dots-leader"></span><span class="pnum">4</span></div>
  
  <div class="toc-line" style="margin-top: 15px;"><strong>2 &nbsp; Literature Survey</strong><span class="dots-leader"></span><span class="pnum">6</span></div>
  <div class="toc-line toc-section">2.1 &nbsp; Bidirectional Indian Sign Language Converter [12]<span class="dots-leader"></span><span class="pnum">6</span></div>
  <div class="toc-line toc-section">2.2 &nbsp; Enhanced Sign Language Translation between ASL and ISL Using LLMs [7]<span class="dots-leader"></span><span class="pnum">7</span></div>
  <div class="toc-line toc-section">2.3 &nbsp; A Continuous Indian Sign Language Production System from Isolated Signs [10]<span class="dots-leader"></span><span class="pnum">8</span></div>
  <div class="toc-line toc-section">2.4 &nbsp; Towards real-time recognition of continuous ISL: RGB and pose [4]<span class="dots-leader"></span><span class="pnum">9</span></div>
  <div class="toc-line toc-section">2.5 &nbsp; Sanket Bhasha: Multilingual NLP and 3D Avatar-Based ISL Translator [3]<span class="dots-leader"></span><span class="pnum">10</span></div>
  <div class="toc-line toc-section">2.6 &nbsp; A Unified Vision System for Multilingual Gesture Recognition: ASL and ISL [19]<span class="dots-leader"></span><span class="pnum">11</span></div>
  <div class="toc-line toc-section">2.7 &nbsp; An effective skeleton-based approach for multilingual sign language [15]<span class="dots-leader"></span><span class="pnum">12</span></div>
  <div class="toc-line toc-section">2.8 &nbsp; Word recognition from ISL using dual feature and GMT-MASKRCNN [2]<span class="dots-leader"></span><span class="pnum">12</span></div>
  <div class="toc-line toc-section">2.9 &nbsp; AI-Assisted Real-Time Multilingual Sign Language Using 3D Avatars [14]<span class="dots-leader"></span><span class="pnum">13</span></div>
  <div class="toc-line toc-section">2.10 A multi-lingual sign language recognition system using machine learning [9]<span class="dots-leader"></span><span class="pnum">14</span></div>
  <div class="toc-line toc-section">2.11 A Transformer-Based Framework for Real Time ISL and Multilingual Translation [11]<span class="dots-leader"></span><span class="pnum">15</span></div>
  <div class="toc-line toc-section">2.12 Harnessing Vision Transformers for ISL Sentence Recognition From Videos [6]<span class="dots-leader"></span><span class="pnum">16</span></div>
  <div class="toc-line toc-section">2.13 Indian Sign Language Recognition using Neural Networks [1]<span class="dots-leader"></span><span class="pnum">18</span></div>
  <div class="toc-line toc-section">2.14 Fingerspelling for Indian Sign Language Using Swin Transformer [20]<span class="dots-leader"></span><span class="pnum">18</span></div>
  <div class="toc-line toc-section">2.15 Accurate Gesture Recognition in ISL Using Deep Learning [8]<span class="dots-leader"></span><span class="pnum">19</span></div>
  <div class="toc-line toc-section">2.16 NLP Based Gesture Translation Recognition for Inclusive Communication [5]<span class="dots-leader"></span><span class="pnum">20</span></div>
  <div class="toc-line toc-section">2.17 Multimodal AI for Audio/Video ISL Conversion Using Federated Learning [16]<span class="dots-leader"></span><span class="pnum">21</span></div>
  <div class="toc-line toc-section">2.18 Indian Sign Language Recognition and Translation: Encoder-Decoder [17]<span class="dots-leader"></span><span class="pnum">23</span></div>
  <div class="toc-line toc-section">2.19 Indian Sign Language Detection for Real-Time Translation Using ML [18]<span class="dots-leader"></span><span class="pnum">24</span></div>
  <div class="toc-line toc-section">2.20 Smart Computing: Sign Language Translation for Educational Accessibility [13]<span class="dots-leader"></span><span class="pnum">25</span></div>
  <div class="toc-line toc-section">2.21 Comparison Table<span class="dots-leader"></span><span class="pnum">26</span></div>
  <div class="toc-line toc-section">2.22 Summary<span class="dots-leader"></span><span class="pnum">31</span></div>

  <div class="toc-line" style="margin-top: 15px;"><strong>3 &nbsp; Software Requirements Specification</strong><span class="dots-leader"></span><span class="pnum">32</span></div>
  <div class="toc-line toc-section">3.1 &nbsp; Functional requirements<span class="dots-leader"></span><span class="pnum">32</span></div>
  <div class="toc-line toc-section">3.2 &nbsp; Non-Functional requirements<span class="dots-leader"></span><span class="pnum">33</span></div>
  <div class="toc-line toc-section">3.3 &nbsp; User interface design<span class="dots-leader"></span><span class="pnum">34</span></div>
  <div class="toc-line toc-section">3.4 &nbsp; Hardware and Software requirements<span class="dots-leader"></span><span class="pnum">34</span></div>
  <div class="toc-line toc-section">3.5 &nbsp; Performance Requirements<span class="dots-leader"></span><span class="pnum">34</span></div>
  <div class="toc-line toc-section">3.6 &nbsp; Any Other Requirements<span class="dots-leader"></span><span class="pnum">34</span></div>
  <div class="toc-line toc-section">3.7 &nbsp; Summary<span class="dots-leader"></span><span class="pnum">34</span></div>

  <div class="toc-line" style="margin-top: 15px;"><strong>4 &nbsp; System Design</strong><span class="dots-leader"></span><span class="pnum">35</span></div>
  <div class="toc-line toc-section">4.1 &nbsp; Abstract Design<span class="dots-leader"></span><span class="pnum">35</span></div>
  <div class="toc-line toc-subsection">4.1.1 Architectural diagram<span class="dots-leader"></span><span class="pnum">35</span></div>
  <div class="toc-line toc-section">4.2 &nbsp; Proposed system<span class="dots-leader"></span><span class="pnum">36</span></div>
  <div class="toc-line toc-section">4.3 &nbsp; Functional Design<span class="dots-leader"></span><span class="pnum">37</span></div>
  <div class="toc-line toc-subsection">4.3.1 Modular design diagram<span class="dots-leader"></span><span class="pnum">37</span></div>
  <div class="toc-line toc-subsection">4.3.2 Sequence diagram<span class="dots-leader"></span><span class="pnum">38</span></div>
  <div class="toc-line toc-subsection">4.3.3 Use case diagram<span class="dots-leader"></span><span class="pnum">39</span></div>
  <div class="toc-line toc-section">4.4 &nbsp; Control Flow Design<span class="dots-leader"></span><span class="pnum">40</span></div>
  <div class="toc-line toc-subsection">4.4.1 Activity diagram for use cases<span class="dots-leader"></span><span class="pnum">40</span></div>
  <div class="toc-line toc-section">4.5 &nbsp; Data Flow Diagram<span class="dots-leader"></span><span class="pnum">41</span></div>
  <div class="toc-line toc-subsection">4.5.1 Zero-Level Data Flow Diagram<span class="dots-leader"></span><span class="pnum">41</span></div>
  <div class="toc-line toc-subsection">4.5.2 First-Level Data Flow Diagram<span class="dots-leader"></span><span class="pnum">42</span></div>
  <div class="toc-line toc-subsection">4.5.3 Second-Level Data Flow Diagram<span class="dots-leader"></span><span class="pnum">43</span></div>
  <div class="toc-line toc-subsection">4.5.4 Additional Design, Simulation and Optimization Steps<span class="dots-leader"></span><span class="pnum">43</span></div>
  <div class="toc-line toc-subsection">4.5.5 Summary<span class="dots-leader"></span><span class="pnum">43</span></div>

  <div class="toc-line" style="margin-top: 15px;"><strong>5 &nbsp; Implementation</strong><span class="dots-leader"></span><span class="pnum">44</span></div>
  <div class="toc-line toc-section">5.1 &nbsp; Software used with justification<span class="dots-leader"></span><span class="pnum">44</span></div>
  <div class="toc-line toc-section">5.2 &nbsp; Hardware Used with justification<span class="dots-leader"></span><span class="pnum">44</span></div>
  <div class="toc-line toc-section">5.3 &nbsp; Algorithm/procedures used in different modules<span class="dots-leader"></span><span class="pnum">45</span></div>
  <div class="toc-line toc-section">5.4 &nbsp; Coding/pseudocodes<span class="dots-leader"></span><span class="pnum">45</span></div>
  <div class="toc-line toc-section">5.5 &nbsp; Summary<span class="dots-leader"></span><span class="pnum">46</span></div>

  <div class="toc-line" style="margin-top: 15px;"><strong>6 &nbsp; Results and Discussion</strong><span class="dots-leader"></span><span class="pnum">47</span></div>
  <div class="toc-line toc-section">6.1 &nbsp; Results<span class="dots-leader"></span><span class="pnum">47</span></div>
  <div class="toc-line toc-section">6.2 &nbsp; TESTING<span class="dots-leader"></span><span class="pnum">48</span></div>
  <div class="toc-line toc-section">6.3 &nbsp; TYPES OF SOFTWARE TESTING<span class="dots-leader"></span><span class="pnum">48</span></div>
  <div class="toc-line toc-section">6.4 &nbsp; TESTING METHODOLOGY<span class="dots-leader"></span><span class="pnum">48</span></div>
  <div class="toc-line toc-section">6.5 &nbsp; TESTING CRITERIA<span class="dots-leader"></span><span class="pnum">49</span></div>
  <div class="toc-line toc-section">6.6 &nbsp; Comparative Analysis<span class="dots-leader"></span><span class="pnum">51</span></div>
  <div class="toc-line toc-section">6.7 &nbsp; Summary<span class="dots-leader"></span><span class="pnum">51</span></div>

  <div class="toc-line" style="margin-top: 15px;"><strong>7 &nbsp; Conclusions and Future work</strong><span class="dots-leader"></span><span class="pnum">52</span></div>
  <div class="toc-line"><strong>References</strong><span class="dots-leader"></span><span class="pnum">53</span></div>
  <div class="toc-line"><strong>A &nbsp; Drill-bit/Turnitin Plagiarism Report</strong><span class="dots-leader"></span><span class="pnum">56</span></div>
  <div class="toc-line"><strong>B &nbsp; Patent/Publication and Project-Expo Details</strong><span class="dots-leader"></span><span class="pnum">57</span></div>

  <div style="text-align: center; margin-top: 30px; font-size: 11pt;">iii</div>
</div>
""")

    # LIST OF FIGURES
    html.append("""
<div class="page">
  <h1 class="prelim-title">List of Figures</h1>
  <div class="toc-line"><span>4.1 &nbsp; System Architecture Diagram</span><span class="dots-leader"></span><span class="pnum">35</span></div>
  <div class="toc-line"><span>4.2 &nbsp; Proposed System</span><span class="dots-leader"></span><span class="pnum">36</span></div>
  <div class="toc-line"><span>4.3 &nbsp; Modular design diagram</span><span class="dots-leader"></span><span class="pnum">37</span></div>
  <div class="toc-line"><span>4.4 &nbsp; Sequence diagram</span><span class="dots-leader"></span><span class="pnum">38</span></div>
  <div class="toc-line"><span>4.5 &nbsp; Use case diagram</span><span class="dots-leader"></span><span class="pnum">39</span></div>
  <div class="toc-line"><span>4.6 &nbsp; Sample Activity diagram</span><span class="dots-leader"></span><span class="pnum">40</span></div>
  <div class="toc-line"><span>4.7 &nbsp; Zero-Level Data Flow Diagram</span><span class="dots-leader"></span><span class="pnum">41</span></div>
  <div class="toc-line"><span>4.8 &nbsp; First-Level Data Flow Diagram</span><span class="dots-leader"></span><span class="pnum">42</span></div>
  <div class="toc-line"><span>4.9 &nbsp; Second-Level Data Flow Diagram</span><span class="dots-leader"></span><span class="pnum">43</span></div>
  <div class="toc-line"><span>6.1 &nbsp; Sample Result-1 (ISL Translation Studio Interface)</span><span class="dots-leader"></span><span class="pnum">47</span></div>
  <div class="toc-line"><span>6.2 &nbsp; Sample Result-2 (Recognition & Multilingual Outcome)</span><span class="dots-leader"></span><span class="pnum">47</span></div>
  <div style="text-align: center; margin-top: 60px; font-size: 11pt;">x</div>
</div>
""")

    # LIST OF TABLES
    html.append("""
<div class="page">
  <h1 class="prelim-title">List of Tables</h1>
  <div class="toc-line"><span>2.1 &nbsp; Comparison of Existing Work and Gap Identification</span><span class="dots-leader"></span><span class="pnum">26</span></div>
  <div class="toc-line"><span>2.2 &nbsp; Comparison of Existing Work and Gap Identification</span><span class="dots-leader"></span><span class="pnum">27</span></div>
  <div class="toc-line"><span>2.3 &nbsp; Comparison of Existing Work and Gap Identification</span><span class="dots-leader"></span><span class="pnum">28</span></div>
  <div class="toc-line"><span>2.4 &nbsp; Comparison of Existing Work and Gap Identification</span><span class="dots-leader"></span><span class="pnum">29</span></div>
  <div class="toc-line"><span>2.5 &nbsp; Comparison of Existing Work and Gap Identification</span><span class="dots-leader"></span><span class="pnum">30</span></div>
  <div class="toc-line"><span>6.1 &nbsp; Testing Criteria for Video Stream Acquisition and Signer Detection</span><span class="dots-leader"></span><span class="pnum">50</span></div>
  <div class="toc-line"><span>6.2 &nbsp; Testing Criteria for Static Gesture Recognition and Confidence Filtering</span><span class="dots-leader"></span><span class="pnum">50</span></div>
  <div class="toc-line"><span>6.3 &nbsp; Testing Criteria for Dynamic Gesture Sequence Buffer and Temporal Debouncing</span><span class="dots-leader"></span><span class="pnum">50</span></div>
  <div class="toc-line"><span>6.4 &nbsp; Testing Criteria for NLP Sentence Synthesis and Grammar Restructuring</span><span class="dots-leader"></span><span class="pnum">51</span></div>
  <div class="toc-line"><span>6.5 &nbsp; Testing Criteria for Multilingual Translation API & Regional Speech Synthesis</span><span class="dots-leader"></span><span class="pnum">51</span></div>
  <div class="toc-line"><span>6.6 &nbsp; Comparative Analysis of Proposed System with Existing Literature Methods</span><span class="dots-leader"></span><span class="pnum">51</span></div>
  <div style="text-align: center; margin-top: 60px; font-size: 11pt;">xi</div>
</div>
""")

    # CHAPTER 1: INTRODUCTION
    html.append(f"""
<div class="page">
  {header_footer(1, 1)}
  <h1 class="chapter-title">Chapter 1<br><span style="font-size: 20pt;">Introduction</span></h1>
  <h2>1.1 Background</h2>
  <p>{p_split(CH1_CONTENT['background'])[0]}</p>
  <p>{p_split(CH1_CONTENT['background'])[1]}</p>
  <p>{p_split(CH1_CONTENT['background'])[2]}</p>
</div>

<div class="page">
  {header_footer(1, 2)}
  <h2>1.2 Motivation and Problem statement</h2>
  <p>{p_split(CH1_CONTENT['motivation'])[0]}</p>
  <p>{p_split(CH1_CONTENT['motivation'])[1]}</p>
  <h2>1.3 Objectives</h2>
  <ul>
    <li><strong>{CH1_CONTENT['objectives'][0][0]}:</strong> {CH1_CONTENT['objectives'][0][1]}</li>
    <li><strong>{CH1_CONTENT['objectives'][1][0]}:</strong> {CH1_CONTENT['objectives'][1][1]}</li>
    <li><strong>{CH1_CONTENT['objectives'][2][0]}:</strong> {CH1_CONTENT['objectives'][2][1]}</li>
    <li><strong>{CH1_CONTENT['objectives'][3][0]}:</strong> {CH1_CONTENT['objectives'][3][1]}</li>
    <li><strong>{CH1_CONTENT['objectives'][4][0]}:</strong> {CH1_CONTENT['objectives'][4][1]}</li>
  </ul>
</div>

<div class="page">
  {header_footer(1, 3)}
  <h2>1.4 Scope and limitations</h2>
  <p>{p_split(CH1_CONTENT['scope_limitations'])[0]}</p>
  <p>{p_split(CH1_CONTENT['scope_limitations'])[1]}</p>
</div>

<div class="page">
  {header_footer(1, 4)}
  <h2>1.5 Relevance and Type</h2>
  <p>{p_split(CH1_CONTENT['relevance_type'])[0]}</p>
  <p>{p_split(CH1_CONTENT['relevance_type'])[1]}</p>
  <p><strong>Relevance &amp; Category:</strong> This project can be categorized as both an <strong>Application-Oriented &amp; Research-Oriented</strong> project, as it involves developing a practical real-time system while also exploring different machine learning techniques and methods for improving gesture recognition and translation accuracy.</p>
  <h2>1.6 Organization of the report</h2>
  <p>{p_split(CH1_CONTENT['organization'])[0]}</p>
</div>
""")

    # CHAPTER 2: LITERATURE SURVEY
    html.append(f"""
<div class="page">
  {header_footer(2, 6)}
  <h1 class="chapter-title">Chapter 2<br><span style="font-size: 20pt;">Literature Survey</span></h1>
""")

    pnum = 6
    for idx, art in enumerate(LITERATURE_ARTICLES):
        # We put 1-2 articles per page
        if idx > 0 and idx % 1 == 0:
            pnum += 1
            html.append(f"""
</div>
<div class="page">
  {header_footer(2, pnum)}
""")
        html.append(f"""
  <h2>{art['num']} {art['title']}</h2>
  <p>{art['intro']}</p>
  <h3>{art['num']}.1 Brief Findings of Article {idx+1}</h3>
  <p>{art['findings']}</p>
  <h3>{art['num']}.2 Design/Methodology/Techniques Adopted in Article {idx+1}</h3>
  <p>{art['methodology']}</p>
  <h3>{art['num']}.3 Results Achieved in Article {idx+1}</h3>
  <p>{art['results']}</p>
""")

    html.append("</div>") # close last article page

    # COMPARISON TABLES (2.1 to 2.5)
    for table_idx, t in enumerate(COMPARISON_TABLES):
        pnum += 1
        html.append(f"""
<div class="page">
  {header_footer(2, pnum)}
  <h2>2.21 Comparision Table</h2>
  <div style="font-size: 11pt; font-weight: bold; margin-bottom: 8px;">Table {t['table_num']}: {t['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr>
        <th style="width: 25%;">Project Title and Author</th>
        <th style="width: 25%;">Problem Addressed</th>
        <th style="width: 25%;">Implementation and Results</th>
        <th style="width: 25%;">Limitations/ Future Scope</th>
      </tr>
    </thead>
    <tbody>
""")
        for r in t['rows']:
            html.append(f"""
      <tr>
        <td><strong>{r[0]}</strong></td>
        <td>{r[1]}</td>
        <td>{r[2]}</td>
        <td>{r[3]}</td>
      </tr>
""")
        html.append(f"""
    </tbody>
  </table>
</div>
""")

    # CHAPTER 2 SUMMARY
    pnum += 1
    html.append(f"""
<div class="page">
  {header_footer(2, pnum)}
  <h2>2.22 Summary</h2>
  <p>{p_split(SUMMARY_CH2)[0]}</p>
  <p>{p_split(SUMMARY_CH2)[1]}</p>
</div>
""")

    # CHAPTER 3: SRS
    html.append(f"""
<div class="page">
  {header_footer(3, 32)}
  <h1 class="chapter-title">Chapter 3<br><span style="font-size: 20pt;">Software Requirements Specification</span></h1>
  <h2>3.1 Functional requirements</h2>
  <p>Functional requirements define the expected behavior and core functionalities of the proposed Indian Sign Language (ISL) recognition and translation system. The application should accurately recognize gestures, process them in real time, and generate meaningful outputs for effective communication. The major functional requirements are:</p>
""")
    for req in CH3_CONTENT['functional'][:4]:
        html.append(f"""
  <h3>{req[0]}</h3>
  <p class="no-indent">{req[1]}</p>
""")
    html.append(f"""
</div>
<div class="page">
  {header_footer(3, 33)}
""")
    for req in CH3_CONTENT['functional'][4:]:
        html.append(f"""
  <h3>{req[0]}</h3>
  <p class="no-indent">{req[1]}</p>
""")
    html.append(f"""
  <h2>3.2 Non-Functional requirements</h2>
  <p>The proposed system must operate smoothly, providing real-time results with minimal delay on commonly available devices without requiring expensive hardware.</p>
  <h3>3.2.1 Safety Requirements</h3>
  <p class="no-indent">{CH3_CONTENT['non_functional'][0][1]}</p>
  <h3>3.2.2 Performance Requirements</h3>
  <p class="no-indent">{CH3_CONTENT['non_functional'][1][1]}</p>
</div>
<div class="page">
  {header_footer(3, 34)}
  <h2>3.3 User interface design</h2>
  <p>{p_split(CH3_CONTENT['ui_design'])[0]}</p>
  <p>{p_split(CH3_CONTENT['ui_design'])[1]}</p>
  <h2>3.4 Hardware and Software requirements</h2>
  <p><strong>Hardware Requirements:</strong></p>
  <ul>
""")
    for h in CH3_CONTENT['hw_sw_requirements']['hardware']:
        html.append(f"<li>{h}</li>")
    html.append("""
  </ul>
  <p><strong>Software Requirements:</strong></p>
  <ul>
""")
    for s in CH3_CONTENT['hw_sw_requirements']['software']:
        html.append(f"<li>{s}</li>")
    html.append("""
  </ul>
  <h2>3.5 Performance Requirements</h2>
  <p>The application should process gestures in real time with good accuracy and low latency (< 35 ms). It should remain reliable during long periods of operation and handle multiple gesture inputs smoothly.</p>
  <h2>3.6 Any Other Requirements</h2>
  <p>The system should be scalable and flexible enough to support future enhancements such as additional ISL gestures, continuous sentence recognition, and support for more regional languages.</p>
  <h2>3.7 Summary</h2>
  <p>This chapter discussed the Software Requirements Specification of the proposed Indian Sign Language recognition and translation system, establishing a solid foundation for the architectural design.</p>
</div>
""")

    # CHAPTER 4: SYSTEM DESIGN
    html.append(f"""
<div class="page">
  {header_footer(4, 35)}
  <h1 class="chapter-title">Chapter 4<br><span style="font-size: 20pt;">System Design</span></h1>
  <h2>4.1 Abstract Design</h2>
  <h3>4.1.1 Architectural diagram</h3>
  <p>{CH4_CONTENT['arch_intro']}</p>
  <div class="figure-container">
    <img src="images/fig_4_1_architecture.jpg" alt="Figure 4.1: System Architecture Diagram" />
    <div class="figure-caption"><strong>Figure 4.1: System Architecture Diagram</strong></div>
  </div>
  <p><strong>Explanation of Architectural diagram:</strong></p>
  <p>{p_split(CH4_CONTENT['arch_explanation'])[0]}</p>
</div>

<div class="page">
  {header_footer(4, 36)}
  <h2>4.2 Proposed system</h2>
  <div class="figure-container">
    <img src="images/fig_4_2_flowchart.jpg" alt="Figure 4.2: Proposed System Flowchart" />
    <div class="figure-caption"><strong>Figure 4.2: Proposed System</strong></div>
  </div>
  <p><strong>Explanation of Proposed System:</strong></p>
  <p>{CH4_CONTENT['flowchart_explanation']}</p>
</div>

<div class="page">
  {header_footer(4, 37)}
  <h2>4.3 Functional Design</h2>
  <h3>4.3.1 Modular design diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_3_modular.jpg" alt="Figure 4.3: Modular Design Diagram" />
    <div class="figure-caption"><strong>Figure 4.3: Modular design diagram</strong></div>
  </div>
  <p><strong>Explanation of Modular design diagram:</strong></p>
  <p>{CH4_CONTENT['modular_explanation']}</p>
</div>

<div class="page">
  {header_footer(4, 38)}
  <h3>4.3.2 Sequence diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_4_sequence.jpg" alt="Figure 4.4: Sequence Diagram" />
    <div class="figure-caption"><strong>Figure 4.4: Sequence diagram</strong></div>
  </div>
  <p><strong>Explanation of Sequence diagram:</strong></p>
  <p>{CH4_CONTENT['sequence_explanation']}</p>
</div>

<div class="page">
  {header_footer(4, 39)}
  <h3>4.3.3 Use case diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_5_usecase.jpg" alt="Figure 4.5: Use Case Diagram" />
    <div class="figure-caption"><strong>Figure 4.5: Use case diagram</strong></div>
  </div>
  <p><strong>Explanation of Use case diagram:</strong></p>
  <p>{CH4_CONTENT['usecase_explanation']}</p>
</div>

<div class="page">
  {header_footer(4, 40)}
  <h2>4.4 Control Flow Design</h2>
  <h3>4.4.1 Activity diagram for use cases</h3>
  <div class="figure-container">
    <img src="images/fig_4_6_activity.jpg" alt="Figure 4.6: Sample Activity Diagram" />
    <div class="figure-caption"><strong>Figure 4.6: Sample Activity diagram</strong></div>
  </div>
  <p><strong>Explanation of Activity diagram:</strong></p>
  <p>{CH4_CONTENT['activity_explanation']}</p>
</div>

<div class="page">
  {header_footer(4, 41)}
  <h2>4.5 Data Flow Diagram</h2>
  <h3>4.5.1 Zero-Level Data Flow Diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_7_dfd0.jpg" alt="Figure 4.7: Zero-Level Data Flow Diagram" />
    <div class="figure-caption"><strong>Figure 4.7: Zero-Level Data Flow Diagram</strong></div>
  </div>
  <p><strong>Explanation of Zero-Level Data Flow diagram:</strong></p>
  <p>{CH4_CONTENT['dfd_explanations']['dfd0']}</p>
</div>

<div class="page">
  {header_footer(4, 42)}
  <h3>4.5.2 First-Level Data Flow Diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_8_dfd1.jpg" alt="Figure 4.8: First-Level Data Flow Diagram" />
    <div class="figure-caption"><strong>Figure 4.8: First-Level Data Flow Diagram</strong></div>
  </div>
  <p><strong>Explanation of First-Level Data Flow diagram:</strong></p>
  <p>{CH4_CONTENT['dfd_explanations']['dfd1']}</p>
</div>

<div class="page">
  {header_footer(4, 43)}
  <h3>4.5.3 Second-Level Data Flow Diagram</h3>
  <div class="figure-container">
    <img src="images/fig_4_9_dfd2.jpg" alt="Figure 4.9: Second-Level Data Flow Diagram" />
    <div class="figure-caption"><strong>Figure 4.9: Second-Level Data Flow Diagram</strong></div>
  </div>
  <p><strong>Explanation of Second-Level Data Flow diagram:</strong></p>
  <p>{CH4_CONTENT['dfd_explanations']['dfd2']}</p>
  <h3>4.5.4 Any other Design/Simulation/Optimization steps</h3>
  <p>{CH4_CONTENT['optimization_steps']}</p>
  <h3>4.5.5 Summary</h3>
  <p>{CH4_CONTENT['summary']}</p>
</div>
""")

    # CHAPTER 5: IMPLEMENTATION
    html.append(f"""
<div class="page">
  {header_footer(5, 44)}
  <h1 class="chapter-title">Chapter 5<br><span style="font-size: 20pt;">Implementation</span></h1>
  <h2>5.1 Software used with justification</h2>
  <h3>5.1.1 Frontend Development:</h3>
  <p class="no-indent">{CH5_CONTENT['software_justification']['frontend']}</p>
  <h3>5.1.2 Backend Development:</h3>
  <p class="no-indent">{CH5_CONTENT['software_justification']['backend']}</p>
  <h3>5.1.3 Framework Used:</h3>
  <p class="no-indent">{CH5_CONTENT['software_justification']['frameworks']}</p>
  <h3>5.1.4 Coding Languages used for Development :</h3>
  <ul>
    <li><strong>Coding Language 1: {CH5_CONTENT['software_justification']['languages'][0][0]}:</strong><br>{CH5_CONTENT['software_justification']['languages'][0][1]}</li>
    <li><strong>Coding Language 2: {CH5_CONTENT['software_justification']['languages'][1][0]}:</strong><br>{CH5_CONTENT['software_justification']['languages'][1][1]}</li>
    <li><strong>Coding Language 3: {CH5_CONTENT['software_justification']['languages'][2][0]}:</strong><br>{CH5_CONTENT['software_justification']['languages'][2][1]}</li>
  </ul>
  <h3>5.1.5 Operating System:</h3>
  <p class="no-indent">{CH5_CONTENT['software_justification']['os']}</p>
  <h2>5.2 Hardware Used with justification</h2>
  <p>{CH5_CONTENT['hardware_justification']}</p>
</div>

<div class="page">
  {header_footer(5, 45)}
  <h2>5.3 Algorithm/procedures used in the project in different modules</h2>
""")
    for algo in CH5_CONTENT['algorithms']:
        html.append(f"""
  <h3>{algo[0]}</h3>
  <p class="no-indent">{algo[1]}</p>
""")
    html.append(f"""
  <h2>5.4 Coding/pseudocodes</h2>
  <h3>5.4.1 Introduction</h3>
  <p>The goal of coding or programming phase is to translate the design of the system produced during the design phase into code in a given programming language, which can be executed by a computer and that performs the computation specified by the design. Readability, maintainability, and execution efficiency are paramount.</p>
  <h3>5.4.2 Programming Style</h3>
  <p>To produce maintainable and scalable code, the following programming style guidelines were rigorously maintained across the project:</p>
  <ul>
    <li><strong>{CH5_CONTENT['programming_style']['names'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['names'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['control_constructs'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['control_constructs'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['info_hiding'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['info_hiding'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['user_types'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['user_types'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['nesting'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['nesting'].split(':')[1]}</li>
  </ul>
</div>

<div class="page">
  {header_footer(5, 46)}
  <ul>
    <li><strong>{CH5_CONTENT['programming_style']['module_size'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['module_size'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['module_interface'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['module_interface'].split(':')[1]}</li>
    <li><strong>{CH5_CONTENT['programming_style']['program_layout'].split(':')[0]}:</strong> {CH5_CONTENT['programming_style']['program_layout'].split(':')[1]}</li>
  </ul>
  <h3>Pseudocode Specifications:</h3>
  <div style="font-weight: bold; margin-top: 10px;">{CH5_CONTENT['pseudocodes'][0][0]}</div>
  <pre class="code-block">{CH5_CONTENT['pseudocodes'][0][1]}</pre>
  <div style="font-weight: bold; margin-top: 10px;">{CH5_CONTENT['pseudocodes'][1][0]}</div>
  <pre class="code-block">{CH5_CONTENT['pseudocodes'][1][1]}</pre>
  <div style="font-weight: bold; margin-top: 10px;">{CH5_CONTENT['pseudocodes'][2][0]}</div>
  <pre class="code-block">{CH5_CONTENT['pseudocodes'][2][1]}</pre>
  <h2>5.5 Summary</h2>
  <p>{CH5_CONTENT['summary']}</p>
</div>
""")

    # CHAPTER 6: RESULTS AND DISCUSSION
    html.append(f"""
<div class="page">
  {header_footer(6, 47)}
  <h1 class="chapter-title">Chapter 6<br><span style="font-size: 20pt;">Results and Discussion</span></h1>
  <h2>6.1 Results</h2>
  <p>{p_split(CH6_CONTENT['results_discussion'])[0]}</p>
  <div class="figure-container">
    <img src="images/fig_6_1_studio.png" alt="Figure 6.1: ISL Translation Studio Interface" style="max-height: 250px;" />
    <div class="figure-caption"><strong>Figure 6.1: Sample Result-1 (ISL Translation Studio Interface)</strong></div>
  </div>
  <div class="figure-container">
    <img src="images/fig_6_2_outcome.png" alt="Figure 6.2: Real-time Recognition & Multilingual Outcome" style="max-height: 250px;" />
    <div class="figure-caption"><strong>Figure 6.2: Sample Result-2 (Real-Time Recognition &amp; Multilingual Outcome)</strong></div>
  </div>
  <p>{p_split(CH6_CONTENT['results_discussion'])[1] if len(p_split(CH6_CONTENT['results_discussion'])) > 1 else ''}</p>
</div>

<div class="page">
  {header_footer(6, 48)}
  <h2>6.2 TESTING:</h2>
  <p>Software testing is the process used to help identify the correctness, completeness, security and quality of developed computer software. During testing, the program is executed with comprehensive test suites and results are evaluated against expected outcomes.</p>
  <h2>6.3 TYPES OF SOFTWARE TESTING:</h2>
  <ul>
    <li><strong>Black Box Testing:</strong> Internal system design is not considered. Tests evaluate functional inputs against outputs across web endpoints, camera capture, and translation buttons.</li>
    <li><strong>White Box Testing:</strong> Tests examine internal logic, path coverage, and mathematical boundary constraints across landmark normalization and confidence gating logic.</li>
  </ul>
  <h2>6.4 TESTING METHODOLOGY</h2>
  <p class="no-indent"><strong>{CH6_CONTENT['testing_methodology']['unit'].split(':')[0]}:</strong> {CH6_CONTENT['testing_methodology']['unit'].split(':')[1]}</p>
  <p class="no-indent"><strong>{CH6_CONTENT['testing_methodology']['integration'].split(':')[0]}:</strong> {CH6_CONTENT['testing_methodology']['integration'].split(':')[1]}</p>
</div>

<div class="page">
  {header_footer(6, 49)}
  <p class="no-indent"><strong>{CH6_CONTENT['testing_methodology']['system'].split(':')[0]}:</strong> {CH6_CONTENT['testing_methodology']['system'].split(':')[1]}</p>
  <p class="no-indent"><strong>{CH6_CONTENT['testing_methodology']['field'].split(':')[0]}:</strong> {CH6_CONTENT['testing_methodology']['field'].split(':')[1]}</p>
  <p class="no-indent"><strong>{CH6_CONTENT['testing_methodology']['acceptance'].split(':')[0]}:</strong> {CH6_CONTENT['testing_methodology']['acceptance'].split(':')[1]}</p>
  <h2>6.5 TESTING CRITERIA</h2>
  <p>Detailed verification criteria were established for every module of the ISL translation system:</p>
""")

    # TESTING TABLES (6.1, 6.2, 6.3 on page 50)
    html.append(f"""
  <div style="font-size: 10.5pt; font-weight: bold;">Table 6.1: {CH6_CONTENT['testing_tables'][0]['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr><th>Test Case</th><th>Input</th><th>Test Description</th><th>Expected Output</th><th>Status</th></tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['testing_tables'][0]['rows']:
        html.append(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><strong>{r[5]}</strong></td></tr>")
    html.append(f"""
    </tbody>
  </table>
</div>

<div class="page">
  {header_footer(6, 50)}
  <div style="font-size: 10.5pt; font-weight: bold;">Table 6.2: {CH6_CONTENT['testing_tables'][1]['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr><th>Test Case</th><th>Input</th><th>Test Description</th><th>Expected Output</th><th>Status</th></tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['testing_tables'][1]['rows']:
        html.append(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><strong>{r[5]}</strong></td></tr>")
    html.append(f"""
    </tbody>
  </table>

  <div style="font-size: 10.5pt; font-weight: bold; margin-top: 15px;">Table 6.3: {CH6_CONTENT['testing_tables'][2]['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr><th>Test Case</th><th>Input</th><th>Test Description</th><th>Expected Output</th><th>Status</th></tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['testing_tables'][2]['rows']:
        html.append(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><strong>{r[5]}</strong></td></tr>")
    html.append(f"""
    </tbody>
  </table>
</div>

<div class="page">
  {header_footer(6, 51)}
  <div style="font-size: 10.5pt; font-weight: bold;">Table 6.4: {CH6_CONTENT['testing_tables'][3]['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr><th>Test Case</th><th>Input</th><th>Test Description</th><th>Expected Output</th><th>Status</th></tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['testing_tables'][3]['rows']:
        html.append(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><strong>{r[5]}</strong></td></tr>")
    html.append(f"""
    </tbody>
  </table>

  <div style="font-size: 10.5pt; font-weight: bold; margin-top: 15px;">Table 6.5: {CH6_CONTENT['testing_tables'][4]['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr><th>Test Case</th><th>Input</th><th>Test Description</th><th>Expected Output</th><th>Status</th></tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['testing_tables'][4]['rows']:
        html.append(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><strong>{r[5]}</strong></td></tr>")
    html.append(f"""
    </tbody>
  </table>

  <h2>6.6 Comparative Analysis</h2>
  <div style="font-size: 10.5pt; font-weight: bold;">Table 6.6: {CH6_CONTENT['comparative_table']['caption']}</div>
  <table class="academic-table">
    <thead>
      <tr>
        <th>System / Author</th>
        <th>Architecture</th>
        <th>Features</th>
        <th>Static</th>
        <th>Dynamic</th>
        <th>Latency</th>
        <th>Multilingual</th>
      </tr>
    </thead>
    <tbody>
""")
    for r in CH6_CONTENT['comparative_table']['rows']:
        html.append(f"""
      <tr{' style="background-color: #f0f7ff; font-weight: bold;"' if 'Proposed' in r[0] else ''}>
        <td>{r[0]}</td>
        <td>{r[1]}</td>
        <td>{r[2]}</td>
        <td>{r[3]}</td>
        <td>{r[4]}</td>
        <td>{r[5]}</td>
        <td>{r[6]}</td>
      </tr>
""")
    html.append(f"""
    </tbody>
  </table>
  <h2>6.7 Summary</h2>
  <p>{CH6_CONTENT['summary']}</p>
</div>
""")

    # CHAPTER 7: CONCLUSIONS AND FUTURE WORK
    html.append(f"""
<div class="page">
  {header_footer(7, 52)}
  <h1 class="chapter-title">Chapter 7<br><span style="font-size: 20pt;">Conclusions and Future work</span></h1>
  <h2>7.1 Conclusions</h2>
  <p>{p_split(CH7_CONTENT['conclusions'])[0]}</p>
  <p>{p_split(CH7_CONTENT['conclusions'])[1]}</p>
  <h2>7.2 Future work</h2>
  <p>{p_split(CH7_CONTENT['future_work'])[0]}</p>
  <ol>
""")
    for fw in [
        "Vocabulary Expansion: Scaling dynamic sign coverage to over 1,000 signs covering advanced technical and legal lexicons.",
        "Bidirectional 3D Sign Avatar: Inverting translation to animate spoken regional audio into 3D avatar ISL gestures.",
        "Edge Device Quantization: Converting neural weights to 8-bit quantized TensorFlow Lite (TFLite) for offline smartphone deployment.",
        "Continuous Sign Recognition: Integrating CTC loss for end-to-end continuous sentence recognition without manual boundaries.",
        "Non-Manual Marker Analysis: Incorporating facial GCNs to track grammatical eyebrow and head movements."
    ]:
        html.append(f"<li>{fw}</li>")
    html.append("""
  </ol>
</div>
""")

    # REFERENCES
    html.append(f"""
<div class="page">
  <div class="running-header">
    <span>Indian Sign Language to Text with Native Language Translation.</span>
    <span>References</span>
  </div>
  <div class="running-footer">
    <span>Department of Computer Science &amp; Engineering, CEC, Benjanapadavu,Mangaluru</span>
    <span>Page 53</span>
  </div>
  <h1 class="prelim-title">References</h1>
""")
    for ref in REFERENCES[:7]:
        html.append(f'<p class="no-indent" style="margin-bottom: 12px; font-size: 10pt;">{ref}</p>')
    html.append(f"""
</div>
<div class="page">
  <div class="running-header">
    <span>Indian Sign Language to Text with Native Language Translation.</span>
    <span>References</span>
  </div>
  <div class="running-footer">
    <span>Department of Computer Science &amp; Engineering, CEC, Benjanapadavu,Mangaluru</span>
    <span>Page 54</span>
  </div>
""")
    for ref in REFERENCES[7:16]:
        html.append(f'<p class="no-indent" style="margin-bottom: 12px; font-size: 10pt;">{ref}</p>')
    html.append(f"""
</div>
<div class="page">
  <div class="running-header">
    <span>Indian Sign Language to Text with Native Language Translation.</span>
    <span>References</span>
  </div>
  <div class="running-footer">
    <span>Department of Computer Science &amp; Engineering, CEC, Benjanapadavu,Mangaluru</span>
    <span>Page 55</span>
  </div>
""")
    for ref in REFERENCES[16:]:
        html.append(f'<p class="no-indent" style="margin-bottom: 12px; font-size: 10pt;">{ref}</p>')
    html.append("</div>")

    # APPENDICES
    html.append(f"""
<div class="page">
  <div class="running-header">
    <span>Indian Sign Language to Text with Native Language Translation.</span>
    <span>Appendix A</span>
  </div>
  <div class="running-footer">
    <span>Department of Computer Science &amp; Engineering, CEC, Benjanapadavu,Mangaluru</span>
    <span>Page 56</span>
  </div>
  <h1 class="prelim-title">{APPENDICES_CONTENT['appendix_a']['title']}</h1>
  <p>{p_split(APPENDICES_CONTENT['appendix_a']['text'])[0]}</p>
  <pre class="code-block" style="font-size: 10pt; line-height: 1.5;">{p_split(APPENDICES_CONTENT['appendix_a']['text'])[1]}</pre>
</div>

<div class="page">
  <div class="running-header">
    <span>Indian Sign Language to Text with Native Language Translation.</span>
    <span>Appendix B</span>
  </div>
  <div class="running-footer">
    <span>Department of Computer Science &amp; Engineering, CEC, Benjanapadavu,Mangaluru</span>
    <span>Page 57</span>
  </div>
  <h1 class="prelim-title">{APPENDICES_CONTENT['appendix_b']['title']}</h1>
  <pre class="code-block" style="font-size: 10pt; line-height: 1.5;">{APPENDICES_CONTENT['appendix_b']['text']}</pre>
</div>
""")

    html.append("""
</body>
</html>
""")

    full_html = "".join(html)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Wrote full HTML report to: {HTML_PATH} ({len(full_html)} characters)")
    return HTML_PATH

def compile_pdf():
    print("Compiling PDF via Headless Chrome...")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        f"file:///{HTML_PATH.replace(os.sep, '/')}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Chrome output:", res.stdout, res.stderr)
    if os.path.exists(PDF_PATH):
        size = os.path.getsize(PDF_PATH)
        doc = pymupdf.open(PDF_PATH)
        print(f"SUCCESS: Generated {PDF_PATH} ({size:,} bytes, {len(doc)} pages)")
        return True
    else:
        print("ERROR: PDF was not generated.")
        return False

def build_docx():
    print("Generating complete Microsoft Word (.docx) report...")
    doc = Document()
    
    # Page setup - A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.paragraph_format.line_spacing = 1.3
    normal_style.paragraph_format.space_after = Pt(6)

    # 1. Title Page
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Visvesvaraya Technological University, Belagavi – 590018.\n\n")
    run.font.size = Pt(13)
    
    if os.path.exists(os.path.join(IMG_DIR, "logo_1.jpeg")):
        doc.add_picture(os.path.join(IMG_DIR, "logo_1.jpeg"), width=Inches(1.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PROJECT REPORT\nON\n").bold = True
    run_title = p.add_run(f"{FRONT_MATTER['title']}\n\n")
    run_title.bold = True
    run_title.font.size = Pt(15)
    
    p.add_run("Submitted in partial fulfillment for the award of degree of\n").italic = True
    p.add_run(f"{FRONT_MATTER['degree']}\nin\n{FRONT_MATTER['branch']}\n\n").bold = True
    p.add_run("Submitted by\n").italic = True
    for name, usn in FRONT_MATTER['students']:
        p.add_run(f"{name}    {usn}\n")
    p.add_run(f"\nUnder the Guidance of\n").italic = True
    p.add_run(f"{FRONT_MATTER['guide']}\n").bold = True
    p.add_run(f"{FRONT_MATTER['guide_desig']}\n\n")
    
    if os.path.exists(os.path.join(IMG_DIR, "logo_2.jpeg")):
        doc.add_picture(os.path.join(IMG_DIR, "logo_2.jpeg"), width=Inches(1.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n").bold = True
    p.add_run(f"{FRONT_MATTER['college']}\n").bold = True
    p.add_run(f"{FRONT_MATTER['college_sub']}\n")
    p.add_run(f"{FRONT_MATTER['address']}\n").bold = True
    p.add_run(f"{FRONT_MATTER['year']}\n").bold = True

    doc.add_page_break()

    # 2. Certificate
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"{FRONT_MATTER['college']}\n").bold = True
    p.add_run(f"{FRONT_MATTER['college_sub']}\n{FRONT_MATTER['address']}\n")
    p.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n\n").bold = True
    p.add_run("CERTIFICATE\n").bold = True
    
    doc.add_paragraph(f"Certified that the project work entitled “{FRONT_MATTER['title']}” carried out by:")
    for name, usn in FRONT_MATTER['students']:
        p = doc.add_paragraph(f"• {name} ({usn})")
        p.paragraph_format.left_indent = Inches(0.5)
        
    doc.add_paragraph(f"the bonafide students of VII semester Department of Computer Science & Engineering in partial fulfillment for the award of Bachelor of Engineering in Department of Computer Science & Engineering of the Visvesvaraya Technological University, Belagavi during the year {FRONT_MATTER['year']}. It is certified that all corrections/suggestions indicated for Internal Assessment have been incorporated. The project report has been approved as it satisfies academic requirements.")
    
    doc.add_paragraph("\nDr. Udaya Kumar K Shenoy                    Dr. Rajgopal K T\nProject Guide                                        HoD\n\nDean-Academics                                      Principal\n\nExternal Viva:\n1. Examiner: _______________________      Signature: _____________\n2. Examiner: _______________________      Signature: _____________")
    
    doc.add_page_break()

    # 3. Declaration
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("DECLARATION\n").bold = True
    doc.add_paragraph(f"We hereby declare that our entire work embodied in this Project Report titled “{FRONT_MATTER['title']}” has been carried out at CANARA ENGINEERING COLLEGE, Mangaluru under the supervision of {FRONT_MATTER['guide']}, for the award of Bachelor of Engineering in Computer Science & Engineering. This report has not been submitted to this or any other University for the award of any other degree.")
    for name, usn in FRONT_MATTER['students']:
        doc.add_paragraph(f"{name} ({usn})")

    doc.add_page_break()

    # 4. Acknowledgement
    p = doc.add_heading("Acknowledgement", level=1)
    doc.add_paragraph("We dedicate this page to acknowledge and thank those responsible for the shaping of the project. Without their guidance and help, the experience while constructing the dissertation would not have been so smooth and efficient.")
    doc.add_paragraph(f"We sincerely thank our Project guide {FRONT_MATTER['guide']}, Professor, Dean R&D, Computer Science & Engineering for his/her guidance and valuable suggestions which helped us to complete this project.")
    doc.add_paragraph(f"We also thank our Project coordinators {FRONT_MATTER['coordinator']}, Dept of Computer Science & Engineering, for their constant encouragement.")
    doc.add_paragraph(f"We owe a profound gratitude to {FRONT_MATTER['hod']}, Head of the Department, Computer Science & Engineering, whose kind support and guidance helped us to complete this work successfully. We also thank our Dean Academics {FRONT_MATTER['dean']} and Principal for their encouragement.")
    doc.add_paragraph("We thank all faculty and staff of the Department of Computer Science & Engineering, and our beloved parents and friends for their constant support.")

    doc.add_page_break()

    # 5. Abstract
    p = doc.add_heading("Abstract", level=1)
    doc.add_paragraph(ABSTRACT_TEXT)
    p_kw = doc.add_paragraph()
    p_kw.add_run("Keywords: ").bold = True
    p_kw.add_run(KEYWORDS_TEXT)

    doc.add_page_break()

    # 6. Chapter 1: Introduction
    doc.add_heading("Chapter 1: Introduction", level=1)
    doc.add_heading("1.1 Background", level=2)
    doc.add_paragraph(CH1_CONTENT['background'])
    doc.add_heading("1.2 Motivation and Problem statement", level=2)
    doc.add_paragraph(CH1_CONTENT['motivation'])
    doc.add_heading("1.3 Objectives", level=2)
    for obj_title, obj_desc in CH1_CONTENT['objectives']:
        p = doc.add_paragraph()
        p.add_run(f"• {obj_title}: ").bold = True
        p.add_run(obj_desc)
    doc.add_heading("1.4 Scope and limitations", level=2)
    doc.add_paragraph(CH1_CONTENT['scope_limitations'])
    doc.add_heading("1.5 Relevance and Type", level=2)
    doc.add_paragraph(CH1_CONTENT['relevance_type'])
    doc.add_heading("1.6 Organization of the report", level=2)
    doc.add_paragraph(CH1_CONTENT['organization'])

    doc.add_page_break()

    # 7. Chapter 2: Literature Survey
    doc.add_heading("Chapter 2: Literature Survey", level=1)
    for idx, art in enumerate(LITERATURE_ARTICLES):
        doc.add_heading(f"{art['num']} {art['title']}", level=2)
        doc.add_paragraph(art['intro'])
        doc.add_heading(f"{art['num']}.1 Brief Findings of Article {idx+1}", level=3)
        doc.add_paragraph(art['findings'])
        doc.add_heading(f"{art['num']}.2 Design/Methodology/Techniques Adopted in Article {idx+1}", level=3)
        doc.add_paragraph(art['methodology'])
        doc.add_heading(f"{art['num']}.3 Results Achieved in Article {idx+1}", level=3)
        doc.add_paragraph(art['results'])

    # Comparison Tables
    doc.add_heading("2.21 Comparison Tables", level=2)
    for t in COMPARISON_TABLES:
        doc.add_paragraph(f"Table {t['table_num']}: {t['caption']}").bold = True
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Project Title and Author"
        hdr_cells[1].text = "Problem Addressed"
        hdr_cells[2].text = "Implementation and Results"
        hdr_cells[3].text = "Limitations / Future Scope"
        for r in t['rows']:
            row_cells = table.add_row().cells
            row_cells[0].text = r[0]
            row_cells[1].text = r[1]
            row_cells[2].text = r[2]
            row_cells[3].text = r[3].replace("<br>", "\n")
        doc.add_paragraph()

    doc.add_heading("2.22 Summary", level=2)
    doc.add_paragraph(SUMMARY_CH2)

    doc.add_page_break()

    # 8. Chapter 3: SRS
    doc.add_heading("Chapter 3: Software Requirements Specification", level=1)
    doc.add_heading("3.1 Functional requirements", level=2)
    for f_title, f_desc in CH3_CONTENT['functional']:
        p = doc.add_paragraph()
        p.add_run(f"{f_title}: ").bold = True
        p.add_run(f_desc)
    doc.add_heading("3.2 Non-Functional requirements", level=2)
    for nf_title, nf_desc in CH3_CONTENT['non_functional']:
        p = doc.add_paragraph()
        p.add_run(f"{nf_title}: ").bold = True
        p.add_run(nf_desc)
    doc.add_heading("3.3 User interface design", level=2)
    doc.add_paragraph(CH3_CONTENT['ui_design'])
    doc.add_heading("3.4 Hardware and Software requirements", level=2)
    doc.add_paragraph("Hardware Requirements:").bold = True
    for h in CH3_CONTENT['hw_sw_requirements']['hardware']:
        doc.add_paragraph(f"• {h}")
    doc.add_paragraph("Software Requirements:").bold = True
    for s in CH3_CONTENT['hw_sw_requirements']['software']:
        doc.add_paragraph(f"• {s}")
    doc.add_heading("3.5 Performance Requirements", level=2)
    doc.add_paragraph("The application processes gestures in real-time with sub-35 ms latency, sustaining 30 FPS throughput on standard consumer hardware.")
    doc.add_heading("3.6 Any Other Requirements", level=2)
    doc.add_paragraph("The architecture maintains loose coupling to allow seamless extension to additional gestures and target regional vernaculars.")
    doc.add_heading("3.7 Summary", level=2)
    doc.add_paragraph("This chapter formalized the functional and non-functional requirements governing the software implementation.")

    doc.add_page_break()

    # 9. Chapter 4: System Design
    doc.add_heading("Chapter 4: System Design", level=1)
    doc.add_heading("4.1 Abstract Design", level=2)
    doc.add_heading("4.1.1 Architectural diagram", level=3)
    doc.add_paragraph(CH4_CONTENT['arch_intro'])
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_1_architecture.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_1_architecture.jpg"), width=Inches(6.2))
        p = doc.add_paragraph("Figure 4.1: System Architecture Diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Architectural diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['arch_explanation'])

    doc.add_heading("4.2 Proposed system", level=2)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_2_flowchart.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_2_flowchart.jpg"), width=Inches(5.8))
        p = doc.add_paragraph("Figure 4.2: Proposed System Flowchart")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Proposed System:").bold = True
    doc.add_paragraph(CH4_CONTENT['flowchart_explanation'])

    doc.add_heading("4.3 Functional Design", level=2)
    doc.add_heading("4.3.1 Modular design diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_3_modular.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_3_modular.jpg"), width=Inches(6.2))
        p = doc.add_paragraph("Figure 4.3: Modular design diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Modular design diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['modular_explanation'])

    doc.add_heading("4.3.2 Sequence diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_4_sequence.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_4_sequence.jpg"), width=Inches(5.8))
        p = doc.add_paragraph("Figure 4.4: Sequence diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Sequence diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['sequence_explanation'])

    doc.add_heading("4.3.3 Use case diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_5_usecase.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_5_usecase.jpg"), width=Inches(5.5))
        p = doc.add_paragraph("Figure 4.5: Use case diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Use case diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['usecase_explanation'])

    doc.add_heading("4.4 Control Flow Design", level=2)
    doc.add_heading("4.4.1 Activity diagram for use cases", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_6_activity.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_6_activity.jpg"), width=Inches(5.8))
        p = doc.add_paragraph("Figure 4.6: Sample Activity diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Activity diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['activity_explanation'])

    doc.add_heading("4.5 Data Flow Diagram", level=2)
    doc.add_heading("4.5.1 Zero-Level Data Flow Diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_7_dfd0.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_7_dfd0.jpg"), width=Inches(6.0))
        p = doc.add_paragraph("Figure 4.7: Zero-Level Data Flow Diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Zero-Level Data Flow diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['dfd_explanations']['dfd0'])

    doc.add_heading("4.5.2 First-Level Data Flow Diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_8_dfd1.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_8_dfd1.jpg"), width=Inches(6.2))
        p = doc.add_paragraph("Figure 4.8: First-Level Data Flow Diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of First-Level Data Flow diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['dfd_explanations']['dfd1'])

    doc.add_heading("4.5.3 Second-Level Data Flow Diagram", level=3)
    if os.path.exists(os.path.join(IMG_DIR, "fig_4_9_dfd2.jpg")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_4_9_dfd2.jpg"), width=Inches(6.2))
        p = doc.add_paragraph("Figure 4.9: Second-Level Data Flow Diagram")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Explanation of Second-Level Data Flow diagram:").bold = True
    doc.add_paragraph(CH4_CONTENT['dfd_explanations']['dfd2'])

    doc.add_heading("4.5.4 Additional Design and Optimization Steps", level=3)
    doc.add_paragraph(CH4_CONTENT['optimization_steps'])
    doc.add_heading("4.5.5 Summary", level=3)
    doc.add_paragraph(CH4_CONTENT['summary'])

    doc.add_page_break()

    # 10. Chapter 5: Implementation
    doc.add_heading("Chapter 5: Implementation", level=1)
    doc.add_heading("5.1 Software used with justification", level=2)
    doc.add_paragraph(CH5_CONTENT['software_justification']['frontend'])
    doc.add_paragraph(CH5_CONTENT['software_justification']['backend'])
    doc.add_paragraph(CH5_CONTENT['software_justification']['frameworks'])
    for lang, desc in CH5_CONTENT['software_justification']['languages']:
        doc.add_paragraph(f"• {lang}: {desc}")
    doc.add_paragraph(CH5_CONTENT['software_justification']['os'])

    doc.add_heading("5.2 Hardware Used with justification", level=2)
    doc.add_paragraph(CH5_CONTENT['hardware_justification'])

    doc.add_heading("5.3 Algorithm/procedures used in different modules", level=2)
    for algo_name, algo_desc in CH5_CONTENT['algorithms']:
        doc.add_heading(algo_name, level=3)
        doc.add_paragraph(algo_desc)

    doc.add_heading("5.4 Coding/pseudocodes", level=2)
    doc.add_heading("5.4.1 Introduction", level=3)
    doc.add_paragraph("The programming phase translates the system design specifications into clean, maintainable, and high-performance code adhering to industry standards.")
    doc.add_heading("5.4.2 Programming Style", level=3)
    for k, v in CH5_CONTENT['programming_style'].items():
        doc.add_paragraph(f"• {v}")

    for p_title, p_code in CH5_CONTENT['pseudocodes']:
        doc.add_heading(p_title, level=3)
        p = doc.add_paragraph(p_code)
        p.paragraph_format.left_indent = Inches(0.4)
        for r in p.runs:
            r.font.name = 'Courier New'
            r.font.size = Pt(9.5)

    doc.add_heading("5.5 Summary", level=2)
    doc.add_paragraph(CH5_CONTENT['summary'])

    doc.add_page_break()

    # 11. Chapter 6: Results and Discussion
    doc.add_heading("Chapter 6: Results and Discussion", level=1)
    doc.add_heading("6.1 Results", level=2)
    doc.add_paragraph(CH6_CONTENT['results_discussion'])
    if os.path.exists(os.path.join(IMG_DIR, "fig_6_1_studio.png")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_6_1_studio.png"), width=Inches(5.5))
        p = doc.add_paragraph("Figure 6.1: Sample Result-1 (ISL Translation Studio Interface)")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(os.path.join(IMG_DIR, "fig_6_2_outcome.png")):
        doc.add_picture(os.path.join(IMG_DIR, "fig_6_2_outcome.png"), width=Inches(5.5))
        p = doc.add_paragraph("Figure 6.2: Sample Result-2 (Real-Time Recognition & Multilingual Outcome)")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("6.2 TESTING", level=2)
    doc.add_paragraph("Software testing establishes empirical validation of correctness, boundary resilience, and real-time execution stability.")
    doc.add_heading("6.3 TYPES OF SOFTWARE TESTING", level=2)
    doc.add_paragraph("• Black Box Testing: Validates high-level system behavior, HUD rendering, and multilingual translation against specifications without examining internal neuron activations.")
    doc.add_paragraph("• White Box Testing: Examines mathematical correctness of coordinate normalization, array slicing, and confidence filtering logic.")

    doc.add_heading("6.4 TESTING METHODOLOGY", level=2)
    for k, v in CH6_CONTENT['testing_methodology'].items():
        doc.add_paragraph(v)

    doc.add_heading("6.5 TESTING CRITERIA", level=2)
    for t in CH6_CONTENT['testing_tables']:
        doc.add_paragraph(f"Table {t['num']}: {t['caption']}").bold = True
        table = doc.add_table(rows=1, cols=len(t['headers']))
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for col_idx, h in enumerate(t['headers']):
            hdr_cells[col_idx].text = h
        for r in t['rows']:
            row_cells = table.add_row().cells
            for col_idx, val in enumerate(r):
                row_cells[col_idx].text = str(val)
        doc.add_paragraph()

    doc.add_heading("6.6 Comparative Analysis", level=2)
    doc.add_paragraph(f"Table 6.6: {CH6_CONTENT['comparative_table']['caption']}").bold = True
    table = doc.add_table(rows=1, cols=len(CH6_CONTENT['comparative_table']['headers']))
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    for col_idx, h in enumerate(CH6_CONTENT['comparative_table']['headers']):
        hdr_cells[col_idx].text = h
    for r in CH6_CONTENT['comparative_table']['rows']:
        row_cells = table.add_row().cells
        for col_idx, val in enumerate(r):
            row_cells[col_idx].text = str(val)
    doc.add_paragraph()

    doc.add_heading("6.7 Summary", level=2)
    doc.add_paragraph(CH6_CONTENT['summary'])

    doc.add_page_break()

    # 12. Chapter 7: Conclusions and Future Work
    doc.add_heading("Chapter 7: Conclusions and Future work", level=1)
    doc.add_heading("7.1 Conclusions", level=2)
    doc.add_paragraph(CH7_CONTENT['conclusions'])
    doc.add_heading("7.2 Future work", level=2)
    doc.add_paragraph(CH7_CONTENT['future_work'])

    doc.add_page_break()

    # 13. References
    doc.add_heading("References", level=1)
    for ref in REFERENCES:
        doc.add_paragraph(ref)

    doc.add_page_break()

    # 14. Appendices
    doc.add_heading(APPENDICES_CONTENT['appendix_a']['title'], level=1)
    doc.add_paragraph(APPENDICES_CONTENT['appendix_a']['text'])

    doc.add_page_break()

    doc.add_heading(APPENDICES_CONTENT['appendix_b']['title'], level=1)
    doc.add_paragraph(APPENDICES_CONTENT['appendix_b']['text'])

    doc.save(DOCX_PATH)
    size = os.path.getsize(DOCX_PATH)
    print(f"SUCCESS: Generated {DOCX_PATH} ({size:,} bytes)")
    return DOCX_PATH

if __name__ == "__main__":
    html_file = build_html()
    pdf_ok = compile_pdf()
    docx_file = build_docx()
    print("\nAll deliverables generated successfully!")
