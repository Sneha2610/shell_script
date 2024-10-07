from bs4 import BeautifulSoup

# List of SonarQube supported languages
supported_languages = [
    'ABAP', 'Apex', 'C', 'C#', 'C++', 'COBOL', 'CSS', 'Dart', 'Flex', 'Go', 
    'Groovy', 'HTML', 'Java', 'JavaScript', 'Kotlin', 'Objective-C', 'PHP', 
    'PL/SQL', 'PLI', 'Python', 'RPG', 'Ruby', 'Rust', 'Scala', 'Swift', 
    'T-SQL', 'TypeScript', 'VB.NET', 'VB6', 'XML'
]

# Function to modify the HTML report
def modify_html_report(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Locate the table in the HTML that contains the file type details
    table = soup.find('table')
    
    # Add a new header for the "Unsupported Language" column
    if table:
        header_row = table.find('tr')  # First row is usually the header
        new_header = soup.new_tag('th')
        new_header.string = 'Unsupported Language'
        header_row.append(new_header)

        # Iterate over the table rows (skipping the header) to add the new column
        for row in table.find_all('tr')[1:]:
            file_type_cell = row.find_all('td')[0]  # Assuming file type is in the first column
            file_type = file_type_cell.text.strip()

            # Check if the language is supported
            unsupported = "Yes" if file_type not in supported_languages else "No"

            # Create a new cell for "Unsupported Language" and append it
            new_cell = soup.new_tag('td')
            new_cell.string = unsupported
            row.append(new_cell)

    # Save the modified HTML
    with open('modified_cloc_report.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Modify the HTML report
modify_html_report('cloc_report.html')
