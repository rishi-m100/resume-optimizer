import os
from pdf2image import convert_from_path
import google.generativeai as genai
import yaml
import shutil
import time
from dotenv import load_dotenv
load_dotenv()
apiKey = os.getenv('API_KEY_NAME')

# Configure the Gemini API
genai.configure(api_key=apiKey)

def clear_directory(directory):
    # Check if the directory exists
    if os.path.exists(directory):
        # Iterate over all files and sub-directories in the directory
        for entry in os.listdir(directory):
            entry_path = os.path.join(directory, entry)
            try:
                if os.path.isfile(entry_path):
                    os.unlink(entry_path)  # Remove file
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)  # Remove directory recursively
            except Exception as e:
                print(f"Failed to delete {entry_path}. Reason: {e}")
    else:
        print(f"Directory '{directory}' does not exist.")


def parse_pdf(file_path):
    try:
        # Convert PDF to images
        images = convert_from_path(file_path)
        
        # Create 'gemini' folder if it doesn't exist
        output_folder = 'gemini'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Extract base file name without extension
        base_file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Process and save each image
        for i, image in enumerate(images):
            image_file = os.path.join(output_folder, f'{base_file_name}_page_{i+1}.png')
            image.save(image_file, 'PNG')
            print(f'Saved {image_file}')
        
        # We'll use the first page of the resume for this example
        first_image_path = os.path.join(output_folder, f'{base_file_name}_page_1.png')
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt
        prompt = """
        Parse this resume image and return the information in the following YAML format:
        It should be in the same order and with no extraneous dashes or tabs/indents. It needs to match this structure and order exactly. 
        Also, make sure the gpa is just the gpa value. Do not include the denominator. 
        For any links you may set it to null in the YAML file. Keep in mind the technologies used for the projects are immediately to the right of the project title.
        Do not omit any keys. Include projects and research. Nothing can be null in the education section. 
        A slash in a heading indicates 1 key. For example x/y: .... - in this case the actual value starts from after the colon. Anything with a colon in it should strictly be ignored as a value passed to any of the YAML keys. This is the most important requirement. For example if you see: Technologies/Frameworks: Numpy, Pandas - you should ignore frameworks. 

        information:
          name: 
          location: 
          phone: 
          email: 
          linkedin: 
          github: 

        education:
          school: 
          gpa: 
          graduation: 
          degree: 
          major: 
          location: 
          relevant-coursework: 'x,y,z'
          involvement: 'x,y,z'

        technical-skills:
          languages: 'x,y,z'
          developer-tools: 'x,y,z'
          technologies: 'x,y,z'
          additional-skills: 'x,y,z'

        experience:
          - company: 
            title: 
            location: 
            dates: 
            description:
              - 

        research:
          - group: 
            dates: 
            description:
              - 

        projects:
          - title: 
            link: 
            date: 
            tech: 
            description:
              - 

        Only standard characters should be used. If a non-standard character is found, replace it with the most similar-looking standard character. 
        A slash in a heading indicates 1 key. For example x/y: .... - in this case the actual value starts from after the colon. Anything with a colon in it should strictly be ignored as a value passed to any of the YAML keys. 
        Ensure all information is accurately extracted from the image and formatted according to this YAML structure. 
        """
        
        # Upload the image and get its identifier
        image = genai.upload_file(path=first_image_path, display_name="resume")
        
        # Generate content
        response = model.generate_content([image, prompt])

        yaml_content = response.candidates[0].content.parts[0].text
        # Remove the first and last lines of the response text
        yaml_lines = yaml_content.split('\n')
        if len(yaml_lines) > 2:
            yaml_lines = yaml_lines[1:-1]
        yaml_content = "\n".join(yaml_lines)

        # print(yaml_content)
        
        yaml_file_path = 'test.yaml'
        with open(yaml_file_path, 'w') as file:
            file.write(yaml_content)

        # Parse the YAML content
        parsed_data = yaml.safe_load(yaml_content)
        clear_directory('backend/gemini')
        return parsed_data
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        clear_directory('backend/gemini')
        return None

def save_as_yaml(data, output_path):
    with open(output_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
