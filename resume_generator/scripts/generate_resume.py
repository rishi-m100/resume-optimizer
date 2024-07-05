import yaml
import re
import subprocess
import argparse
import os
import shutil

# Set up argument parser
parser = argparse.ArgumentParser(description='Generate LaTeX resume from YAML data.')
parser.add_argument('yaml_file', help='Path to the YAML data file')
parser.add_argument('output_file', help='Name of the output LaTeX file')
args = parser.parse_args()

# Load the YAML data
with open(args.yaml_file, 'r') as file:
    data = yaml.safe_load(file)

# Read the LaTeX template
with open('templates/template.tex', 'r') as file:
    template = file.read()

def replace_placeholders(template, data, prefix=''):
    if isinstance(data, dict):
        for key, value in data.items():
            template = replace_placeholders(template, value, prefix + key + '.')
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # Check if any required fields are null for experiences or projects
                if 'experience' in prefix:
                    if not all([item.get('company'), item.get('title'), item.get('dates'), item.get('location')]):
                        continue
                elif 'projects' in prefix:
                    if not all([item.get('title'), item.get('date')]):
                        continue
            template = replace_placeholders(template, item, f"{prefix}{i}.")
        # Remove entire sections for non-existent list items
        template = re.sub(r'\\resumeSubheading\s*{{{' + re.escape(prefix) + r'\d+\..*?}}}{.*?}\s*{.*?}{.*?}\s*\\resumeItemListStart.*?\\resumeItemListEnd', '', template, flags=re.DOTALL)
        # Remove individual \resumeItem lines for non-existent list items
        template = re.sub(r'\\resumeItem\{{{' + re.escape(prefix) + r'\d+\..*?}}}\n?', '', template)
    else:
        # Escape special characters for LaTeX
        escaped_value = re.sub(r'([&%$#_{}])', r'\\\1', str(data))
        # Replace placeholders with the escaped value
        placeholder = '{{' + prefix.rstrip('.') + '}}'
        template = re.sub(re.escape(placeholder), escaped_value, template)
    return template

# Perform the replacement
final_content = replace_placeholders(template, data)

# Output the final LaTeX content to a new file
output_tex_file = args.output_file

with open(output_tex_file, 'w') as file:
    file.write(final_content)

print(f"LaTeX content has been generated and written to {output_tex_file}")

# Run pdflatex to generate the PDF
subprocess.run(['pdflatex', f'{output_tex_file}'], check=True)


# Create 'extras' and 'outputs' folders if they don't exist
extras_folder = 'extras'
outputs_folder = 'outputs'
if not os.path.exists(extras_folder):
    os.makedirs(extras_folder)
if not os.path.exists(outputs_folder):
    os.makedirs(outputs_folder)

# Move the PDF to the 'outputs' folder
base_name = os.path.splitext(args.output_file)[0]
output_pdf_file = base_name + '.pdf'

if os.path.exists(output_pdf_file):
    destination = os.path.join(outputs_folder, os.path.basename(output_pdf_file))
    if os.path.exists(destination):
        os.remove(destination)
    shutil.move(output_pdf_file, destination)

# Move all other generated files to the 'extras' folder
base_name = os.path.splitext(output_tex_file)[0]
extensions_to_move = ['.aux', '.log', '.out', '.tex']
for ext in extensions_to_move:
    file_to_move = base_name + ext
    if os.path.exists(file_to_move):
        destination = os.path.join(extras_folder, os.path.basename(file_to_move))
        if os.path.exists(destination):
            os.remove(destination)
        shutil.move(file_to_move, destination)

print(f"Extra files have been moved to the {extras_folder} folder.")
print(f"PDF file has been moved to the {outputs_folder} folder.")