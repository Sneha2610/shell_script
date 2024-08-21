import re
import toml

def escape_special_characters(line):
    # List of special characters in regex that need to be escaped
    special_characters = r".*+-^$\\?|\[]()"

    # Escape each special character
    escaped_line = re.escape(line)
    
    return escaped_line

def generate_toml_from_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Generate regex patterns by escaping special characters
    regex_patterns = [escape_special_characters(line.strip()) for line in lines]

    # Format regex patterns to be wrapped in double quotes with escaped backslashes
    formatted_patterns = [f'"{pattern}"' for pattern in regex_patterns]

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
