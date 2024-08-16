import re
import tomli_w

def escape_special_characters(line):
    special_characters = r".*+-^$\\?|\[]()"
    escaped_line = re.escape(line)
    return escaped_line

def generate_toml_from_lines(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    regex_patterns = [escape_special_characters(line.strip()) for line in lines]

    data = {
        "allowlist": {
            "description": "allowlist pattern",
            "regex": regex_patterns
        }
    }

    with open(output_file, 'wb') as f:
        tomli_w.dump(data, f)

if __name__ == "__main__":
    input_file = "patterns.txt"
    output_file = "allowlist_pattern.toml"

    generate_toml_from_lines(input_file, output_file)
    print(f"TOML file '{output_file}' generated successfully.")
