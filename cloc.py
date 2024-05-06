import json

def generate_html_table(cloc_data):
    html = "<!DOCTYPE html>\n<html>\n<head>\n<title>CLOC Report</title>\n<style>\n"
    html += "    body {\n"
    html += "        font-family: Arial, sans-serif;\n"
    html += "    }\n"
    html += "    h1 {\n"
    html += "        color: #333;\n"
    html += "        text-align: center;\n"
    html += "    }\n"
    html += "    table {\n"
    html += "        border-collapse: collapse;\n"
    html += "        width: 100%;\n"
    html += "    }\n"
    html += "    th, td {\n"
    html += "        border: 1px solid #ddd;\n"
    html += "        padding: 8px;\n"
    html += "        text-align: center;\n"
    html += "    }\n"
    html += "    th {\n"
    html += "        background-color: #4CAF50;\n"
    html += "        color: white;\n"
    html += "    }\n"
    html += "    tr:nth-child(even) {\n"
    html += "        background-color: #f9f9f9;\n"
    html += "    }\n"
    html += "    tr:hover {\n"
    html += "        background-color: #f2f2f2;\n"
    html += "    }\n"
    html += "    td:first-child {\n"
    html += "        font-weight: bold;\n"
    html += "    }\n"
    html += "</style>\n</head>\n<body>\n"
    html += "<h1>CLOC Report</h1>\n<table>\n"
    html += "<tr><th>Language</th><th>Code</th><th>Comments</th><th>Blank</th><th>Total</th><th>Files</th></tr>\n"
    
    for lang, stats in cloc_data.items():
        html += f"<tr><td>{lang}</td><td>{stats.get('code', 0)}</td><td>{stats.get('comment', 0)}</td><td>{stats.get('blank', 0)}</td><td>{stats.get('code', 0) + stats.get('comment', 0) + stats.get('blank', 0)}</td><td>{stats.get('nFiles', 0)}</td></tr>\n"
    
    html += "</table>\n</body>\n</html>"
    return html

def convert_cloc_to_html(json_file, html_file):
    with open(json_file, 'r') as f:
        cloc_data = json.load(f)
    
    html_content = generate_html_table(cloc_data)
    
    with open(html_file, 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    convert_cloc_to_html("cloc_report.json", "cloc_report.html")
