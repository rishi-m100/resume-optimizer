import re
import yaml

def parse_tex(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        parsed_data = parse_latex_to_yaml_format(content)
        
        return parsed_data
    except Exception as e:
        print(f"Error parsing LaTeX: {str(e)}")
        return None

def parse_latex_to_yaml_format(content):
    parsed_data = {
        "information": {},
        "education": {},
        "technical-skills": {},
        "experience": [],
        "research": [],
        "projects": []
    }

    # Parse personal information
    parsed_data["information"]["name"] = re.search(r'\\name{(.+?)}', content).group(1)
    parsed_data["information"]["email"] = re.search(r'\\email{(.+?)}', content).group(1)
    parsed_data["information"]["phone"] = re.search(r'\\phone{(.+?)}', content).group(1)
    parsed_data["information"]["location"] = re.search(r'\\address{(.+?)}', content).group(1)

    # Parse education
    education_section = re.search(r'\\section{Education}(.+?)\\section', content, re.DOTALL).group(1)
    parsed_data["education"]["school"] = re.search(r'\\textbf{(.+?)}', education_section).group(1)
    parsed_data["education"]["degree"] = re.search(r'(Bachelor of .+?)[,\n]', education_section).group(1)
    parsed_data["education"]["major"] = re.search(r'(Computer Science|CS)', education_section).group(1)
    parsed_data["education"]["gpa"] = re.search(r'GPA:?\s*(\d\.\d+)', education_section).group(1)
    parsed_data["education"]["graduation"] = re.search(r'(May \d{4})', education_section).group(1)

    # Parse technical skills
    skills_section = re.search(r'\\section{(Technical )?Skills}(.+?)\\section', content, re.DOTALL).group(2)
    skills_items = re.findall(r'\\item\s+(.+?)(?:(?=\\item)|$)', skills_section, re.DOTALL)
    for item in skills_items:
        if ':' in item:
            key, value = item.split(':', 1)
            parsed_data["technical-skills"][key.strip().lower()] = [skill.strip() for skill in value.split(',')]

    # Parse experience
    experience_section = re.search(r'\\section{Experience}(.+?)\\section', content, re.DOTALL).group(1)
    experiences = re.split(r'\\resumeSubheading', experience_section)[1:]  # Skip the first empty split
    for exp in experiences:
        experience = {}
        parts = exp.split('}{')
        experience["company"] = parts[0].strip('{}')
        experience["title"] = parts[1].strip('{}')
        experience["dates"] = parts[2].strip('{}')
        experience["location"] = parts[3].strip('{}')
        experience["description"] = [item.strip('{}') for item in re.findall(r'\\resumeItem{(.+?)}', exp)]
        parsed_data["experience"].append(experience)

    # Parse projects (if available)
    projects_section = re.search(r'\\section{Projects}(.+)', content, re.DOTALL)
    if projects_section:
        projects = re.split(r'\\resumeSubheading', projects_section.group(1))[1:]  # Skip the first empty split
        for proj in projects:
            project = {}
            parts = proj.split('}{')
            project["title"] = parts[0].strip('{}')
            project["description"] = [item.strip('{}') for item in re.findall(r'\\resumeItem{(.+?)}', proj)]
            parsed_data["projects"].append(project)

    return parsed_data

def save_as_yaml(data, output_path):
    with open(output_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)