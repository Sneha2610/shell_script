import re

def escape_special_characters(line):
    # Escape only the special characters .*+-^$\\?|\[]()
    special_characters = r".*+-^$\\?|\[]()"
    
    # Use re.escape and then selectively remove escapes we don't want
    escaped_line = re.escape(line)
    
    # Replace escaped curly braces back to normal since they shouldn't be escaped
    escaped_line = escaped_line.replace(r"\{", "{").replace(r"\}", "}")
    
    return escaped_line

def generate_toml_from_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Generate regex patterns by escaping special characters
    regex_patterns = [escape_special_characters(line.strip()) for line in lines]

    # Manually format the TOML content
    toml_content = "[allowlist]\n"
    toml_content += 'description = "allowlist pattern"\n'
    toml_content += "regex = [\n"
    
    # Add each regex pattern with triple single quotes and proper indentation
    for pattern in regex_patterns:
        toml_content += f"    '''{pattern}''',\n"
    
    toml_content += "]\n"

    # Write the formatted TOML content to a file
    with open(output_file, 'w') as f:
        f.write(toml_content)

if __name__ == "__main__":
    input_file = "password.txt"  # Input text file with lines to exclude
    output_file = "allowlist_pattern.toml"  # Output TOML file

    generate_toml_from_lines(input_file, output_file)
    print(f"TOML file '{output_file}' generated successfully.")
