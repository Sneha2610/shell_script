from bs4 import BeautifulSoup

# List of SonarQube supported languages
supported_languages = [
    'ABAP', 'Apex', 'C', 'C#', 'C++', 'COBOL', 'CSS', 'Dart', 'Flex', 'Go', 
    'Groovy', 'HTML', 'Java', 'JavaScript', 'Kotlin', 'Objective-C', 'PHP', 
    'PL/SQL', 'PLI', 'Python', 'RPG', 'Ruby', 'Rust', 'Scala', 'Swift', 
    'T-SQL', 'TypeScript', 'VB.NET', 'VB6', 'XML'
]

# Function to modify the HTML report and add a new table for unsupported languages
def add_unsupported_languages_table(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Locate the main table in the HTML that contains the file type details
    original_table = soup.find('table')

    # Initialize a list for unsupported languages
    unsupported_rows = []

    # Iterate over the existing table rows (skipping the header) to find unsupported languages
    for row in original_table.find_all('tr')[1:]:
        file_type_cell = row.find_all('td')[0]  # Assuming file type is in the first column
        file_type = file_type_cell.text.strip()

        # Check if the language is unsupported
        if file_type not in supported_languages:
            unsupported_rows.append(row)

    # Create a new table for unsupported languages if any exist
    if unsupported_rows:
        # Clone the structure of the original table
        unsupported_table = original_table.clone()
        # Remove the existing rows from the cloned table
        for row in unsupported_table.find_all('tr')[1:]:
            row.decompose()

        # Append rows with unsupported languages to the cloned table
        for unsupported_row in unsupported_rows:
            unsupported_table.append(unsupported_row)

        # Add a heading for unsupported languages
        unsupported_heading = soup.new_tag('h2')
        unsupported_heading.string = 'Unsupported Languages'
        soup.body.append(unsupported_heading)

        # Append the new table to the HTML body
        soup.body.append(unsupported_table)

    # Save the modified HTML with the new table
    with open('modified_cloc_report_with_unsupported.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Modify the HTML report to add the unsupported languages table
add_unsupported_languages_table('sample_cloc_report.html')
