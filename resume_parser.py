import spacy
import docx
import PyPDF2

nlp = spacy.load('en_core_web_sm')


def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(path):
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

def extract_section(text, section_titles):
    if isinstance(section_titles, str):
        section_titles = [section_titles]
    section = []
    in_section = False
    for line in text.split("\n"):
        if any(title.lower() in line.lower() for title in section_titles):
            in_section = True
        elif in_section and line.strip() == "":
            break
        elif in_section:
            section.append(line)
    return "\n".join(section)


def parse_resume(resume_text):
    doc = nlp(resume_text)
    skills = extract_section(resume_text, ['skills', 'technical skills', 'core skills'])
    experience = extract_section(resume_text, ['work experience', 'professional experience', 'experience', 'employment history'])
    education = extract_section(resume_text, ['education', 'academic background', 'qualifications'])
    certifications = extract_section(resume_text, ['certifications', 'certificates'])
    projects = extract_section(resume_text, ['projects', 'project experience', 'personal projects'])
    languages = extract_section(resume_text, ['languages', 'language proficiency'])

    return {
        'skills': skills.lower(),
        'work experience': experience.lower(),
        'education': education.lower(),
        'certifications': certifications.lower(),
        'projects': projects.lower(),
        'languages': languages.lower(),
        'entities': [ent.text for ent in doc.ents],
        'full_text': resume_text
    }
