from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from pdf_parser import parse_pdf, save_as_yaml
import google.generativeai as genai
import json
import concurrent.futures
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import subprocess
from dotenv import load_dotenv
load_dotenv()
apiKey = os.getenv('API_KEY_NAME')

app = Flask(__name__, static_folder='./build', static_url_path='/')
CORS(app)

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, 'index.html')

ALLOWED_EXTENSIONS = {'pdf'}
genai.configure(api_key=apiKey)
model = genai.GenerativeModel('gemini-1.5-flash')

# Global variable for timestamp
RUN_TIMESTAMP_FILE = None

def generate_timestamp_and_create_directories_file():
    global RUN_TIMESTAMP_FILE
    if RUN_TIMESTAMP_FILE is None:
        RUN_TIMESTAMP_FILE = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Write timestamp to file
        with open('run_timestamp_file.txt', 'w') as f:
            f.write(RUN_TIMESTAMP_FILE)
        
        # Create directories
        for folder in ['uploads', 'parsed_resumes']:
            folder_path = os.path.join(folder, RUN_TIMESTAMP_FILE)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        app.config['UPLOAD_FOLDER'] = os.path.join('uploads', RUN_TIMESTAMP_FILE)

# Global variable for timestamp
RUN_TIMESTAMP_LINK = None

def generate_timestamp_and_create_directories_link():
    global RUN_TIMESTAMP_LINK
    if RUN_TIMESTAMP_LINK is None:
        RUN_TIMESTAMP_LINK = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Write timestamp to file
        with open('run_timestamp_link.txt', 'w') as f:
            f.write(RUN_TIMESTAMP_LINK)
        
        # Create directories
        for folder in ['job_postings']:
            folder_path = os.path.join(folder, RUN_TIMESTAMP_LINK)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        app.config['UPLOAD_FOLDER'] = os.path.join('uploads', RUN_TIMESTAMP_LINK)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        parsed_data = parse_pdf(file_path)
        
        if parsed_data:
            yaml_filename = f"{filename.rsplit('.', 1)[0]}.yaml"
            yaml_path = os.path.join('parsed_resumes', RUN_TIMESTAMP_FILE, yaml_filename)
            save_as_yaml(parsed_data, yaml_path)
            return True
    return False

@app.route('/upload', methods=['POST'])
def upload_files():
    generate_timestamp_and_create_directories_file()
    
    if 'file0' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = [file for key, file in request.files.items() if key.startswith('file')]
    
    if len(files) == 0:
        return jsonify({'error': 'No selected files'}), 400
    
    if len(files) > 5:
        return jsonify({'error': 'Maximum 5 files allowed'}), 400
    
    processed_files = 0
    errors = []

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file_with_delay, file, i): file for i, file in enumerate(files)}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                if result:
                    processed_files += 1
                else:
                    errors.append(f"Failed to process {file.filename}")
            except Exception as exc:
                errors.append(f"{file.filename} generated an exception: {exc}")
    
    if processed_files > 0:
        message = f'Files uploaded and parsed successfully: {processed_files} out of {len(files)}'
        if errors:
            message += f'. Errors: {"; ".join(errors)}'
        return jsonify({
            'message': message,
            'processed_files': processed_files
        }), 200
    else:
        return jsonify({'error': 'Failed to parse any files. ' + '; '.join(errors)}), 500

def process_file_with_delay(file, index):
    result = process_file(file)
    time.sleep(3.5)  # 3.5 seconds delay between files
    return result

@app.route('/scrape-job-posting', methods=['POST'])
def scrape_job_posting():
    generate_timestamp_and_create_directories_link()
    if RUN_TIMESTAMP_LINK is None:
        return jsonify({'error': 'Upload route must be called first to generate timestamp'}), 400

    link = request.json.get('link')
    print("LINK",link)
    if not link:
        return jsonify({'error': 'No link provided'}), 400

    try:
        # Use requests to get the content of the job posting
        import requests
        response = requests.get(link)
        job_posting_content = response.text
        # Prompt for Gemini API
        prompt = f"""
        Analyze the following job posting and extract these key elements:
        1. Job Title
        2. Company Name
        3. Job Description (summarized)
        4. Required Education
        5. Required Skills
        6. Key Responsibilities
        7. Experience Level
        8. Location (if mentioned)
        9. Employment Type (full-time, part-time, contract, internship, etc.)
        10. Top 20 Keywords

        Present the information in a JSON format.

        Job Posting:
        {job_posting_content}
        """

        # Generate response using Gemini API
        response = model.generate_content(prompt)

        content = response.candidates[0].content.parts[0].text
        
        # Remove the first and last lines of the response text
        lines = content.split('\n')
        if len(lines) > 2:
            lines = lines[1:-1]
        content = "\n".join(lines)

        # print(content)

        # Parse the JSON response
        parsed_info = json.loads(content)

        # Prepare the formatted job posting
        formatted_posting = f"""
Job Title: {parsed_info.get('Job Title', 'N/A')}
Company: {parsed_info.get('Company Name', 'N/A')}

Description:
{parsed_info.get('Job Description', 'N/A')}

Education Requirements:
{parsed_info.get('Required Education', 'Not specified')}

Skills:
{', '.join(parsed_info.get('Required Skills', []))}

Key Responsibilities:
{', '.join(parsed_info.get('Key Responsibilities', []))}

Experience Level: {parsed_info.get('Experience Level', 'N/A')}
Location: {parsed_info.get('Location', 'N/A')}
Employment Type: {parsed_info.get('Employment Type', 'N/A')}

Keywords:
{', '.join(parsed_info.get('Top 20 Keywords', []))}
"""

        # Save the formatted job posting
        filename = secure_filename(f"{parsed_info['Company Name']}_{parsed_info['Job Title']}.txt")
        file_path = os.path.join('job_postings', RUN_TIMESTAMP_LINK, filename)
        with open(file_path, 'w') as f:
            f.write(formatted_posting)

        return jsonify({'message': 'Job posting scraped and saved successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to scrape job posting: {str(e)}'}), 500



@app.route('/api/run-model', methods=['POST'])
def run_model():
    try:
        subprocess.run(['python', 'model.py'], check=True)
        return jsonify({'message': 'Model run successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-reconstruct', methods=['POST'])
def run_reconstruct():
    try:
        subprocess.run(['python', 'reconstruct.py'], check=True)
        return jsonify({'message': 'Reconstruct run successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    try:
        subprocess.run(['python', 'scripts/generate_resume.py', '../backend/new_resume.yaml', 'output.tex'], cwd='../resume_generator', check=True)
        pdf_path = '../resume_generator/outputs/output.pdf'
        if os.path.exists(pdf_path):
            return jsonify({'pdfUrl': f'/download-pdf/output.pdf'}), 200
        else:
            return jsonify({'error': 'PDF file not generated'}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-pdf/<filename>')
def download_pdf(filename):
    return send_from_directory('../resume_generator/outputs', filename, as_attachment=True)
    
# Serve static files
@app.route('/static/resume_generator/outputs/<filename>')
def serve_resume(filename):
    return send_from_directory('../resume_generator/outputs', filename)

if __name__ == '__main__':
    app.run(debug=True)


