# CV Analysis AI

## Project Overview
This project provides an AI-powered pipeline for parsing, analyzing, and scoring resumes (CVs) against job descriptions. It extracts structured information from both resumes and job descriptions, computes similarity scores using advanced NLP models, and generates actionable feedback for candidates.

## Tech Stack
- **Python 3.x**
- **spaCy**: Natural language processing (NLP) for keyword and entity extraction
- **transformers (HuggingFace)**: Pre-trained language models (e.g., DistilBERT) for feature extraction
- **PyTorch (torch)**: Backend for transformer models
- **scikit-learn**: Cosine similarity calculations
- **python-docx**: Reading and generating DOCX files
- **PyPDF2**: Extracting text from PDF files
- **re (regex)**: Text and pattern matching

## Directory Structure
```
cv_analysis_ai/
  ├── job_description_parser.py   # Job description parsing and keyword extraction
  ├── resume_parser.py            # Resume parsing (PDF/DOCX) and section extraction
  ├── resume_scorer.py            # Resume scoring and feedback generation
  ├── utils.py                    # Utility functions for parsing and extraction
  ├── generate_report.py          # Main script for analysis and DOCX report generation
```

## Setup Instructions
1. **Clone the repository and navigate to the project directory.**
2. **Install dependencies:**
   ```bash
   pip install spacy python-docx PyPDF2 torch transformers scikit-learn
   python -m spacy download en_core_web_sm
   ```
3. **Place your CV file** (PDF or DOCX) in the project directory.
4. **Edit `generate_report.py`** to specify your CV filename and job description details.

## Usage Example
Run the analysis and generate a DOCX report:
```bash
python generate_report.py
```
This will:
- Parse your CV and the job description
- Score the resume against the job requirements
- Generate actionable feedback
- Create a structured DOCX report (`resume_analysis_report.docx`)

## Approach: Local File-Based Testing
- No backend or web frontend required.
- Simply drop your CV in the directory, update the script, and run it.
- All results (score breakdown, parsed data, feedback) are saved in a shareable DOCX report.

## Extending the Project
- Add more job description fields or scoring criteria as needed.
- Integrate with a backend or web frontend for user uploads if desired.
- Batch process multiple CVs for bulk analysis.

---

**For questions or contributions, please open an issue or pull request!** 