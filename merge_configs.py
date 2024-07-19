import toml
import sys

def merge_configs(base_config_path, repo_config_path, output_path):
    # Load the base configuration
    with open(base_config_path, 'r') as base_file:
        base_config = toml.load(base_file)
    
    # Load the repository-specific configuration
    with open(repo_config_path, 'r') as repo_file:
        repo_config = toml.load(repo_file)
    
    # Merge the allowlists
    if 'allowlist' in base_config and 'allowlist' in repo_config:
        # Merge paths
        base_config['allowlist']['paths'] = list(set(base_config['allowlist'].get('paths', []) + repo_config['allowlist'].get('paths', [])))
        # Merge regexes
        base_config['allowlist']['regexes'] = list(set(base_config['allowlist'].get('regexes', []) + repo_config['allowlist'].get('regexes', [])))
    elif 'allowlist' in repo_config:
        base_config['allowlist'] = repo_config['allowlist']
    
    # Save the merged configuration
    with open(output_path, 'w') as output_file:
        toml.dump(base_config, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_configs.py <base_config_path> <repo_config_path> <output_path>")
        sys.exit(1)
    
    base_config_path = sys.argv[1]
    repo_config_path = sys.argv[2]
    output_path = sys.argv[3]

    merge_configs(base_config_path, repo_config_path, output_path)
