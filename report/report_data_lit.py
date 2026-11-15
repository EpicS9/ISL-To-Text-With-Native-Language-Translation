# -*- coding: utf-8 -*-
"""
Chapter 2 (Literature Survey) and References for the ISL Project Report.
Extracted verbatim from the original academic report with all 20 articles and comparison tables.
"""

LITERATURE_ARTICLES = [
    {
        "num": "2.1",
        "title": "Bidirectional Indian Sign Language Converter[12]",
        "author": "Sandeep Kumar PS et al. (2025)",
        "intro": "This research by Sandeep Kumar PS et al. (2025) addresses the challenge of establishing two-way communication between signers and non-signers. The study focuses on developing a system that converts Indian Sign Language (ISL) into text and vice versa. To train and evaluate their models, the researchers utilized a custom ISL gesture dataset.",
        "findings": "The study successfully demonstrated that bidirectional communication systems for ISL can be effectively implemented, bridging the communication gap by allowing seamless back-and-forth interaction.",
        "methodology": "The authors employed computer vision-based gesture recognition as the core technology for their system. To classify and interpret the recognized gestures accurately, they integrated various machine learning-based classification techniques.",
        "results": "The system successfully enables functional bidirectional communication. However, the study notes significant limitations regarding the dataset, specifically that its small scale results in limited gesture coverage, which restricts the system's overall vocabulary."
    },
    {
        "num": "2.2",
        "title": "Enhanced Sign Language Translation between ASL and ISL Using LLMs[7]",
        "author": "Kumar et al. (2025)",
        "intro": "Conducted by Kumar et al. (2025), this article tackles the complexities of translating between American Sign Language (ASL) and Indian Sign Language (ISL). The primary problem addressed is the lack of contextual understanding in traditional translation tools. The researchers relied on comprehensive datasets encompassing both ASL and ISL.",
        "findings": "The researchers found that integrating advanced language models significantly improves the contextual and semantic accuracy of translations between two distinct sign languages.",
        "methodology": "The methodology heavily relies on Large Language Models (LLMs) to process and understand the nuances of the signs. The system utilizes Natural Language Processing (NLP) techniques to facilitate the complex translation pipeline.",
        "results": "The primary result is a noticeably better semantic translation compared to older methods. On the downside, the reliance on LLMs introduces a high computational cost, making it resource-intensive to run."
    },
    {
        "num": "2.3",
        "title": "A Continuous Indian Sign Language Production System from Isolated Signs[10]",
        "author": "Patra et al. (2025)",
        "intro": "Patra et al. (2025) focus on the difficult task of generating continuous sign language expressions rather than just individual, disjointed signs. The study addresses the gap between static gesture recognition and fluid sentence creation using an isolated sign dataset.",
        "findings": "This research paper focuses on generating continuous Indian Sign Language (ISL) sequences from isolated sign inputs. The study addresses the challenge of creating smooth and meaningful sign language communication instead of displaying separate, disconnected gestures. The authors aim to improve the natural flow of ISL production so that communication appears more realistic and understandable. The paper highlights the importance of developing advanced sign language systems that can support effective interaction for the deaf and hard-of-hearing community.",
        "methodology": "The researchers used deep learning and sequence modeling techniques to transform isolated signs into continuous ISL representations. The system analyzes individual sign gestures and predicts the correct sequence and transitions between them to create fluent sign language output. Machine learning algorithms were applied to learn temporal relationships between signs and improve gesture continuity. The framework focuses on generating natural-looking sign sequences while maintaining the meaning and context of the communication.",
        "results": "The proposed approach successfully generated smoother and more continuous ISL outputs compared to isolated sign generation methods. The results showed improvements in sign transition quality and overall communication clarity. The study demonstrated that deep learning models can effectively support continuous sign language production, making interactions more natural and user-friendly. The research also provides a foundation for future developments in real-time sign language animation and assistive communication technologies."
    },
    {
        "num": "2.4",
        "title": "Towards real-time recognition of continuous indian sign language: A multi-modal approach using RGB and pose[4]",
        "author": "Geetha et al. (2025)",
        "intro": "In this paper, Geetha et al. (2025) address the need for continuous sign recognition that operates in real-time. To build and test their system, the team developed and utilized a custom ISL dataset specifically tailored for dynamic movement tracking.",
        "findings": "The findings indicate that combining standard video feeds with spatial pose data creates a highly accurate system capable of recognizing continuous sign language on the fly.",
        "methodology": "The architecture is built on a multi-modal approach combining both video (RGB) and pose data. To process this information, the researchers implemented a hybrid framework using Convolutional Neural Networks (CNN) paired with Transformer models.",
        "results": "The system achieved a very good accuracy rate, reflected by a Word Error Rate (WER) of approximately 19. Despite this strong performance, the model still struggles to accurately interpret highly fast-paced gestures."
    },
    {
        "num": "2.5",
        "title": "Sanket Bhasha: Multilingual NLP and 3D Avatar-Based Indian Sign Language (ISL) Translator[3]",
        "author": "Ganboi et al. (2025)",
        "intro": "Ganboi et al. (2025) introduce \"Sanket Bhasha\", a system designed to convert spoken or written text into visual Indian Sign Language. The project utilizes extensive language datasets to map spoken words to their corresponding visual signs.",
        "findings": "This research paper introduces Sanket Bhasha, an Indian Sign Language (ISL) translation system that combines Natural Language Processing (NLP) with 3D avatar technology. The study aims to improve communication accessibility for deaf and hard-of-hearing individuals by converting text or speech into animated ISL gestures using a virtual 3D avatar. The paper highlights how intelligent language processing and realistic visual representation can make sign language communication more interactive, understandable, and user-friendly.",
        "methodology": "The authors used NLP techniques to analyze and process textual or spoken language inputs before converting them into Indian Sign Language sequences. A 3D animated avatar was developed to visually perform the generated ISL gestures in a realistic manner. The framework combines language understanding, gesture mapping, and animation technologies to produce meaningful sign language representations. Machine learning and language-processing methods were applied to improve translation quality and ensure smoother gesture generation by the avatar.",
        "results": "The proposed system successfully translated text and speech into animated ISL gestures using the 3D avatar. The results showed improved communication support for users who rely on sign language for interaction. The use of NLP helped enhance translation accuracy, while the 3D avatar provided a more natural and engaging visual experience. The research demonstrates the potential of combining artificial intelligence and animation technologies to build effective assistive communication systems for the deaf community."
    },
    {
        "num": "2.6",
        "title": "A Unified Computer Vision System for Multilingual Bidirectional Gesture Recognition: Asl and Isl [19]",
        "author": "Sruthi et al. (2025)",
        "intro": "This paper by Sruthi et al. (2025) tackles the challenge of multilingual gesture recognition, aiming to build a single system capable of understanding both ASL and ISL. The research utilizes combined datasets from both sign languages.",
        "findings": "The study proves the viability of creating a unified framework that does not need separate distinct models to recognize different regional sign languages.",
        "methodology": "The core methodology is based entirely on a computer vision system designed to extract and classify visual features from signers, adapting to the varying syntax and gestures of both ASL and ISL.",
        "results": "The system successfully supports and recognizes multiple sign languages simultaneously. The main drawback is the highly complex system design required to manage and differentiate between the overlapping languages."
    },
    {
        "num": "2.7",
        "title": "An effective skeleton-based approach for multilingual sign language recognition [15]",
        "author": "Renjith et al. (2025)",
        "intro": "Renjith et al. (2025) address the problem of recognizing gestures in less-than-ideal visual conditions. By using pose-based datasets, they shifted the focus from pixel-based image analysis to the structural movements of the human body.",
        "findings": "The study found that focusing purely on skeletal joint data provides a highly reliable method for recognizing multilingual sign languages, largely ignoring background interference.",
        "methodology": "The methodology involves sophisticated pose estimation techniques to map the user's body. The extracted skeleton tracking data is then fed into specialized machine learning models trained to classify the geometric movements of the joints.",
        "results": "The major achievement of this approach is its robust performance even in highly cluttered or visually noisy environments. However, processing the skeletal data makes this approach slower when compared to more lightweight, direct image-classification methods."
    },
    {
        "num": "2.8",
        "title": "Word recognition from Indian sign language in videos using dual feature descriptor and GMT-MASKRCNN recognition technique [2]",
        "author": "Bansal & Jain (2025)",
        "intro": "This research by Bansal & Jain (2025) narrows its focus to the precise recognition of individual words directly from ISL videos. The study relied on a comprehensive video-based ISL dataset to train their models on dynamic, real-world signing.",
        "findings": "The authors demonstrated that deep learning models specifically designed for image segmentation and object detection can be highly effective when repurposed for isolating and recognizing sign language vocabulary.",
        "methodology": "The study adopted a sophisticated MASK-RCNN model framework. To improve accuracy, the researchers utilized a dual feature extraction technique, allowing the model to analyze multiple layers of visual data from the video frames simultaneously.",
        "results": "The adopted methodology resulted in high accuracy in recognizing specific words from the video feeds. The primary limitation of this highly detailed analytical approach is that it is computationally intensive."
    },
    {
        "num": "2.9",
        "title": "AI-Assisted Real-Time Multilingual Sign Language Translation using 3D Avatars [14]",
        "author": "Reddy et al. (2025)",
        "intro": "Reddy et al. (2025) aim to solve the problem of real-time translation of spoken or written languages into multilingual sign language. To achieve this, the team used expansive language datasets mapping text and speech to specific sign language parameters.",
        "findings": "The study established that AI can be leveraged to generate immediate, on-the-fly translations of text and speech into sign language, utilizing digital avatars to deliver the message visually in real time.",
        "methodology": "The researchers designed a real-time translation system that integrates Natural Language Processing (NLP) to decode incoming speech and text. This processed data immediately triggers a 3D avatar animation system to perform the translated signs.",
        "results": "The system successfully provides vital visual communication support for real-time interactions. However, much like other avatar-based systems, it is limited by the accuracy of the avatar's natural expressions, which can occasionally hinder the full emotional context of the translation."
    },
    {
        "num": "2.10",
        "title": "A multi-lingual sign language recognition system using machine learning [9]",
        "author": "Najib et al. (2025)",
        "intro": "Najib et al.(2025) aims to address the challenge of recognizing and translating multiple sign languages using machine learning techniques. The study focuses on improving communication accessibility by developing a multilingual sign language recognition system capable of identifying gestures from different sign languages. To achieve this, the author utilized multilingual gesture datasets and machine learning-based recognition approaches for accurate gesture classification.",
        "findings": "The study demonstrated that machine learning techniques can effectively recognize and classify gestures from multiple sign languages with good accuracy. The system improves accessibility and communication support for users belonging to different linguistic backgrounds..",
        "methodology": "The proposed system uses machine learning algorithms along with feature extraction techniques for gesture recognition. The model processes visual gesture inputs, extracts relevant hand movement and shape features, and classifies them into corresponding sign language outputs. The approach focuses on multilingual support and efficient recognition performanc",
        "results": "The system successfully supports multilingual sign language recognition and achieves satisfactory accuracy in gesture classification. However, the model has limitations in real-time performance and may face challenges under varying environmental conditions and complex gestures."
    },
    {
        "num": "2.11",
        "title": "A Transformer-Based Deep Learning Framework for Real Time Sign Language Recognition and Multilingual Translation [11]",
        "author": "Priyadarsini et al. (2026)",
        "intro": "This research by Priyadarsini et al. (2026) addresses the communication gap between Indian Sign Language (ISL) users and non-signers. The study proposes a deep learning-based system that recognizes ISL gestures, converts the recognized gloss words into meaningful English sentences, and translates the resulting sentences into Tamil. The researchers created a dataset similar to Indian Sign Language and augmented the original dataset to support model development.",
        "findings": "The study demonstrates the feasibility of integrating sign recognition, sentence generation, and regional language translation into a single communication pipeline. The system achieved 98.65% accuracy for gloss word recognition and 99.96% accuracy for alphabet recognition. It also generates grammatically meaningful English sentences and translates them into Tamil.",
        "methodology": "The proposed system uses MediaPipe to extract hand features from sign language videos. The extracted features are stored in separate CSV files for word and alphabet recognition. A Multi-Layer Perceptron (MLP) is employed to classify the recognized words and alphabets. The sequence of recognized gloss words is then processed using a pretrained T5 Transformer to generate meaningful English sentences. Finally, a pretrained English-to-Tamil translation model converts the generated sentences into Tamil.",
        "results": "The system achieved 98.65% accuracy for gloss word recognition and 99.96% accuracy for alphabet recognition. The integration of a pretrained T5 Transformer enables the conversion of recognized signs into meaningful English sentences, followed by Tamil translation. However, the reported recognition accuracies alone do not establish the quality of the generated sentences or the accuracy of the final Tamil translations, which require separate evaluation."
    },
    {
        "num": "2.12",
        "title": "Harnessing Vision Transformers for Indian Sign Language Sentence Recognition From Videos [6]",
        "author": "Kalagudi and Thenmozhi (2025)",
        "intro": "This research by Kalagudi and Thenmozhi (2025) focuses on recognizing continuous Indian Sign Language gestures from videos and converting them into complete sentences. Unlike systems that recognize only individual signs, the proposed Signwave assistive technology aims to interpret sequences of gestures in real time. The study addresses the need for more natural communication between people with hearing or speech impairments and non-signers.",
        "findings": "The study demonstrates that combining spatial feature extraction with temporal modelling can support continuous sign language sentence recognition. The proposed Signwave system achieved an overall accuracy of 72.9% and provides both text and speech outputs. These capabilities make the system potentially useful in educational institutions, healthcare environments, workplaces, and everyday communication.",
        "methodology": "The researchers developed a hybrid architecture combining a Convolutional Neural Network (CNN) with a Vision Transformer (ViT). The CNN is used to extract spatial features from video frames, while the Vision Transformer models temporal patterns across the gesture sequence. This combination enables the system to process continuous gestures and generate sentence-level outputs. The resulting text can also be converted into speech to facilitate communication.",
        "results": "The proposed system achieved an overall recognition accuracy of 72.9%, with the authors also reporting precision, recall, and F1-score performance. The system supports both text and speech output, extending its functionality beyond isolated gesture classification. However, the reported accuracy indicates that further evaluation and improvement may be needed before relying on the system for consistently accurate real-world communication. The abstract does not provide enough detail to establish its performance across different signers or signing environments."
    },
    {
        "num": "2.13",
        "title": "Indian Sign Language Recognition using Neural Networks [1]",
        "author": "Agarwal et al. (2025)",
        "intro": "This research by Agarwal et al. (2025) focuses on developing an Indian Sign Language recognition system using neural networks to improve communication accessibility. The study explores the recognition of static hand gestures and dynamic sign language movements.",
        "findings": "The study presents a neural network-based approach for recognizing ISL gestures and supporting communication through automated sign interpretation.",
        "methodology": "The researchers use a Multi-Layer Perceptron (MLP) for static handshape recognition and a Channel-wise Topology Refinement Graph Convolutional Network (CTR-GCN) for dynamic gesture recognition.",
        "results": "The proposed approach addresses both static and dynamic sign recognition. However, further evaluation across different datasets and signing conditions is important to establish its generalization capability."
    },
    {
        "num": "2.14",
        "title": "Fingerspelling for Indian Sign Language Using Swin Transformer [20]",
        "author": "Suchithra et al. (2025)",
        "intro": "This research by Suchithra et al. (2025) focuses on recognizing Indian Sign Language fingerspelling using deep learning. The study aims to improve alphabet recognition and support accessible communication through automated gesture interpretation.",
        "findings": "The study explores the use of Transformer-based image recognition for identifying ISL fingerspelling gestures and integrating the recognized output into a communication system.",
        "methodology": "The researchers employ a Swin Transformer to extract visual features from hand gesture images. The proposed pipeline also incorporates spelling correction, machine translation, and text-to-speech components to convert recognized signs into more accessible outputs.",
        "results": "The system combines fingerspelling recognition with translation and speech generation. However, the effectiveness of the complete pipeline depends on recognition accuracy and the quality of subsequent language processing."
    },
    {
        "num": "2.15",
        "title": "Accurate Gesture Recognition in Indian Sign Language Using Deep Learning [8]",
        "author": "Meena et al. (2025)",
        "intro": "This research by Meena et al. (2025) focuses on recognizing Indian Sign Language alphabets and numerals using a transfer learning approach. The authors use a balanced Kaggle dataset containing 42,000 images representing 35 classes, including the English alphabets A–Z and numerals 1–9.",
        "findings": "The study demonstrates that a pretrained deep learning model can recognize ISL hand gestures with high classification performance. The proposed system achieves 100% precision, recall, and F1-score on the reported evaluation, highlighting the potential of transfer learning for gesture recognition.",
        "methodology": "The researchers employ MobileNetV2, a pretrained convolutional neural network, to extract visual features from hand gesture images. Transfer learning is used to adapt the pretrained model to the ISL classification task. The architecture incorporates batch normalization to stabilize training, dropout to reduce overfitting, and L2 regularization to control model complexity. A final Softmax layer classifies the input into 35 gesture classes. The dataset is divided into 70% training, 15% validation, and 15% testing data.",
        "results": "The proposed MobileNetV2 model achieves 100% precision, recall, and F1-score according to the paper's abstract. The use of transfer learning also provides a computationally efficient alternative to training a deep network from scratch. However, the reported results are based on the specified dataset, and further testing with unseen signers and real-world video inputs would help establish the model's generalization capability."
    },
    {
        "num": "2.16",
        "title": "NLP Based Gesture Translation Recognition for Inclusive Communication [5]",
        "author": "JosephineUsha et al. (2025)",
        "intro": "This research by JosephineUsha et al. (2025) presents HySign-Transformer, an intelligent and low-cost communication system designed to reduce barriers between sign language users and non-signers. The system accepts audio input, converts it into text, and generates corresponding sign gesture images and videos, supporting English and Indian Sign Language (ISL) communication.",
        "findings": "The study demonstrates an integrated approach that combines speech recognition, natural language processing, and gesture generation within a single communication pipeline. The authors report that the generated sign representations provide reasonably understandable output and can support more immediate communication between people who use speech and those who communicate through signs.",
        "methodology": "The proposed HySign-Transformer system consists of two main stages. First, the Google Speech API converts the user's audio input into text. Second, Natural Language Processing (NLP) techniques process the recognized text, while a Convolutional Neural Network (CNN)-based architecture supports the generation of corresponding sign gesture images and videos. The training data includes static and dynamic English and ISL gestures arranged in different combinations, allowing the system to handle more than isolated hand poses.",
        "results": "The authors report that the generated gesture output translates reasonably well into human-understandable communication. The system offers a low-cost alternative to solutions that depend on more specialized sign-to-speech infrastructure. However, its performance depends on speech transcription quality, the coverage of the gesture training data, and the accuracy of mapping natural-language input to the appropriate signs. The available abstract does not provide a numerical accuracy score for the complete pipeline."
    },
    {
        "num": "2.17",
        "title": "Multimodal AI for Audio and Video Conversion for ISL Using Federated Learning [16]",
        "author": "SandeepVarma et al. (2025)",
        "intro": "This research by SandeepVarma et al. (2025) presents a multimodal artificial intelligence system designed to improve communication between Indian Sign Language (ISL) users and people who communicate through speech. The proposed system integrates audio, text, and gesture translation to support bidirectional communication. The authors also address data privacy and scalability by employing federated learning instead of relying entirely on centralized model training.",
        "findings": "The study demonstrates the feasibility of combining speech processing and video-based sign recognition within a unified communication platform. The developed system supports audio-to-ISL and ISL-to-text translation through a graphical user interface and achieves 84.93% accuracy for ISL-to-text translation.",
        "methodology": "The proposed system incorporates a Transformer-based model for converting audio into text and a Spatial Temporal Convolutional Graph Network (STCGN) combined with Long Short-Term Memory (LSTM) networks for translating ISL video sequences into text. Federated learning is used to train the models across distributed clients without requiring all training data to be collected centrally. The system integrates these components through a graphical user interface that supports both audio-to-ISL and ISL-to-text communication.",
        "results": "The ISL-to-text model achieved an accuracy of 84.93% in the reported experiments. The system demonstrates the potential of federated learning for developing privacy-aware and scalable sign language translation applications. However, the authors identify noisy environments and dynamic gestures as continuing challenges, with future improvements needed to support regional variations and the grammatical complexity of ISL."
    },
    {
        "num": "2.18",
        "title": "Indian Sign Language Recognition and Translation: An Encoder-Decoder Approach [17]",
        "author": "Sharma, Singh, and Gaito (2025)",
        "intro": "This research by Sharma, Singh, and Gaito (2025) investigates Indian Sign Language recognition and translation using an encoder-decoder approach. Published in the 17th International Conference on Communication Systems and Networks (COMSNETS 2025), the study focuses on the challenge of converting visual sign language input into a linguistic representation that can be understood by non-signers.",
        "findings": "The paper explores encoder-decoder modelling as an approach to ISL recognition and translation. Such a framework can represent the visual input in an encoded feature space and use a decoder to produce the corresponding linguistic output. The specific experimental findings and quantitative performance of the proposed system require verification from the full paper.",
        "methodology": "The study is identified as an encoder-decoder-based approach to Indian Sign Language recognition and translation. In this general architecture, an encoder extracts a representation from the input data, while a decoder generates the corresponding output sequence.",
        "results": "The paper addresses the application of encoder-decoder modelling to ISL recognition and translation."
    },
    {
        "num": "2.19",
        "title": "Indian Sign Language Detection for Real-Time Translation Using Machine Learning [18]",
        "author": "Singhal et al. (2025)",
        "intro": "This research by Singhal et al. (2025) focuses on developing a machine learning-based system for detecting Indian Sign Language gestures and translating them in real time. The study aims to reduce communication barriers between ISL users and non-signers by converting recognized hand gestures into an understandable output.",
        "findings": "The research investigates the feasibility of combining real-time gesture detection with machine learning-based classification to support accessible communication. The system is designed to recognize hand gestures from visual input and provide corresponding translated output.",
        "methodology": "The proposed approach uses computer vision techniques to identify hand gestures from input images or video frames. MediaPipe is used to extract hand landmarks, while a machine learning model processes the extracted features to classify the corresponding signs. The recognized output is then used in the translation pipeline to facilitate real-time communication.",
        "results": "The study explores the use of machine learning and landmark-based feature extraction for real-time ISL recognition. However, the exact dataset characteristics, numerical accuracy, and detailed evaluation results should be verified from the original IEEE paper before drawing conclusions about the system's performance."
    },
    {
        "num": "2.20",
        "title": "Smart Computing for Communication: Real-Time Sign Language Translation for Educational Accessibility of Hard-of-Hearing Individuals [13]",
        "author": "Raja et al. (2025)",
        "intro": "This research by Raja et al. (2025) focuses on applying smart computing technologies to improve educational accessibility for individuals with hearing impairments. The study explores a real-time sign language translation system intended to make educational content more accessible and support communication between learners and educators.",
        "findings": "The paper investigates how real-time sign language translation can be incorporated into educational environments to improve communication accessibility. Its primary focus is the practical application of computing technologies to support inclusive learning for individuals with hearing impairments.",
        "methodology": "The research addresses a technology-assisted sign language translation system designed for educational accessibility. However, the exact recognition architecture, dataset, preprocessing methods, and translation pipeline cannot be established reliably from the bibliographic information alone and must be checked in the full publication.",
        "results": "The study explores the potential of real-time sign language translation to support inclusive educational communication. However, the specific experimental results, evaluation metrics, and limitations require verification from the original paper before they can be reported accurately."
    }
]

COMPARISON_TABLES = [
    {
        "table_num": "2.1",
        "caption": "Comparison of Existing Work and Gap Identification",
        "rows": [
            ("Bidirectional Indian Sign Language Converter By Sandeep Kumar PS et.al., 2025 [12]",
             "The authors focused on enabling two-way communication between signers and non-signers by converting Indian Sign Language (ISL) into text and vice versa using a custom ISL gesture dataset.",
             "The system was implemented using computer vision techniques along with machine learning-based classification methods for gesture recognition and interpretation.",
             "- Successfully enabled bidirectional communication between users<br>- Limited gesture coverage due to small dataset size<br>- Future scope includes expanding vocabulary and improving dataset diversity"),
            ("Enhanced Sign Language Translation between ASL and ISL Using LLMs By Kumar et.al., 2025 [7]",
             "The paper addressed the problem of contextual and semantic translation between American Sign Language (ASL) and Indian Sign Language (ISL).",
             "The authors used Large Language Models (LLMs) and Natural Language Processing (NLP) techniques for multilingual sign translation and contextual understanding.",
             "- Improved semantic and contextual translation accuracy<br>- High computational and hardware requirements<br>- Future work can focus on lightweight real-time implementation"),
            ("A Continuous Indian Sign Language Production System from Isolated Signs By Patra et.al., 2025 [10]",
             "The study focused on generating continuous ISL sequences from isolated gestures to improve natural communication flow.",
             "Deep learning and sequence modeling techniques were used to predict smooth transitions between isolated signs and generate continuous ISL outputs.",
             "- Generated smoother and more natural sign sequences<br>- Depends heavily on predefined isolated sign datasets<br>- Future scope includes real-time continuous sign generation"),
            ("Towards Real-Time Recognition of Continuous Indian Sign Language: A Multi-Modal Approach Using RGB and Pose By Geetha et.al., 2025 [4]",
             "The paper addressed the challenge of real-time continuous sign language recognition using dynamic movement tracking.",
             "The system used a multi-modal framework combining RGB video data, pose estimation, CNN, and Transformer models for recognition.",
             "- Achieved good recognition accuracy with WER of around 19<br>- Struggles with highly fast-paced gestures<br>- Future improvements can focus on robustness and speed optimization")
        ]
    },
    {
        "table_num": "2.2",
        "caption": "Comparison of Existing Work and Gap Identification",
        "rows": [
            ("Sanket Bhasha: Multilingual NLP and 3D Avatar-Based Indian Sign Language Translator By Ganboi et.al., 2025 [3]",
             "The research focused on converting spoken or written language into visual ISL gestures using multilingual translation support.",
             "The authors combined NLP techniques with a 3D animated avatar system to generate realistic ISL gesture animations.",
             "- Improved accessibility through visual sign communication<br>- Avatar expressions may not always appear natural<br>- Future scope includes improving realism and emotional expression"),
            ("A Unified Computer Vision System for Multilingual Bidirectional Gesture Recognition: ASL and ISL By Sruthi et.al., 2025 [19]",
             "The paper aimed to develop a unified framework capable of recognizing both ASL and ISL gestures.",
             "Computer vision-based feature extraction and multilingual gesture recognition techniques were implemented using combined datasets.",
             "- Successfully supported multilingual gesture recognition<br>- Complex system architecture and high computational requirements<br>- Future work can focus on lightweight implementation"),
            ("An Effective Skeleton-Based Approach for Multilingual Sign Language Recognition By Renjith et.al., 2025 [15]",
             "The study addressed gesture recognition in cluttered and noisy visual environments using skeletal movement data.",
             "Pose estimation and skeleton tracking techniques were combined with machine learning models for gesture classification.",
             "- Robust performance in visually noisy environments<br>- Slower processing due to skeleton tracking computations<br>- Future improvements can optimize processing speed"),
            ("Word Recognition from Indian Sign Language in Videos Using GMT-MASKRCNN Recognition Technique By Bansal & Jain, 2025 [2]",
             "The paper focused on recognizing words directly from ISL video sequences.",
             "The authors used MASK-RCNN along with dual feature extraction techniques for video-based word recognition.",
             "- Achieved high word recognition accuracy<br>- Computationally intensive approach<br>- Future scope includes lightweight optimization for real-time use")
        ]
    },
    {
        "table_num": "2.3",
        "caption": "Comparison of Existing Work and Gap Identification",
        "rows": [
            ("AI-Assisted Real-Time Multilingual Sign Language Translation Using 3D Avatars By Reddy et.al., 2025 [14]",
             "The study aimed to provide real-time multilingual translation of text and speech into sign language.",
             "NLP techniques and 3D avatar animation systems were integrated for real-time visual translation.",
             "- Enabled real-time multilingual sign translation<br>- Limited by avatar expression realism<br>- Future work can improve natural gesture animation"),
            ("A Multi-Lingual Sign Language Recognition System Using Machine Learning By Najib et.al., 2025 [9]",
             "The paper addressed multilingual sign language recognition and classification using machine learning methods.",
             "Machine learning algorithms and feature extraction techniques were used to process and classify gesture inputs from multiple sign languages.",
             "- Achieved satisfactory multilingual gesture recognition accuracy<br>- Performance affected in complex real-world environments<br>- Future scope includes improving real-time performance and robustness"),
            ("A Transformer Based Deep Learning Framework for Real Time Sign Language Recognition and Multilingual Translation by Priyadarsini et al., 2026 [11]",
             "The authors developed a system to recognize ISL gestures, generate meaningful English sentences, and translate them into Tamil using a custom ISL dataset.",
             "MediaPipe was used for hand feature extraction, an MLP for alphabet and gloss classification, and a pretrained T5 Transformer for sentence generation, followed by an English-to-Tamil translation model.",
             "- Reported 98.65% gloss recognition accuracy and 99.96% alphabet recognition accuracy.<br>- Supports English sentence generation and Tamil translation.<br>- Translation quality requires separate evaluation."),
            ("Harnessing Vision Transformers for Indian Sign Language Sentence Recognition From Videos by Kalagudi and Thenmozhi, 2025 [6]",
             "The authors proposed a system called Signwave to recognize continuous ISL gestures from videos and convert them into sentence-level text and speech output.",
             "A hybrid CNN and Vision Transformer architecture was used to extract spatial features from video frames and model temporal patterns across gesture sequences.",
             "- Reported an overall recognition accuracy of 72.9%.<br>- Supports both text and speech output.<br>- Further improvements are needed for reliable continuous sign recognition.")
        ]
    },
    {
        "table_num": "2.4",
        "caption": "Comparison of Existing Work and Gap Identification",
        "rows": [
            ("Indian Sign Language Recognition using Neural Networks by Agarwal et al., 2025 [1]",
             "The authors investigated ISL gesture recognition using neural networks, considering both static handshapes and dynamic sign movements.",
             "A Multi-Layer Perceptron (MLP) was used for static handshape recognition, while a CTR-GCN was employed for dynamic gesture recognition.",
             "- Addresses both static and dynamic sign recognition.<br>- Combines neural network classification with graph-based modelling of movement.<br>- Generalization is needed further evaluation."),
            ("Fingerspelling for Indian Sign Language Using Swin Transformer by Suchithra et al., 2025 [20]",
             "The authors focused on recognizing ISL fingerspelling gestures to support alphabet recognition and accessible communication.",
             "A Swin Transformer was used for visual feature extraction, with additional components for spelling correction, machine translation, and text-to-speech output.",
             "- Combines fingerspelling recognition with translation and speech generation.<br>- Supports a pipeline for converting recognized gestures into accessible outputs.<br>- Overall performance depends on accuracy"),
            ("Accurate Gesture Recognition in Indian Sign Language Using Deep Learning by Meena et al., 2025 [8]",
             "The authors developed an ISL gesture classification system using a dataset of 42,000 images across 35 classes representing alphabets and numerals.",
             "MobileNetV2 transfer learning was used for feature extraction and classification, with batch normalization, dropout, and L2 regularization to improve generalization and reduce overfitting.",
             "- Reported 100% precision, recall, and F1-score on the evaluated dataset.<br>- Uses transfer learning to reduce the need to train a deep model.<br>- Testing with unseen signers and real-world video inputs is needed."),
            ("NLP Based Gesture Translation Recognition for Inclusive Communication by JosephineUsha et al., 2025 [5]",
             "The authors proposed HySign-Transformer, a communication system that converts audio into text and generates corresponding sign gesture images and videos.",
             "Google Speech API was used for speech-to-text conversion, followed by NLP processing and a CNN-based component for gesture representation generation.",
             "- Integrates speech recognition, language processing, and gesture output.<br>- Supports audio-based interaction for inclusive communication.<br>- Accuracy score for the complete pipeline is not published.")
        ]
    },
    {
        "table_num": "2.5",
        "caption": "Comparison of Existing Work and Gap Identification",
        "rows": [
            ("Multimodal AI for Audio and Video Conversion for ISL Using Federated Learning by SandeepVarma et al., 2025 [16]",
             "The authors proposed a multimodal system for ISL communication that integrates audio processing and video-based sign recognition while addressing privacy through federated learning.",
             "A Transformer based model was used for audio-to-text conversion, while a STCGN combined with LSTM was used for ISL video-to-text translation.",
             "- Reported 84.93% accuracy for ISL-to-text translation.<br>- Supports audio-to-ISL and ISL-to-text communication.<br>- Noisy environments and dynamic gestures remain challenging."),
            ("Indian Sign Language Recognition and Translation: An Encoder-Decoder Approach by Sharma et al., 2025 [17]",
             "The authors investigated an encoder-decoder approach for converting visual ISL input into a linguistic representation to improve communication.",
             "The proposed approach is based on an encoder-decoder architecture, in which an encoder represents the input features and a decoder generates the corresponding linguistic output.",
             "- Explores encoder-decoder modelling for ISL recognition and translation.<br>- Provides a framework for mapping visual input to language output."),
            ("Indian Sign Language Detection for Real-Time Translation Using Machine Learning by Singhal et al., 2025 [18]",
             "The authors focused on detecting ISL gestures and translating them in real time to support communication between sign language users and non-signers.",
             "The described pipeline uses computer vision and MediaPipe-based hand landmark extraction, followed by machine learning-based gesture classification and translation.",
             "- Focuses on real-time gesture detection and translation.<br>- Uses landmark-based features for gesture recognition.<br>- Reported accuracy must be verified in real-world environment."),
            ("Smart Computing for Communication: Real-Time Sign Language Translation for Educational Accessibility of Hard-of-Hearing Individuals by Raja et al., 2025 [13]",
             "The authors explored real-time sign language translation as a way to improve educational accessibility and communication between learners with hearing impairments and educators.",
             "The study presents a technology-assisted sign language translation system for educational use. The specific recognition architecture, dataset, and processing pipeline require confirmation from the full paper.",
             "- Focuses on inclusive communication in educational environments.<br>- Explores the practical application of real-time sign language translation.<br>- Quantitative results and implementation details require verification.")
        ]
    }
]

SUMMARY_CH2 = """This chapter reviewed 20 research papers related to Indian Sign Language (ISL) recognition, translation, and assistive communication using techniques such as machine learning, deep learning, computer vision, and Transformers. The studies explored gesture recognition, continuous sign language translation, bidirectional communication, and multilingual output.

The review identified challenges such as limited datasets, variations in gestures, real-time recognition, and translation accuracy. These research gaps provide a foundation for the proposed system, which aims to convert ISL gestures into text and native Indian languages. The next chapter describes the software requirements and system specifications."""

REFERENCES = [
    "[1] Arpita Agarwal, Aditya Gupta, Dheeraj Devadas, Ayush Duduskar, and Gaurav Patil. “Indian Sign Language Recognition using Neural Networks”. In: 2025 5th International Conference on Artificial Intelligence and Signal Processing (AISP). IEEE. 2025, pp. 1–5.",
    "[2] Naman Bansal and Abhilasha Jain. “Word recognition from Indian sign language in videos using dual feature descriptor and GMT-MASKRCNN recognition technique”. In: Multimedia Tools and Applications 84.5 (2025), pp. 2565–2597.",
    "[3] Dikesh Ganboi, Mohini Kumbhar, Dipak Surnar, and Harsh Patel. “Sanket Bhasha: Multilingual NLP and 3D Avatar-Based Indian Sign Language (ISL) Translator”. In: 2025 IEEE Pune Section International Conference (PuneCon). IEEE. 2025, pp. 1–6.",
    "[4] Madathilkulangara Geetha, Neena Aloysius, Darshik A Somasundaran, Amritha Raghunath, and Prema Nedungadi. “Towards real-time recognition of continuous indian sign language: A multi-modal approach using RGB and pose”. In: IEEE Access (2025).",
    "[5] L JosephineUsha et al. “NLP based Gesture Translation Recognition for Inclusive Communication”. In: 2025 5th International Conference on Ubiquitous Computing and Intelligent Information Systems (ICUIS). IEEE. 2025, pp. 1334–1339.",
    "[6] Prakruti M Kalagudi and S Thenmozhi. “Harnessing Vision Transformers for Indian Sign Language Sentence Recognition From Videos”. In: 2025 IEEE International Conference on Distributed Computing, VLSI, Electrical Circuits and Robotics (DISCOVER). IEEE. 2025, pp. 297–301.",
    "[7] Malay Kumar, S Sarvajit Visagan, Tanish Mahajan, Anisha Natarajan, and PS Sreeja. “Enhanced Sign Language Translation between American Sign Language and Indian Sign Language Using LLMs”. In: IEEE Access (2025).",
    "[8] Kunj Bihari Meena, Sambhav Mehta, Sameer Hasan, Sanjana Shrivastava, and Vipin Tyagi. “Accurate Gesture Recognition in Indian Sign Language Using Deep Learning”. In: 2025 7th International Conference on Information Systems and Computer Networks (ISCON). IEEE. 2025, pp. 1–6.",
    "[9] Fatma M Najib. “A multi-lingual sign language recognition system using machine learning”. In: Multimedia Tools and Applications 84.24 (2025), pp. 27987–28011.",
    "[10] Suvajit Patra, Arkadip Maitra, and Soumitra Samanta. “A Continuous Indian Sign Language Production System from Isolated Signs”. In: 2025 11th International Conference on Smart Computing and Communications (ICSCC). IEEE. 2025, pp. 1–6.",
    "[11] PLK Priyadarsini, P Madhumitha, M Priyadharshan, S Sai Mrithula, et al. “A Transformer-Based Deep Learning Framework for Real Time Sign Language Recognition and Multilingual Translation”. In: 2026 10th International Conference on Inventive Systems and Control (ICISC). IEEE. 2026, pp. 1363–1369.",
    "[12] Sandeep Kumar PS, Ajay Krishna VK, Rahul Dhanaraj, Shins John Jaison, Jithin KC, et al. “Bidirectional Indian Sign Language Converter”. In: 2025 International Conference on Networks & Advances in Computational Technologies (NetACT). IEEE. 2025, pp. 1–6.",
    "[13] Kanaga Suba Raja, S Shanmugapriya, et al. “Smart Computing for Communication: Real-Time Sign Language Translation for Educational Accessibility of Hard-of-Hearing Individuals”. In: 2025 4th OPJU International Technology Conference (OTCON) on Smart Computing for Innovation and Advancement in Industry 5.0. IEEE. 2025, pp. 1–6.",
    "[14] M Venkata Krishna Reddy, Jayasree Rathod, and Uppari Sangeetha. “AI-Assisted Real-Time Multilingual Sign Language Translation using 3D Avatars”. In: 2025 Third International Conference on Emerging Applications of Material Science and Technology (ICEAMST). IEEE. 2025, pp. 1604–1609.",
    "[15] S Renjith, MS Sumi Suresh, and Manazhy Rashmi. “An effective skeleton-based approach for multilingual sign language recognition”. In: Engineering Applications of Artificial Intelligence 143 (2025), p. 109995.",
    "[16] N SandeepVarma, Siddharth Sahay, Vishesh Bishnoi, Varsh Gandhi, and Mathias Prajwal Dsouza. “Multimodal AI for Audio and Video Conversion for ISL Using Federated learning”. In: 2025 IEEE North Karnataka Subsection Flagship International Conference (NKCon). IEEE. 2025, pp. 1–6.",
    "[17] Vibhor Sharma, Anurag Singh, and Sabrina Gaito. “Indian Sign Language recognition and translation: An Encoder-Decoder Approach”. In: 2025 17th International Conference on COMmunication Systems and NETworks (COMSNETS). IEEE. 2025, pp. 802–804.",
    "[18] Rajat Singhal, Jatin Gupta, Akhil Sharma, Anushka Gupta, and Navya Sharma. “Indian sign language detection for real-time translation using machine learning”. In: 2025 6th International Conference on Recent Advances in Information Technology (RAIT). IEEE. 2025, pp. 1–6.",
    "[19] KS Sruthi, Sukshma Shetty, Sanya Pateel, et al. “A Unified Computer Vision System for Multilingual Bidirectional Gesture Recognition: Asl and Isl”. In: 2025 3rd International Conference on Recent Advances in Information Technology for Sustainable Development (ICRAIS). IEEE. 2025, pp. 67–72.",
    "[20] M Suchithra, Ayushi Gupta, and Abhilasha Kasaraneni. “Fingerspelling for indian sign language using swin transformer”. In: 2025 6th International Conference on Intelligent Communication Technologies and Virtual Mobile Networks (ICICV). IEEE. 2025, pp. 947–952."
]
