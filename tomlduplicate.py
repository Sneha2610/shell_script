import re

def escape_special_characters(line):
    # Escape special characters for regex and convert single backslashes to double backslashes
    escaped_line = re.escape(line)
    escaped_line = escaped_line.replace("\\", "\\\\")
    return escaped_line

def remove_duplicates(lines):
    # Remove duplicate lines while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            unique_lines.append(line)
            seen.add(line)
    return unique_lines

def generate_toml_from_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Remove duplicates and strip whitespace/newlines
    lines = [line.strip() for line in lines]
    unique_lines = remove_duplicates(lines)

    # Generate regex patterns by escaping special characters
    regex_patterns = [escape_special_characters(line) for line in unique_lines]

    # Format the regex patterns for TOML output using double quotes
    formatted_patterns = [f'"{pattern}"' for pattern in regex_patterns]

    # Manually create the TOML content as a string
    toml_content = "[allowlist]\ndescription = \"allowlist pattern\"\nregex = [\n"
    toml_content += ",\n".join(formatted_patterns)
    toml_content += "\n]"

    # Write to the TOML file
    with open(output_file, 'w') as f:
        f.write(toml_content)

if __name__ == "__main__":
    input_file = "password.txt"  # File containing lines to exclude
    output_file = "allowlist_pattern.toml"  # Output TOML file

    generate_toml_from_lines(input_file, output_file)
    
    print(f"TOML file '{output_file}' generated successfully.")
