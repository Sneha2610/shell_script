import json

def generate_html_table(cloc_data):
    html = "<table border='1'>\n"
    html += "<tr><th>Language</th><th>Code</th><th>Comments</th><th>Blank</th><th>Total</th></tr>\n"
    
    for lang, stats in cloc_data.items():
        html += f"<tr><td>{lang}</td><td>{stats['code']}</td><td>{stats['comment']}</td><td>{stats['blank']}</td><td>{stats['total']}</td></tr>\n"
    
    html += "</table>"
    return html

def convert_cloc_to_html(json_file, html_file):
    with open(json_file, 'r') as f:
        cloc_data = json.load(f)
    
    html_table = generate_html_table(cloc_data)
    
    with open(html_file, 'w') as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>CLOC Report</title>\n</head>\n<body>\n")
        f.write("<h1>CLOC Report</h1>\n")
        f.write(html_table)
        f.write("\n</body>\n</html>")

if __name__ == "__main__":
    convert_cloc_to_html("cloc_report.json", "cloc_report.html")
