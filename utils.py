import re

def parse_cv_template_format(text):
    """
    Parse a structured CV using multiple methods:
    1. Label-based section extraction
    2. Pattern matching for contact info
    3. spaCy NER for name detection
    """
    def extract_section(label, stop_labels):
        # Find section by label and stop at the next label
        pattern = rf"{label}[\s:\n]*(.*?)(?=({'|'.join(stop_labels)}|$))"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''

    def extract_contact_info():
        # Email patterns
        email_patterns = [
            r"[\w\.-]+@[\w\.-]+\.\w+",  # Basic email
            r"e-?mail[\s:]*([\w\.-]+@[\w\.-]+\.\w+)",  # Labeled email
            r"contact[\s:]*([\w\.-]+@[\w\.-]+\.\w+)"   # Contact section email
        ]
        
        # Phone patterns
        phone_patterns = [
            r"\+?\d[\d\s\-()]{7,}",  # Basic phone
            r"phone[\s:]*(\+?\d[\d\s\-()]{7,})",  # Labeled phone
            r"tel(?:ephone)?[\s:]*(\+?\d[\d\s\-()]{7,})",  # Tel labeled
            r"mobile[\s:]*(\+?\d[\d\s\-()]{7,})"  # Mobile labeled
        ]
        
        # Address patterns
        address_patterns = [
            r"address[\s:]*([^\n]+)",  # Labeled address
            r"location[\s:]*([^\n]+)",  # Location labeled
            r"residence[\s:]*([^\n]+)"  # Residence labeled
        ]

        contact_info = {
            'email': '',
            'phone': '',
            'address': ''
        }

        # Try all patterns for each type
        for pattern in email_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info['email'] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break

        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info['phone'] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break

        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info['address'] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break

        return contact_info

    def extract_name():
        # Try to find name in first few lines
        first_lines = text.split('\n')[:5]
        for line in first_lines:
            # Look for common name patterns
            name_patterns = [
                r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$",  # Capitalized full name
                r"name[\s:]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",  # Labeled name
                r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*$"  # Standalone name
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return ''

    # Extract contact information using multiple methods
    contact_info = extract_contact_info()
    name = extract_name()

    # Extract other sections
    labels = ['Education', 'Experience', 'Skills', 'Summary', 'Certifications', 'Projects', 'Languages']
    data = {}

    for i, label in enumerate(labels):
        stop_labels = labels[i+1:]
        data[label.lower()] = extract_section(label, stop_labels)

    # Combine all extracted information
    return {
        'name': name,
        'email': contact_info['email'],
        'phone': contact_info['phone'],
        'address': contact_info['address'],
        'education': data.get('education', ''),
        'experience': data.get('experience', ''),
        'skills': [skill.strip() for skill in re.split(r',|\n|-', data.get('skills', '')) if skill.strip()],
        'summary': data.get('summary', ''),
        'certifications': data.get('certifications', ''),
        'projects': data.get('projects', ''),
        'languages': data.get('languages', '')
    }
