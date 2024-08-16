import re
import tomlkit

def escape_special_characters(line):
    # Escape special characters but avoid double escaping backslashes
    special_characters = r".*+-^$\\?|\[]()"
    escaped_line = re.escape(line)
    
    # Replace double backslashes with a single backslash
    escaped_line = escaped_line.replace(r"\\", r"\\")

    return escaped_line

def generate_toml_from_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Generate regex patterns by escaping special characters
    regex_patterns = [escape_special_characters(line.strip()) for line in lines]

    # Create a TOML document using tomlkit
    doc = tomlkit.document()
    allowlist = tomlkit.table()
    allowlist.add("description", "allowlist pattern")

    # Replace double quotes with triple single quotes in the regex patterns
    allowlist.add("regex", [f"'''{pattern}'''" for pattern in regex_patterns])
    doc.add("allowlist", allowlist)

    # Write the TOML document to a file
    with open(output_file, 'w') as f:
        f.write(tomlkit.dumps(doc))

if __name__ == "__main__":
    input_file = "patterns.txt"
    output_file = "allowlist_pattern.toml"

    generate_toml_from_lines(input_file, output_file)
    print(f"TOML file '{output_file}' generated successfully.")
