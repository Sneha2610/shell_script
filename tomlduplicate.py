import re
import toml

def escape_special_characters(line):
    # List of special characters in regex that need to be escaped
    special_characters = r".*+-^$\\?|\[]()"

    # Escape each special character in the line
    escaped_line = re.escape(line)
    
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

    # Format the regex patterns for TOML output
    formatted_patterns = [f"'''{pattern}'''" for pattern in regex_patterns]

    # Create a TOML structure
    data = {
        "allowlist": {
            "description": "allowlist pattern",
            "regex": formatted_patterns
        }
    }

    # Write to a TOML file
    with open(output_file, 'w') as f:
        toml.dump(data, f)

if __name__ == "__main__":
    input_file = "patterns.txt"  # File containing lines to exclude
    output_file = "allowlist_pattern.toml"  # Output TOML file

    generate_toml_from_lines(input_file, output_file)
    
    print(f"TOML file '{output_file}' generated successfully.")
