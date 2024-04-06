import json

def generate_html_from_json(json_data):
    html_content = "<html><head><title>JSON to HTML Report</title></head><body>"
    
    # Iterate over JSON data to generate HTML content
    for category, details in json_data.items():
        html_content += f"<h2>{category}</h2>"
        html_content += "<ul>"
        for item in details:
            html_content += f"<li>{item['name']}: {item['severity']}</li>"
        html_content += "</ul>"
    
    html_content += "</body></html>"
    
    return html_content

def main():
    # Load JSON data from file
    with open('models_scan_report.json', 'r') as file:
        json_data = json.load(file)
    
    # Generate HTML content from JSON data
    html_content = generate_html_from_json(json_data)
    
    # Write HTML content to a file
    with open('models_scan_report.html', 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    main()
