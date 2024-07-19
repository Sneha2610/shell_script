import toml
import sys

def merge_configs(template_path, allowlist_path, output_path):
    # Load the template configuration
    with open(template_path, 'r') as template_file:
        template_config = toml.load(template_file)
    
    # Load the allowlist configuration
    with open(allowlist_path, 'r') as allowlist_file:
        allowlist_config = toml.load(allowlist_file)
    
    # Merge the allowlist into the template
    if 'allowlist' in allowlist_config:
        template_config['allowlist'] = allowlist_config['allowlist']
    else:
        template_config['allowlist'] = allowlist_config
    
    # Save the merged configuration
    with open(output_path, 'w') as output_file:
        toml.dump(template_config, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_configs.py <template_path> <allowlist_path> <output_path>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    allowlist_path = sys.argv[2]
    output_path = sys.argv[3]

    merge_configs(template_path, allowlist_path, output_path)
