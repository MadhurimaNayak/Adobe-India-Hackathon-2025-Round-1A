## Evolution of Approach: From Heuristics to Layout-Aware Modeling

### Initial Strategy: Heuristic-Based Text Extraction

At the beginning of development, we relied on a traditional text extraction approach using libraries like PyMuPDF (fitz). This method parsed PDF documents by iterating through text blocks, spans, and fonts to heuristically identify headings (e.g., bold text, larger font sizes, position-based grouping) and extract corresponding content.

However, this approach quickly revealed several limitations:

- *Inconsistent Formatting*: Not all documents used bold or large fonts for headings. Some used stylistic cues like underlines, ALL CAPS, or indents, which were not reliably detected through font metadata.
- *Complex Layouts*: Multi-column documents, sidebars, footnotes, and nested tables confused the flow of text, resulting in fragmented or misaligned section detection.
- *False Positives*: Many non-heading elements (e.g., bullet points, dates, numbering) were falsely identified as headers.
- *Low Generalization*: Heuristics that worked for one document often failed on others, especially across domains or languages.

Despite applying multiple cleanup and formatting rules (e.g., ignoring digits, enforcing minimum text length, checking font boldness), the overall performance remained unstable and failed to generalize across diverse documents.

---

### Transition: Moving Toward Model-Based Layout Understanding

To overcome the above issues, we adopted a *layout-aware model-based approach* using *DocLayout-YOLO*. Unlike heuristic techniques that only look at raw text and fonts, this model:

- *Understands full document layout visually* (like a human reader would).
- Detects structured components such as *titles, paragraphs, figures, tables, footers*, and more.
- Outputs bounding boxes for each element, allowing precise spatial segmentation of the document.

By incorporating layout modeling, we significantly improved the accuracy and reliability of:

- *Title Detection*: The model could detect true section headers even if they lacked bold or size-based cues.
- *Context Preservation*: Text blocks grouped together semantically (e.g., side notes, captions) were no longer mixed with unrelated content.
- *Scalability*: The model performed consistently across PDFs with varying structures and languages.

---

### Further Improvement: Integrating OCR for Robust Text Recognition

Many PDFs (especially scanned documents or those generated from images) contained non-selectable text or partial character recognition issues. To address this, we integrated *OCR (Optical Character Recognition)* capabilities using *PaddleOCR*.

This allowed us to:
- *Extract text from images, diagrams, scanned PDFs*, and embedded annotations.
- Handle *non-English scripts* and multilingual content with improved accuracy.
- Ensure *complete text coverage*, even when layout information was visually clear but text was unreadable via traditional parsing.

---

### Result: A Unified, High-Accuracy Layout and Text Parsing System

The combination of:
- *DocLayout-YOLO* for layout segmentation,
- *Title-based heuristics on top of layout tags* for better sectioning, and
- *PaddleOCR* for robust text reading,

led to a much more accurate, scalable, and generalizable system for extracting structured information from PDFs. This significantly outperformed our initial rule-based approach and enabled consistent, high-quality section ranking across a wide variety of documents.



## Models and Libraries

MinerU is powered by a rich suite of models and libraries across its modular backends. These components enable accurate, efficient, and scalable document layout understanding, OCR, table extraction, and vision-language parsing.

---

### Core Models Used in MinerU

#### Pipeline Backend Models (pyproject.toml:58-73)

| Model                | Description                                           | Version Constraint        |
|---------------------|-------------------------------------------------------|---------------------------|
| *DocLayout-YOLO*  | Layout detection and block segmentation               | doclayout_yolo==0.0.4   |
| *UniMERNet*        | Formula recognition and semantic parsing             | |
| *RapidTable*       | Table recognition, structure analysis, and extraction| rapid_table>=1.0.5,<2.0.0|
| *PaddleOCR*        | OCR engine supporting 84+ languages                  |  |

#### VLM Backend Models

| Model                        | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| *Mineru2QwenForCausalLM*  | Lightweight custom VLM (<1B parameters) for end-to-end document understanding | (refer to README.md:122-124) |

---

###Key Library Dependencies

#### Core Processing Libraries (pyproject.toml:19-38)

These libraries support foundational PDF rendering, text extraction, and pre/post-processing workflows.

| Library          | Purpose                                | Version Constraint         |
|------------------|----------------------------------------|----------------------------|
| pypdfium2       | High-speed PDF rendering               | >=4.30.0                 |
| pdfminer.six    | PDF text extraction and parsing        | ==20250506               |
| pdftext         | Enhanced PDF text block parsing        | >=0.6.2                  |

#### Backend-Specific Libraries

| Library         | Backend            | Purpose                                    | Version Constraint           |
|------------------|---------------------|--------------------------------------------|------------------------------|
| transformers    | VLM                 | HuggingFace model loading and inference     | >=4.51.1                   |
| sglang[all]     | VLM (SGLang variant)| High-throughput generative decoding         | >=0.4.7,<0.4.10            |
| torch           | Both                | Core deep learning framework                | >=2.2.2                    |
| ultralytics     | Pipeline            | YOLO detection and layout analysis          | >=8.3.48,<9                |

---

### Model Management System

MinerU supports automatic downloading and version tracking of all required models from trusted sources.

| Source             | Description                                 | Defined in             |
|--------------------|---------------------------------------------|------------------------|
| *HuggingFace Hub*| Pretrained model downloads                  | huggingface-hub>=0.32.4 |
| *ModelScope*     | Backup and alternate model hosting          | modelscope>=1.26.0       |

Use the dedicated model download utility:
```bash
mineru-models-download
---
## Build the Docker Image

Use the following command to build the Docker image. This sets the platform explicitly to linux/amd64 for compatibility:

bash docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
