import torch
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity

import ast

# Load the pre-trained model
nlp = pipeline('feature-extraction', model='distilbert-base-uncased', framework='pt')

import ast

def to_clean_string(value):
    """Converts stringified lists or other formats to clean plain text"""
    try:
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            # Try parsing the list if it's stringified
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return " ".join(str(item) for item in parsed)
        elif isinstance(value, list):
            return " ".join(str(item) for item in value)
        elif isinstance(value, str):
            return value
        return str(value)
    except Exception as e:
        print(f"[WARN] Failed to clean string: {e}")
        return str(value)


def safe_parse_list(value):
    """Parses a stringified list into a real list, or returns the original list."""
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        try:
            return ast.literal_eval(value)
        except Exception as e:
            print(f"[WARN] Could not parse list: {e}")
            return []
    elif isinstance(value, list):
        return value
    return []


def calculate_similarity(text1, text2):
    # Use the pre-trained model to get feature vectors
    vec1 = nlp(text1)
    vec2 = nlp(text2)

    # Perform average pooling to get fixed-size vectors
    vec1_mean = torch.mean(torch.tensor(vec1), dim=1)
    vec2_mean = torch.mean(torch.tensor(vec2), dim=1)

    # Calculate cosine similarity
    similarity = cosine_similarity(vec1_mean, vec2_mean)[0][0]
    return similarity


import re

def check_resume_structure(resume_text):
    sections = {
        'Contact Information': False,
        'Summary or Objective': False,
        'Skills': False,
        'Experience': False,
        'Education': False,
        'Certifications': False,
        'Projects': False
    }

    # Lowercase for case-insensitive matching
    clean_text = resume_text.lower()

    # Normalize multiple newlines/spacing
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Section detection keywords
    keywords = {
        'Contact Information': ['contact', 'email', 'phone', 'address'],
        'Summary or Objective': ['summary', 'objective', 'overview', 'profile'],
        'Skills': ['skill', 'skills', 'competency', 'proficiency'],
        'Experience': ['experience', 'work history', 'professional experience', 'employment history'],
        'Education': ['education', 'academic background', 'qualifications'],
        'Certifications': ['certification', 'certificate', 'certifications'],
        'Projects': ['project', 'projects', 'portfolio']
    }

    for section, keys in keywords.items():
        for keyword in keys:
            if keyword in clean_text:
                sections[section] = True
                break  # Stop once any keyword is found

    structure_score = sum(sections.values()) / len(sections) * 100
    print(f"Debug: Detected sections: {sections}")
    return structure_score, sections


def score_resume(resume_data, job_data):
    # 🧹 Clean inputs
    resume_skills = to_clean_string(resume_data.get('skills', ''))
    resume_experience = to_clean_string(resume_data.get('work experience', ''))
    resume_education = to_clean_string(resume_data.get('education', ''))
    resume_certifications = to_clean_string(resume_data.get('certifications', ''))
    resume_projects = to_clean_string(resume_data.get('projects', ''))
    resume_languages = to_clean_string(resume_data.get('languages', ''))

    job_skills = to_clean_string(job_data.get('skills', ''))
    job_experience = to_clean_string(job_data.get('experience', ''))
    job_education = to_clean_string(job_data.get('education', ''))
    job_certifications = to_clean_string(job_data.get('certifications', ''))
    job_projects = to_clean_string(job_data.get('projects', ''))
    job_languages = to_clean_string(job_data.get('languages', ''))

    try:
        # 🧠 Entity score (keywords)
        resume_entities = set(word.lower() for ent in resume_data.get('entities', []) for word in ent.split())
        job_entities = set(job_data.get('keywords', []))
        entity_score = len(resume_entities & job_entities) / len(job_entities) * 100 if job_entities else 0

        # 🤖 Similarity scores
        skills_score = calculate_similarity(resume_skills, job_skills) * 100
        experience_score = calculate_similarity(resume_experience, job_experience) * 100
        education_score = calculate_similarity(resume_education, job_education) * 100
        certifications_score = calculate_similarity(resume_certifications, job_certifications) * 100
        projects_score = calculate_similarity(resume_projects, job_projects) * 100
        languages_score = calculate_similarity(resume_languages, job_languages) * 100

        structure_score, sections = check_resume_structure(resume_data.get('full_text', ''))

        total_score = (
            0.35 * skills_score +
            0.25 * experience_score +
            0.20 * projects_score +
            0.10 * entity_score +
            0.05 * education_score +
            0.03 * certifications_score +
            0.01 * languages_score +
            0.01 * structure_score
        )

        return {
            'total_score': round(total_score, 2),
            'entity_score': round(entity_score, 2),
            'skills_score': round(skills_score, 2),
            'experience_score': round(experience_score, 2),
            'education_score': round(education_score, 2),
            'certifications_score': round(certifications_score, 2),
            'projects_score': round(projects_score, 2),
            'languages_score': round(languages_score, 2),
            'structure_score': round(structure_score, 2),
            'sections': sections
        }

    except Exception as e:
        print(f"[ERROR] Scoring failed: {e}")
        return {
            'total_score': 0,
            'error': str(e)
        }


def generate_feedback(resume_data, job_description_data):
    feedback = []

    # Get job requirements
    job_keywords = set(job_description_data.get('keywords', []))
    
    # Get resume sections
    resume_skills = set(resume_data.get('skills', '').lower().split())
    resume_experience = set(resume_data.get('work experience', '').lower().split())
    resume_education = set(resume_data.get('education', '').lower().split())
    resume_certifications = set(resume_data.get('certifications', '').lower().split())
    resume_projects = set(resume_data.get('projects', '').lower().split())
    resume_languages = set(resume_data.get('languages', '').lower().split())

    # Skills Feedback
    missing_skills = job_keywords - resume_skills
    if missing_skills:
        feedback.append(
            f'Your skills section could be improved. Consider adding these key skills: {", ".join(list(missing_skills)[:5])}. '
            'Focus on technical skills relevant to the position.'
        )
    elif not resume_skills:
        feedback.append('Your resume is missing a skills section. Add a dedicated section highlighting your technical skills.')

    # Experience Feedback
    missing_experience = job_keywords - resume_experience
    if missing_experience:
        feedback.append(
            f'Your work experience could be enhanced. Try to highlight experience with: {", ".join(list(missing_experience)[:5])}. '
            'Include specific achievements and technologies used.'
        )
    elif not resume_experience:
        feedback.append('Your resume is missing work experience. Include relevant professional experience, even if it\'s from internships or projects.')

    # Projects Feedback
    if not resume_projects:
        feedback.append(
            'Consider adding a projects section. For software roles, highlight personal or academic projects that demonstrate your technical abilities. '
            'Include technologies used and your specific contributions.'
        )
    elif len(resume_projects) < 3:
        feedback.append('Your projects section could be more detailed. Add more projects and include specific technical details and outcomes.')

    # Education Feedback
    if not resume_education:
        feedback.append('Your resume is missing education details. Include your degree, major, and relevant coursework.')
    elif len(resume_education) < 3:
        feedback.append('Consider expanding your education section with more details about your coursework and academic achievements.')

    # Certifications Feedback
    if not resume_certifications:
        feedback.append(
            'Consider adding relevant certifications. For software roles, certifications in specific technologies or methodologies can strengthen your profile.'
        )

    # Languages Feedback
    if not resume_languages:
        feedback.append('If you know multiple programming languages, add them to your resume. This is particularly important for software development roles.')

    # Structure Feedback
    structure_score, sections = check_resume_structure(resume_data.get('full_text', ''))
    missing_sections = [section for section, present in sections.items() if not present]
    if missing_sections:
        feedback.append(f'Your resume is missing these important sections: {", ".join(missing_sections)}.')

    # General Tips
    feedback.append(
        'Remember to: '
        '1) Use action verbs to describe your achievements '
        '2) Quantify your accomplishments where possible '
        '3) Keep your resume concise and focused on relevant experience '
        '4) Ensure all technical skills mentioned are backed by experience or projects'
    )

    return ' '.join(feedback)
