import json
from jinja2 import Environment, FileSystemLoader

def load_json_report(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

def render_html_report(data, output_file):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('gitleaks_report_template.html')
    
    rendered_html = template.render(findings=data)
    
    with open(output_file, 'w') as f:
        f.write(rendered_html)

if __name__ == "__main__":
    json_report_path = 'report.json'  # Path to the Gitleaks JSON report
    output_html_path = 'gitleaks_report.html'  # Output HTML file
    data = load_json_report(json_report_path)
    
    render_html_report(data, output_html_path)
    print(f"HTML report generated at {output_html_path}")
