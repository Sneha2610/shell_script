import json
from json2html import json2html

def convert_json_to_html(json_file_path, output_html_path):
    # Load JSON data from file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    
    # Convert JSON to HTML
    html_content = json2html.convert(json = json_data)
    
    # Write HTML content to output file
    with open(output_html_path, 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    # Input and output file paths
    json_file_path = "models_scan_report.json"
    output_html_path = "models_scan_report.html"
    
    # Convert JSON to HTML
    convert_json_to_html(json_file_path, output_html_path)
    print(f"HTML report generated successfully: {output_html_path}")
