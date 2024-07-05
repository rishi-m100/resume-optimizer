import yaml
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import os

nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# ... [Keep the existing functions: load_yaml, load_job_description, extract_keywords] ...
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def load_job_description(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def extract_keywords(text):
    words = re.findall(r'\w+', text.lower())
    keywords = [word for word in words if len(word) > 2]
    
    # Add related terms to keywords
    extended_keywords = keywords.copy()
    for word in keywords:
        extended_keywords.extend(get_related_terms(word))
    
    return list(set(extended_keywords))  # Remove duplicates

def calculate_relevance(item, keywords, vectorizer):
    if isinstance(item, str):
        item_text = item
    elif isinstance(item, dict):
        item_text = ' '.join(str(value) for value in item.values())
    else:
        item_text = str(item)
    
    item_vector = vectorizer.transform([item_text])
    keywords_vector = vectorizer.transform([' '.join(keywords)])
    return cosine_similarity(item_vector, keywords_vector)[0][0]

def get_top_items(items, keywords, vectorizer, top_n):
    scored_items = [(item, calculate_relevance(item, keywords, vectorizer)) for item in items]
    return sorted(scored_items, key=lambda x: x[1], reverse=True)[:top_n]

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace('_', ' '))
    return list(synonyms)


def get_related_terms(item):
    related_terms = []

    def calculate_score(item, keywords, high_priority_words, priority_weight=2):
        base_score = sum(keyword.lower() in str(item).lower() for keyword in keywords)
        priority_score = sum(word.lower() in str(item).lower() for word in high_priority_words) * priority_weight
        return base_score + priority_score

    # Programming languages and frameworks
    programming_high_priority = ['Python', 'Java', 'JavaScript', 'C++', 'SQL']
    programming_keywords = [
        'Python', 'Java', 'JavaScript', 'C', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'TypeScript', 'Rust', 'Go', 'Perl', 'Scala', 'Haskell', 'Lua', 'Objective-C', 'Assembly',
        'SQL', 'HTML', 'CSS', 'XML', 'JSON', 'YAML', 'Markdown', 'VBScript', 'Bash', 'PowerShell',
        'Node.js', 'React', 'Angular', 'Vue.js', 'Express.js', 'Django', 'Flask', 'Spring', 'ASP.NET',
        'Ruby on Rails', 'Symfony', 'Laravel', 'Jinja', 'Hibernate', 'jQuery', 'Bootstrap', 'Tailwind CSS',
        'OpenGL', 'Unity', 'Qt', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
        'Matplotlib', 'D3.js', 'Redux', 'RxJS', 'Mocha', 'JUnit', 'Selenium', 'Jest', 'Chai',
        'Apache Kafka', 'RabbitMQ', 'GraphQL', 'RESTful', 'SOAP', 'Microservices', 'Serverless',
        'Algorithms', 'Data Structures', 'Machine Learning', 'Deep Learning', 'Artificial Intelligence'
    ]

    if calculate_score(item, programming_keywords, programming_high_priority) > 0:
        related_terms.extend(['programming', 'coding', 'development', 'software', 'algorithm', 'framework', 'library'])

    # Databases
    database_high_priority = ['MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQL Server']
    database_keywords = [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQL Server', 'SQLite', 'Redis', 'Cassandra',
        'MariaDB', 'Elasticsearch', 'DynamoDB', 'Couchbase', 'Firebase', 'Neo4j', 'Hive', 'HBase',
        'Teradata', 'Snowflake', 'BigQuery', 'Redshift', 'Vertica', 'Splunk', 'Databricks'
    ]

    if calculate_score(item, database_keywords, database_high_priority) > 0:
        related_terms.extend(['database', 'DBMS', 'SQL', 'NoSQL', 'data storage', 'query'])

    # Cloud platforms
    cloud_high_priority = ['AWS', 'Azure', 'Google Cloud', 'Kubernetes', 'Docker']
    cloud_keywords = [
        'AWS', 'Amazon Web Services', 'Azure', 'Microsoft Azure', 'Google Cloud Platform', 'GCP',
        'Heroku', 'DigitalOcean', 'IBM Cloud', 'Oracle Cloud', 'Alibaba Cloud', 'VMware',
        'OpenStack', 'Rackspace', 'Salesforce', 'SAP', 'Workday', 'ServiceNow', 'Kubernetes',
        'Docker', 'Terraform', 'Ansible', 'Chef', 'Puppet', 'Jenkins', 'GitLab CI/CD', 'CircleCI'
    ]

    if calculate_score(item, cloud_keywords, cloud_high_priority) > 0:
        related_terms.extend(['cloud computing', 'IaaS', 'PaaS', 'SaaS', 'virtualization', 'scalability', 'containerization'])

    # Version control and collaboration tools
    vcs_high_priority = ['Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN']
    vcs_keywords = [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Subversion', 'Mercurial',
        'Perforce', 'Azure DevOps', 'Jira', 'Confluence', 'Trello', 'Asana', 'Slack',
        'Microsoft Teams', 'Zoom', 'Skype', 'Notion', 'Basecamp', 'Figma', 'Miro'
    ]

    if calculate_score(item, vcs_keywords, vcs_high_priority) > 0:
        related_terms.extend(['version control', 'collaboration', 'project management', 'code repository', 'team communication'])

    # Operating systems
    os_high_priority = ['Linux', 'Windows', 'macOS', 'Unix', 'Android']
    os_keywords = [
        'Linux', 'Windows', 'macOS', 'Unix', 'Android', 'iOS', 'Ubuntu', 'Debian',
        'CentOS', 'Red Hat', 'Fedora', 'Arch Linux', 'FreeBSD', 'OpenBSD', 'Solaris',
        'Chrome OS', 'Raspberry Pi OS', 'SUSE', 'Kali Linux', 'Embedded systems'
    ]

    if calculate_score(item, os_keywords, os_high_priority) > 0:
        related_terms.extend(['operating system', 'OS', 'kernel', 'system administration', 'shell'])

    # Web technologies
    web_high_priority = ['HTML', 'CSS', 'JavaScript', 'RESTful API', 'HTTPS']
    web_keywords = [
        'HTML', 'CSS', 'JavaScript', 'DOM', 'AJAX', 'JSON', 'XML', 'RESTful API',
        'SOAP', 'WebSocket', 'OAuth', 'JWT', 'CORS', 'SSL/TLS', 'HTTPS', 'HTTP/2',
        'WebRTC', 'Progressive Web Apps', 'Single Page Applications', 'Server-Side Rendering',
        'Web Components', 'Web Assembly', 'Web Workers', 'Service Workers', 'IndexedDB'
    ]

    if calculate_score(item, web_keywords, web_high_priority) > 0:
        related_terms.extend(['web development', 'front-end', 'back-end', 'full-stack', 'responsive design', 'web security'])

    # Data science and analytics
    data_science_high_priority = ['Machine Learning', 'Data Analysis', 'Statistics', 'Big Data', 'Data Visualization']
    data_science_keywords = [
        'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Data Analysis',
        'Statistics', 'Big Data', 'Data Mining', 'Data Visualization', 'Predictive Modeling',
        'Natural Language Processing', 'Computer Vision', 'Time Series Analysis',
        'Regression', 'Classification', 'Clustering', 'Dimensionality Reduction',
        'Feature Engineering', 'A/B Testing', 'Hypothesis Testing', 'Bayesian Inference',
        'Neural Networks', 'Random Forests', 'Support Vector Machines', 'K-means',
        'Principal Component Analysis', 'Reinforcement Learning', 'Ensemble Methods'
    ]

    if calculate_score(item, data_science_keywords, data_science_high_priority) > 0:
        related_terms.extend(['data science', 'analytics', 'predictive modeling', 'statistical analysis', 'machine learning'])

    # DevOps and infrastructure
    devops_high_priority = ['CI/CD', 'Infrastructure as Code', 'Monitoring', 'Containerization', 'Configuration Management']
    devops_keywords = [
        'CI/CD', 'Continuous Integration', 'Continuous Deployment', 'Infrastructure as Code',
        'Configuration Management', 'Monitoring', 'Logging', 'Alerting', 'Containerization',
        'Orchestration', 'Load Balancing', 'Auto-scaling', 'Service Discovery', 'Microservices',
        'Serverless', 'Site Reliability Engineering', 'DevSecOps', 'GitOps', 'Chaos Engineering',
        'Blue-Green Deployment', 'Canary Releases', 'Feature Flags', 'Distributed Tracing'
    ]

    if calculate_score(item, devops_keywords, devops_high_priority) > 0:
        related_terms.extend(['DevOps', 'infrastructure', 'automation', 'deployment', 'monitoring', 'scalability'])

    # Networking
    networking_high_priority = ['TCP/IP', 'DNS', 'DHCP', 'VPN', 'Firewall']
    networking_keywords = [
        'TCP/IP', 'UDP', 'HTTP', 'HTTPS', 'FTP', 'SSH', 'DNS', 'DHCP', 'VPN', 'Firewall',
        'Router', 'Switch', 'Load Balancer', 'Proxy', 'CDN', 'NAT', 'VLAN', 'SDN',
        'BGP', 'OSPF', 'MPLS', 'IPsec', 'SSL/TLS', 'SMTP', 'POP3', 'IMAP', 'VoIP'
    ]

    if calculate_score(item, networking_keywords, networking_high_priority) > 0:
        related_terms.extend(['networking', 'protocols', 'network security', 'network infrastructure', 'connectivity'])

    # Cybersecurity
    security_high_priority = ['Encryption', 'Penetration Testing', 'Firewall', 'Intrusion Detection', 'Authentication']
    security_keywords = [
        'Encryption', 'Cryptography', 'Penetration Testing', 'Vulnerability Assessment',
        'Firewall', 'Intrusion Detection System', 'Intrusion Prevention System',
        'Authentication', 'Authorization', 'Access Control', 'SIEM', 'Incident Response',
        'Malware Analysis', 'Forensics', 'Risk Assessment', 'Compliance', 'DDoS',
        'Phishing', 'Social Engineering', 'Zero Trust', 'Threat Intelligence'
    ]

    if calculate_score(item, security_keywords, security_high_priority) > 0:
        related_terms.extend(['cybersecurity', 'information security', 'network security', 'data protection', 'threat prevention'])

    # Mobile development
    mobile_high_priority = ['iOS', 'Android', 'React Native', 'Flutter', 'Kotlin']
    mobile_keywords = [
        'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic', 'PhoneGap',
        'Swift', 'Objective-C', 'Java', 'Kotlin', 'Mobile UI/UX', 'App Store',
        'Google Play Store', 'Mobile Analytics', 'Push Notifications', 'Geolocation',
        'Augmented Reality', 'Virtual Reality', 'Mobile Security', 'Offline Storage'
    ]

    if calculate_score(item, mobile_keywords, mobile_high_priority) > 0:
        related_terms.extend(['mobile development', 'app development', 'cross-platform', 'mobile UI/UX', 'mobile security'])

    # Communication and teamwork
    communication_high_priority = ['Collaboration', 'Leadership', 'Presentation', 'Negotiation', 'Conflict Resolution']
    communication_keywords = [
        'Collaboration', 'Leadership', 'Presentation', 'Negotiation', 'Conflict Resolution',
        'Team Building', 'Active Listening', 'Interpersonal Skills', 'Public Speaking',
        'Emotional Intelligence', 'Cross-functional Coordination', 'Stakeholder Management',
        'Facilitation', 'Mentoring', 'Coaching', 'Cultural Awareness', 'Virtual Collaboration'
    ]

    if calculate_score(item, communication_keywords, communication_high_priority) > 0:
        related_terms.extend(['communication', 'teamwork', 'leadership', 'interpersonal skills', 'collaboration'])

    # Marketing and sales
    marketing_high_priority = ['Digital Marketing', 'SEO', 'Content Marketing', 'Social Media Marketing', 'CRM']
    marketing_keywords = [
        'Digital Marketing', 'SEO', 'Content Marketing', 'Social Media Marketing', 'CRM',
        'Brand Management', 'Market Research', 'Email Marketing', 'PPC', 'Affiliate Marketing',
        'Marketing Analytics', 'Public Relations', 'Sales Strategy', 'Lead Generation',
        'Customer Acquisition', 'Revenue Growth', 'Product Marketing', 'Marketing Automation'
    ]

    if calculate_score(item, marketing_keywords, marketing_high_priority) > 0:
        related_terms.extend(['marketing', 'sales', 'branding', 'customer acquisition', 'revenue growth'])

    # Finance and accounting
    finance_high_priority = ['Financial Analysis', 'Budgeting', 'Forecasting', 'Risk Management', 'Financial Reporting']
    finance_keywords = [
        'Financial Analysis', 'Budgeting', 'Forecasting', 'Risk Management', 'Financial Reporting',
        'Accounting', 'Auditing', 'Taxation', 'Financial Modeling', 'Valuation', 'M&A',
        'Corporate Finance', 'Investment Banking', 'Financial Planning', 'Cost Accounting',
        'Treasury Management', 'GAAP', 'IFRS', 'Financial Controls', 'Profit & Loss'
    ]

    if calculate_score(item, finance_keywords, finance_high_priority) > 0:
        related_terms.extend(['finance', 'accounting', 'financial management', 'budgeting', 'financial analysis'])

    # Human resources and recruiting
    hr_high_priority = ['Talent Acquisition', 'Employee Relations', 'Performance Management', 'Compensation', 'HR Analytics']
    hr_keywords = [
        'Talent Acquisition', 'Employee Relations', 'Performance Management', 'Compensation',
        'HR Analytics', 'Benefits Administration', 'HRIS', 'Workforce Planning', 'Training & Development',
        'Succession Planning', 'Labor Law', 'Diversity & Inclusion', 'Employee Engagement',
        'Organizational Development', 'HR Policies', 'Onboarding', 'Talent Management'
    ]

    if calculate_score(item, hr_keywords, hr_high_priority) > 0:
        related_terms.extend(['human resources', 'recruiting', 'talent management', 'employee relations', 'HR strategy'])

    # Writing and content creation
    writing_high_priority = ['Content Strategy', 'Copywriting', 'Technical Writing', 'Editing', 'SEO Writing']
    writing_keywords = [
        'Content Strategy', 'Copywriting', 'Technical Writing', 'Editing', 'SEO Writing',
        'Blogging', 'Journalism', 'Creative Writing', 'Content Marketing', 'Proofreading',
        'Storytelling', 'Grant Writing', 'UX Writing', 'Scriptwriting', 'White Papers',
        'Content Management', 'Editorial Planning', 'Content Optimization'
    ]

    if calculate_score(item, writing_keywords, writing_high_priority) > 0:
        related_terms.extend(['writing', 'content creation', 'editing', 'content strategy', 'copywriting'])

    # Customer support and service
    customer_service_high_priority = ['Customer Experience', 'Customer Retention', 'Help Desk', 'Conflict Resolution', 'CRM']
    customer_service_keywords = [
        'Customer Experience', 'Customer Retention', 'Help Desk', 'Conflict Resolution', 'CRM',
        'Customer Satisfaction', 'Technical Support', 'Call Center Operations', 'Customer Feedback',
        'Service Level Agreements', 'Customer Onboarding', 'Complaint Resolution', 'Live Chat Support',
        'Customer Success', 'Account Management', 'Ticketing Systems', 'Customer Loyalty'
    ]

    if calculate_score(item, customer_service_keywords, customer_service_high_priority) > 0:
        related_terms.extend(['customer support', 'customer service', 'customer experience', 'client relations', 'technical support'])

    # Legal and compliance
    legal_high_priority = ['Contract Law', 'Intellectual Property', 'Regulatory Compliance', 'Corporate Law', 'Data Privacy']
    legal_keywords = [
        'Contract Law', 'Intellectual Property', 'Regulatory Compliance', 'Corporate Law', 'Data Privacy',
        'Litigation', 'Legal Research', 'Due Diligence', 'Risk Assessment', 'GDPR', 'HIPAA',
        'Employment Law', 'Mergers & Acquisitions', 'Antitrust', 'Patent Law', 'Trademark Law',
        'Legal Writing', 'Negotiation', 'Arbitration', 'Mediation', 'Ethics'
    ]

    if calculate_score(item, legal_keywords, legal_high_priority) > 0:
        related_terms.extend(['legal', 'compliance', 'regulations', 'contracts', 'intellectual property'])

    # Education and training
    education_high_priority = ['Curriculum Development', 'Instructional Design', 'E-learning', 'Assessment', 'Adult Learning']
    education_keywords = [
        'Curriculum Development', 'Instructional Design', 'E-learning', 'Assessment', 'Adult Learning',
        'Learning Management Systems', 'Blended Learning', 'Educational Technology', 'Training Facilitation',
        'Course Creation', 'Student Engagement', 'Pedagogy', 'Classroom Management', 'Special Education',
        'STEM Education', 'Distance Learning', 'Educational Psychology', 'Professional Development'
    ]

    if calculate_score(item, education_keywords, education_high_priority) > 0:
        related_terms.extend(['education', 'training', 'teaching', 'learning', 'instructional design'])

    # Healthcare and medical
    healthcare_high_priority = ['Patient Care', 'Electronic Health Records', 'Medical Coding', 'Clinical Research', 'Healthcare Compliance']
    healthcare_keywords = [
        'Patient Care', 'Electronic Health Records', 'Medical Coding', 'Clinical Research', 'Healthcare Compliance',
        'Nursing', 'Pharmacy', 'Medical Devices', 'Health Informatics', 'Telemedicine', 'Public Health',
        'Healthcare Administration', 'Medical Billing', 'HIPAA', 'Biotechnology', 'Pharmacology',
        'Diagnostics', 'Medical Imaging', 'Healthcare Policy', 'Patient Safety', 'Epidemiology'
    ]

    if calculate_score(item, healthcare_keywords, healthcare_high_priority) > 0:
        related_terms.extend(['healthcare', 'medical', 'patient care', 'clinical', 'health informatics'])

    # Design and creative arts
    design_high_priority = ['UX/UI Design', 'Graphic Design', 'Visual Design', 'Product Design', 'Web Design']
    design_keywords = [
        'UX/UI Design', 'Graphic Design', 'Visual Design', 'Product Design', 'Web Design',
        'Branding', 'Typography', 'Illustration', 'Animation', '3D Modeling', 'CAD',
        'Industrial Design', 'Interior Design', 'Fashion Design', 'Game Design',
        'Motion Graphics', 'Photography', 'Art Direction', 'Creative Direction'
    ]

    if calculate_score(item, design_keywords, design_high_priority) > 0:
        related_terms.extend(['design', 'creative arts', 'visual communication', 'aesthetics', 'user experience'])

    # Quant finance/trading/quant software development
    quant_high_priority = ['Algorithmic Trading', 'Risk Modeling', 'Quantitative Analysis', 'Financial Engineering', 'High-Frequency Trading']
    quant_keywords = [
        'Algorithmic Trading', 'Risk Modeling', 'Quantitative Analysis', 'Financial Engineering', 'High-Frequency Trading',
        'Statistical Arbitrage', 'Options Pricing', 'Portfolio Optimization', 'Time Series Analysis',
        'Market Microstructure', 'Derivatives', 'Stochastic Calculus', 'Machine Learning in Finance',
        'Econometrics', 'Quantitative Research', 'Volatility Modeling', 'Backtesting', 'Order Execution', 'stock'
    ]

    if calculate_score(item, quant_keywords, quant_high_priority) > 0:
        related_terms.extend(['quantitative finance', 'algorithmic trading', 'financial modeling', 'risk analysis', 'quant development'])

    return related_terms



def calculate_relevance(item, keywords, vectorizer):
    if isinstance(item, str):
        item_text = item
    elif isinstance(item, dict):
        item_text = ' '.join(str(value) for value in item.values())
    else:
        item_text = str(item)
    
    related_terms = get_related_terms(item)
    extended_item = item_text + ' ' + ' '.join(related_terms)
    
    item_vector = vectorizer.transform([extended_item])

    keywords_vector = vectorizer.transform([' '.join(keywords)])
    return cosine_similarity(item_vector, keywords_vector)[0][0]

def get_top_items(items, keywords, vectorizer, top_n):
    scored_items = [(item, calculate_relevance(item, keywords, vectorizer)) for item in items]
    return sorted(scored_items, key=lambda x: x[1], reverse=True)[:top_n]

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace('_', ' '))
    return list(synonyms)

def calculate_skill_relevance(skill, keywords, vectorizer, job_description):
    skill_words = skill.lower().split()
    synonyms = [syn for word in skill_words for syn in get_synonyms(word)]
    related_terms = get_related_terms(skill)
    extended_skill = ' '.join(skill_words + synonyms + related_terms)
    
    if any(word in job_description.lower() for word in skill_words + synonyms):
        direct_match_boost = 0.5
    else:
        direct_match_boost = 0
    
    return calculate_relevance(extended_skill, keywords, vectorizer) + direct_match_boost

def process_resume(resume, job_description, keywords, vectorizer):
    top_experiences = get_top_items(resume.get('experience', []), keywords, vectorizer, 4)
    top_projects = get_top_items(resume.get('projects', []), keywords, vectorizer, 2)
    top_involvements = get_top_items(resume.get('education', {}).get('involvement', '').split(', '), keywords, vectorizer, 3)
    top_courseworks = get_top_items(resume.get('education', {}).get('relevant-coursework', '').split(', '), keywords, vectorizer, 4)
    top_research = get_top_items(resume.get('research', []), keywords, vectorizer, 1)
    
    additional_skills = resume.get('technical-skills', {}).get('additional-skills', '').split(', ')
    developer_tools = resume.get('technical-skills', {}).get('developer-tools', '').split(', ')
    languages = resume.get('technical-skills', {}).get('languages', '').split(', ')
    technologies = resume.get('technical-skills', {}).get('technologies', '').split(', ')
    
    additional_skills_scores = {skill: calculate_skill_relevance(skill, keywords, vectorizer, job_description) for skill in additional_skills if skill}
    developer_tools_scores = {tool: calculate_skill_relevance(tool, keywords, vectorizer, job_description) for tool in developer_tools if tool}
    languages_scores = {lang: calculate_skill_relevance(lang, keywords, vectorizer, job_description) for lang in languages if lang}
    technologies_scores = {tech: calculate_skill_relevance(tech, keywords, vectorizer, job_description) for tech in technologies if tech}
    
    return {
        'experiences': top_experiences,
        'projects': top_projects,
        'involvements': top_involvements,
        'courseworks': top_courseworks,
        'research': top_research,
        'additional_skills': additional_skills_scores,
        'developer_tools': developer_tools_scores,
        'languages': languages_scores,
        'technologies': technologies_scores
    }


def get_unique_items(items):
    seen = set()
    unique_items = []
    stop_words = set(stopwords.words('english'))

    for item, score in items:
        item_key = None
        
        # Determine the key based on item structure
        if 'company' in item:
            item_key = item['company']
        elif 'title' in item:
            item_key = item['title']
        elif 'group' in item:
            item_key = item['group']
        else:
            item_key = str(item)
        
        # Adjust item_key to consider first 8 characters for flexibility
        if item_key is not None and len(item_key) >= 8:
            item_key_short = item_key[:8]  # Take first 8 characters
        else:
            item_key_short = item_key

        # Convert key to string for hashing
        item_key_short = str(item_key_short)

        # Get non-stopwords from the full item_key
        non_stop_words = [word.lower() for word in item_key.split() if word.lower() not in stop_words]

        # Check if item_key (or first 8 characters) is already seen or if there are 2+ shared non-stopwords
        is_duplicate = False
        for seen_key in seen:
            seen_non_stop_words = [word.lower() for word in seen_key.split() if word.lower() not in stop_words]
            shared_words = set(non_stop_words) & set(seen_non_stop_words)
            if item_key_short == seen_key[:8] or len(shared_words) >= 2:
                is_duplicate = True
                break

        if not is_duplicate:
            seen.add(item_key)
            unique_items.append((item, score))

    return unique_items

def main():
    file_timestamp = ''
    link_timestamp = ''
    
    with open('run_timestamp_file.txt', 'r') as f:
            file_timestamp = f.read().strip()
    with open('run_timestamp_link.txt', 'r') as f:
            link_timestamp = f.read().strip()
    
    resume_dir = os.path.join('parsed_resumes', file_timestamp)
    directory = 'job_postings'
    directory = os.path.join(directory, link_timestamp)
    
    # Check if the directory exists and has files
    if os.path.exists(directory) and os.path.isdir(directory):
        # Get a list of files in the directory with their modification times
        files = [(file, os.path.getmtime(os.path.join(directory, file))) for file in os.listdir(directory)]

        # Sort files by modification time (ascending order)
        files.sort(key=lambda x: x[1])

        # Get the name of the last file (most recently modified)
        if files:
            last_file = files[-1][0]
            print(f"The name of the last file by modification time is: {last_file}")

            # Load job description from the last file
            job_description_path = os.path.join(directory, last_file)
            job_description = load_job_description(job_description_path)
        else:
            print("No files found in the directory.")
    else:
        print(f"Directory '{directory}' does not exist or is not a directory.")
    print(file_timestamp,link_timestamp)

    keywords = extract_keywords(job_description)
    
    vectorizer = TfidfVectorizer()
    vectorizer.fit([job_description])

    def count_uppercase(s):
        return sum(1 for c in s if c.isupper())

    def update_skills(skills_dict, new_skill, new_score):
        lower_skill = new_skill.lower()
        if lower_skill not in skills_dict:
            skills_dict[lower_skill] = (new_skill, new_score)
        else:
            existing_skill, existing_score = skills_dict[lower_skill]
            if count_uppercase(new_skill) > count_uppercase(existing_skill):
                skills_dict[lower_skill] = (new_skill, new_score)
            elif count_uppercase(new_skill) == count_uppercase(existing_skill) and new_score > existing_score:
                skills_dict[lower_skill] = (new_skill, new_score)

    all_results = []
    all_additional_skills = {}
    all_developer_tools = {}
    all_languages = {}
    all_technologies = {}
    all_experiences = []
    all_projects = []
    all_involvements = []
    all_courseworks = []
    all_research = []

    for filename in os.listdir(resume_dir):
        if filename.endswith('.yaml'):
            resume_path = os.path.join(resume_dir, filename)
            resume = load_yaml(resume_path)
            results = process_resume(resume, job_description, keywords, vectorizer)
            all_results.append((filename, results))

            # Update all skill categories
            for skill, score in results['additional_skills'].items():
                update_skills(all_additional_skills, skill, score)
            for tool, score in results['developer_tools'].items():
                update_skills(all_developer_tools, tool, score)
            for language, score in results['languages'].items():
                update_skills(all_languages, language, score)
            for tech, score in results['technologies'].items():
                update_skills(all_technologies, tech, score)

            all_experiences.extend(results['experiences'])
            all_projects.extend(results['projects'])
            all_involvements.extend(results['involvements'])
            all_courseworks.extend(results['courseworks'])
            all_research.extend(results['research'])

    top_additional_skills = sorted(all_additional_skills.values(), key=lambda x: x[1], reverse=True)
    top_developer_tools = sorted(all_developer_tools.values(), key=lambda x: x[1], reverse=True)
    top_languages = sorted(all_languages.values(), key=lambda x: x[1], reverse=True)
    top_technologies = sorted(all_technologies.values(), key=lambda x: x[1], reverse=True)

    top_experiences = get_unique_items(sorted(all_experiences, key=lambda x: x[1], reverse=True))[:4]
    top_projects = get_unique_items(sorted(all_projects, key=lambda x: x[1], reverse=True))[:2]
    top_involvements = get_unique_items(sorted(all_involvements, key=lambda x: x[1], reverse=True))[:3]
    top_courseworks = get_unique_items(sorted(all_courseworks, key=lambda x: x[1], reverse=True))[:4]
    top_research = get_unique_items(sorted(all_research, key=lambda x: x[1], reverse=True))[:1]


    # Write results to files
    with open('resume_analysis.txt', 'w') as f:
        f.write("Top Items Across All Resumes:\n\n")
        
        f.write("Top 4 Experiences:\n")
        for exp, score in top_experiences:
            f.write(f"- {exp['company']}: {exp['title']} (Score: {score:.2f})\n")

        f.write("\nTop 2 Projects:\n")
        for proj, score in top_projects:
            f.write(f"- {proj['title']} (Score: {score:.2f})\n")

        f.write("\nTop 3 Involvements:\n")
        for inv, score in top_involvements:
            f.write(f"- {inv} (Score: {score:.2f})\n")

        f.write("\nTop 4 Courseworks:\n")
        for course, score in top_courseworks:
            f.write(f"- {course} (Score: {score:.2f})\n")

        f.write("\nTop Research:\n")
        for res, score in top_research:
            f.write(f"- {res['description']} (Score: {score:.2f})\n")

        f.write("\nTop Additional Skills:\n")
        f.write(", ".join(skill for skill, score in top_additional_skills))

        f.write("\n\nTop Developer Tools:\n")
        f.write(", ".join(tool for tool, score in top_developer_tools))

        f.write("\n\nTop Languages:\n")
        f.write(", ".join(lang for lang, score in top_languages))

        f.write("\n\nTop Technologies:\n")
        f.write(", ".join(tech for tech, score in top_technologies))

    with open('individual_resume_analysis.txt', 'w') as f:
        f.write("Individual Resume Analysis:\n")
        for filename, results in all_results:
            f.write(f"\n\nAnalysis for {filename}:\n")
            f.write("Top 4 Experiences:\n")
            for exp, score in results['experiences']:
                f.write(f"- {exp['company']}: {exp['title']} (Score: {score:.2f})\n")

            f.write("\nTop 2 Projects:\n")
            for proj, score in results['projects']:
                f.write(f"- {proj['title']} (Score: {score:.2f})\n")

            f.write("\nTop 3 Involvements:\n")
            for inv, score in results['involvements']:
                f.write(f"- {inv} (Score: {score:.2f})\n")

            f.write("\nTop 4 Courseworks:\n")
            for course, score in results['courseworks']:
                f.write(f"- {course} (Score: {score:.2f})\n")

            f.write("\nTop Research:\n")
            for res, score in results['research']:
                f.write(f"- {res['description']} (Score: {score:.2f})\n")

            f.write("\nAdditional Skills:\n")
            for skill, score in sorted(results['additional_skills'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {skill} (Score: {score:.2f})\n")

            f.write("\nDeveloper Tools:\n")
            for tool, score in sorted(results['developer_tools'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {tool} (Score: {score:.2f})\n")

            f.write("\nLanguages:\n")
            for lang, score in sorted(results['languages'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {lang} (Score: {score:.2f})\n")

            f.write("\nTechnologies:\n")
            for tech, score in sorted(results['technologies'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {tech} (Score: {score:.2f})\n")

    print("Analysis complete. Results written to resume_analysis.txt and individual_resume_analysis.txt")

if __name__ == "__main__":
    main()
