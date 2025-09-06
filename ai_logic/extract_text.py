import re
import PyPDF2

def read_pdf_text(path):
    """
    Extract full text from a PDF file.
    """
    try:
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
            return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")

def extract_relevant_text(text, keywords):
    """
    Extracts relevant parts of a CV or Job Description by capturing lines and their context.
    Includes lines containing keywords and up to 2 following lines for more context.
    """
    lines = text.splitlines()
    relevant_lines = []
    keyword_found = False
    lines_to_add = 0

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        if any(k in line_lower for k in keywords):
            keyword_found = True
            lines_to_add = 2
            relevant_lines.append(line.strip())
        elif keyword_found and lines_to_add > 0:
            relevant_lines.append(line.strip())
            lines_to_add -= 1
        else:
            keyword_found = False
            lines_to_add = 0

    extracted = " ".join(relevant_lines)
    return extracted if extracted else text[:1000]

def extract_cv_text(text):
    """
    Extract relevant information from CV using flexible keywords.
    """
    cv_keywords = ["position", "skills", "experience", "education", "qualification", "summary", "profile", "technical skills", "work history"]
    return extract_relevant_text(text, cv_keywords)

def extract_job_text(text):
    """
    Extract relevant information from Job Description using flexible keywords.
    """
    job_keywords = ["job title", "requirement", "skills", "experience", "qualification", "responsibilities", "description", "duties"]
    return extract_relevant_text(text, job_keywords)