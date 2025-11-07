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

def extract_relevant_text(text, keywords, weight_multiplier=2.0):
    """
    Enhanced extraction that gives more weight to sections containing keywords.
    Includes lines containing keywords and up to 3 following lines for context.
    Keyword lines are added multiple times to increase their weight in embeddings.
    """
    lines = text.splitlines()
    relevant_lines = []
    keyword_found = False
    lines_to_add = 0

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower:
            continue
            
        # Check for keyword matches
        if any(k in line_lower for k in keywords):
            keyword_found = True
            lines_to_add = 3  # Increased from 2 to 3 lines of context
            
            # Add keyword line multiple times to increase weight in embeddings
            for _ in range(int(weight_multiplier)):
                relevant_lines.append(line.strip())
        elif keyword_found and lines_to_add > 0:
            relevant_lines.append(line.strip())
            lines_to_add -= 1
        else:
            keyword_found = False
            lines_to_add = 0

    # Fallback: if no keywords found, use first 1000 chars
    extracted = " ".join(relevant_lines)
    return extracted if extracted else text[:1000]

def extract_cv_text(text):
    """
    Extract relevant information from CV using flexible keywords.
    """
    cv_keywords = [
        "position", "skills", "experience", "education", "qualification", 
        "summary", "profile", "technical skills", "work history", "employment",
        "projects", "achievements", "certifications", "training", "objective",
        "work experience", "professional experience", "technical", "technologies"
    ]
    return extract_relevant_text(text, cv_keywords, weight_multiplier=2.0)

def extract_job_text(text):
    """
    Extract relevant information from Job Description using flexible keywords.
    """
    job_keywords = [
        "job title", "requirement", "skills", "experience", "qualification", 
        "responsibilities", "description", "duties", "must have", "required",
        "looking for", "candidate should", "essential", "qualifications",
        "about the role", "position overview", "key responsibilities", "what you'll do"
    ]
    return extract_relevant_text(text, job_keywords, weight_multiplier=2.0)