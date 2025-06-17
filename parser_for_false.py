import json
import os

def sanitize_filename(filename):
    """Replace / with _ for safe filenames or folder names."""
    return filename.replace('/', '_')

def main(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for element in data:
        if not element.get('success', True):
            file_comment = f"# {element['file']}\n"
            safe_folder = sanitize_filename(element['file'])

            # Create a subfolder for each entry for clarity
            os.makedirs(safe_folder, exist_ok=True)
            # Write input.txt
            with open(os.path.join(safe_folder, 'input.txt'), 'w', encoding='utf-8') as fi:
                fi.write(file_comment)
                fi.write(element.get('input', ''))
            # Write pred.txt
            with open(os.path.join(safe_folder, 'pred.txt'), 'w', encoding='utf-8') as fp:
                fp.write(file_comment)
                fp.write(element.get('pred', ''))
            # Write gd.txt
            with open(os.path.join(safe_folder, 'gd.txt'), 'w', encoding='utf-8') as fg:
                fg.write(file_comment)
                fg.write(element.get('gt', ''))

if __name__ == '__main__':
    # Replace 'input.json' with your actual file name
    main('results_armv8_O2 1.json')
