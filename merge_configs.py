import tomli
import tomli_w
import os

def merge_configs(base_config_path, repo_config_path, output_path):
    try:
        # Load the base configuration (global config)
        print(f"Loading base configuration from {base_config_path}")
        with open(base_config_path, 'rb') as base_file:
            base_content = base_file.read()
            print("Base configuration content:")
            print(base_content.decode('utf-8'))
            base_config = tomli.loads(base_content.decode('utf-8'))
        
        # Load the repository-specific configuration (allowlist)
        print(f"Loading repository-specific configuration from {repo_config_path}")
        with open(repo_config_path, 'rb') as repo_file:
            repo_content = repo_file.read()
            print("Repository-specific configuration content:")
            print(repo_content.decode('utf-8'))
            repo_config = tomli.loads(repo_content.decode('utf-8'))
        
        # Ensure 'allowlist' key exists in base_config
        if 'allowlist' not in base_config:
            base_config['allowlist'] = {}
        
        # Merge the allowlists
        if 'allowlist' in repo_config:
            if 'paths' in repo_config['allowlist']:
                base_paths = set(base_config['allowlist'].get('paths', []))
                repo_paths = set(repo_config['allowlist'].get('paths', []))
                merged_paths = list(base_paths | repo_paths)
                base_config['allowlist']['paths'] = merged_paths
            
            if 'regexes' in repo_config['allowlist']:
                base_regexes = set(base_config['allowlist'].get('regexes', []))
                repo_regexes = set(repo_config['allowlist'].get('regexes', []))
                merged_regexes = list(base_regexes | repo_regexes)
                base_config['allowlist']['regexes'] = merged_regexes
            
            if 'description' in repo_config['allowlist']:
                base_config['allowlist']['description'] = repo_config['allowlist']['description']
        
        # Save the merged configuration
        with open(output_path, 'w') as output_file:
            tomli_w.dump(base_config, output_file)
        print(f"Configuration merged successfully into {output_path}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except tomli.TOMLDecodeError as e:
        print(f"Error parsing TOML file: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    # Define file paths
    base_config_path = 'rules.toml'
    repo_config_path = 'gitleaks.toml'
    output_path = 'combined_gitleaks.toml'

    # Ensure the files exist before proceeding
    if not os.path.exists(base_config_path):
        print(f"Base config file '{base_config_path}' does not exist.")
        exit(1)
    
    if not os.path.exists(repo_config_path):
        print(f"Repository config file '{repo_config_path}' does not exist.")
        exit(1)

    merge_configs(base_config_path, repo_config_path, output_path)
