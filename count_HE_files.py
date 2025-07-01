import os

def count_files_in_dir(directory):
    try:
        # List all files in the directory
        files = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        return len(files)
    except FileNotFoundError:
        print(f"Directory {directory} not found.")
        return 0

# Directories to check
dirs = ["false_o2_ARM", "true_o2_ARM"]
sum = 0
for dir_name in dirs:
    file_count = count_files_in_dir(dir_name)
    print(f"Number of files in '{dir_name}': {file_count}")
    sum += file_count
print(f"Total number of files in all directories: {sum}")