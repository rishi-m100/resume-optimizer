import yaml
import os
from datetime import datetime

# Load data from the text file
with open('resume_analysis.txt', 'r') as file:
    content = file.read()

# Split the content into sections
sections = content.split('\n\n')

# Function to extract items and scores
def extract_items_and_scores(section):
    lines = section.split('\n')[1:]  # Skip the header
    items = []
    for line in lines:
        if ':' in line:
            item, score = line.rsplit('(Score:', 1)
            items.append(item.strip('- ').strip())
        else:
            items.append(line.strip('- ').strip())
    return items

# Extract data from each section
experiences = extract_items_and_scores(sections[1])
projects = extract_items_and_scores(sections[2])
involvements = extract_items_and_scores(sections[3])
courseworks = extract_items_and_scores(sections[4])
research = extract_items_and_scores(sections[5])
additional_skills = extract_items_and_scores(sections[6])
developer_tools = extract_items_and_scores(sections[7])
languages = extract_items_and_scores(sections[8])
technologies = extract_items_and_scores(sections[9])

file_timestamp = ''
with open('run_timestamp_file.txt', 'r') as f:
    file_timestamp = f.read().strip()
directory = os.path.join('parsed_resumes', file_timestamp,)

# Function to find matching information in parsed resumes
def find_matching_info(item_type, item_name):
    for filename in os.listdir(directory):
        if filename.endswith('.yaml'):
            with open(os.path.join(directory, filename), 'r') as file:
                resume_data = yaml.safe_load(file)
                if item_type in resume_data:
                    for entry in resume_data[item_type]:
                        if item_type == 'experience' and entry['company'] == item_name.split(':')[0].strip():
                            return entry
                        elif item_type == 'projects' and entry['title'] == item_name:
                            return entry
                        elif item_type == 'research' and item_name in str(entry['description']):
                            return entry
    return None

# Function to get basic information and education from parsed resumes
def get_basic_info_and_education():
    for filename in os.listdir(directory):
        if filename.endswith('.yaml'):
            with open(os.path.join(directory, filename), 'r') as file:
                resume_data = yaml.safe_load(file)
                if 'information' in resume_data and 'education' in resume_data:
                    return resume_data['information'], resume_data['education']
    return None, None

# Function to parse dates in the format "Month YYYY"
def parse_date(date_str):
    if date_str.lower() in ['present', 'current', 'now']:
        return datetime.max  # Use a very large date for 'Present'
    try:
        return datetime.strptime(date_str, '%B %Y')  # Adjust the date format as necessary
    except ValueError:
        return None

# Function to get both start and end dates
def get_start_end_dates(date_range):
    dates = date_range.split(' - ')
    start_date = parse_date(dates[0])
    end_date = parse_date(dates[-1])
    return start_date, end_date

# Updated sorting key function
def sort_key(x):
    dates = x.get('dates', '').split(' - ')
    end_date = parse_date(dates[-1])
    start_date = parse_date(dates[0]) if len(dates) > 1 else None
    return (end_date, start_date)

# Get basic information and education
basic_info, education = get_basic_info_and_education()

if not basic_info or not education:
    print("Error: Could not find basic information or education in parsed resumes.")
    exit(1)

# Create the new YAML structure
new_yaml = {
    'information': basic_info,
    'education': education,
    'experience': [],
    'projects': [],
    'research': [],
    'technical-skills': {
        'languages': ', '.join(languages),
        'technologies': ', '.join(technologies),
        'developer-tools': ', '.join(developer_tools),
        'additional-skills': ', '.join(additional_skills)
    }
}

# Update education with coursework and involvement
new_yaml['education']['relevant-coursework'] = ', '.join(courseworks)
new_yaml['education']['involvement'] = ', '.join(involvements)

# Fill in experience information
for exp in experiences:
    exp_info = find_matching_info('experience', exp)
    if exp_info:
        new_yaml['experience'].append(exp_info)
    else:
        company = exp.split(':')[0].strip()
        title = exp.split(':')[1].strip() if ':' in exp else 'Not specified'
        new_yaml['experience'].append({
            'company': company,
            'title': title,
            'location': 'Not specified',
            'dates': 'Not specified',
            'description': ['Description not available']
        })

# Fill in project information
for proj in projects:
    proj_info = find_matching_info('projects', proj)
    if proj_info:
        new_yaml['projects'].append(proj_info)
    else:
        new_yaml['projects'].append({
            'title': proj,
            'date': 'Not specified',
            'tech': 'Not specified',
            'description': ['Description not available'],
            'link': None
        })

# Fill in research information
for res in research:
    res_info = find_matching_info('research', res)
    if res_info:
        # Ensure description is a list of strings, not a string representation of a list
        if isinstance(res_info['description'], str):
            res_info['description'] = eval(res_info['description'])
        new_yaml['research'].append(res_info)
    else:
        new_yaml['research'].append({
            'group': 'Research Group',
            'dates': f"{datetime.now().strftime('%B %Y')} - Present",
            'description': [res]
        })

# Sort experience, projects, and research by newest date at the top
new_yaml['experience'].sort(key=lambda x: sort_key(x), reverse=True)
new_yaml['research'].sort(key=lambda x: sort_key(x), reverse=True)

# For projects, we need to handle the 'date' field differently
new_yaml['projects'].sort(key=lambda x: parse_date(x.get('date', '')), reverse=True)

# Custom YAML dumper to format lists correctly
class CustomDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)

# Write the new YAML file
with open('new_resume.yaml', 'w') as file:
    yaml.dump(new_yaml, file, sort_keys=False, default_flow_style=False, Dumper=CustomDumper)

print("New YAML file created successfully: new_resume.yaml")
