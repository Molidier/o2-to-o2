import os
import shutil

# --- Configuration ---
SOURCE_ROOT_DIR = 'eval'
DESTINATION_ROOT_DIR = 'false_o2_ARM'

# The specific list of problems to be parsed, as provided.
PROBLEM_LIST = [
    6, 7, 8, 9, 10, 11, 15, 18, 19, 20, 21, 22, 23, 27, 28, 29, 33, 35, 36,
    37, 38, 40, 41, 44, 45, 47, 50, 51, 60, 63, 64, 65, 66, 68, 71, 72, 76,
    77, 81, 82, 85, 86, 87, 89, 90, 91, 92, 93, 96, 99, 101, 105, 106, 107,
    109, 112, 113, 116, 117, 118, 119, 120, 124, 125, 126, 127, 129, 130,
    131, 133, 136, 137, 140, 141, 142, 143, 144, 145, 146, 148, 149, 150,
    152, 154, 156, 158, 159, 161, 162, 163, 164
]

def extract_and_copy_files(problem_indexes):
    """
    Extracts specified problem files and copies them to a new directory structure.

    Args:
        problem_indexes (list): A list of integer indexes for the problems to process.
    """
    # 1. Check if the root destination directory exists. If not, create it.
    if not os.path.exists(DESTINATION_ROOT_DIR):
        print(f"Root destination directory '{DESTINATION_ROOT_DIR}' not found. Creating it.")
        os.makedirs(DESTINATION_ROOT_DIR)

    total_problems = len(problem_indexes)
    print(f"Starting to process {total_problems} specified problems...")

    # 2. Loop through each problem index from the list.
    for i, index in enumerate(problem_indexes):
        try:
            # 3. Construct the full path to the source file.
            # e.g., 'eval/problem6/code.c'
            source_file_path = os.path.join(SOURCE_ROOT_DIR, f'problem{index}', 'code.c')

            # 4. Check if the source file actually exists.
            if not os.path.exists(source_file_path):
                print(f"({i + 1}/{total_problems}) WARNING: Source file not found, skipping: {source_file_path}")
                continue  # Skip to the next index in the list

            # 5. Construct the path for the destination subdirectory.
            # e.g., 'false_o2_ARM/problem6_code.c'
            dest_subdir_name = f'problem{index}_code.c'
            dest_subdir_path = os.path.join(DESTINATION_ROOT_DIR, dest_subdir_name)

            # 6. Create the destination subdirectory. `exist_ok=True` prevents errors
            # if the script is run multiple times.
            os.makedirs(dest_subdir_path, exist_ok=True)
            
            # 7. Construct the final destination file path.
            # As per the pattern from your previous requests, we save it as a .cpp file.
            # e.g., 'false_o2_ARM/problem6_code.c/problem6_code.cpp'
            dest_file_name = f'problem{index}_code.cpp'
            dest_file_path = os.path.join(dest_subdir_path, dest_file_name)

            # 8. Copy the file from source to the final destination path.
            # shutil.copy2 preserves file metadata (like modification time).
            shutil.copy2(source_file_path, dest_file_path)

            # 9. Print a success message for user feedback.
            print(f"({i + 1}/{total_problems}) Successfully created: {dest_file_path}")

        except Exception as e:
            # Catch any other unexpected errors during file operations.
            print(f"({i + 1}/{total_problems}) ERROR: An unexpected error occurred for problem {index}: {e}")

def main():
    """Main function to run the script."""
    extract_and_copy_files(PROBLEM_LIST)

# --- Execution ---
if __name__ == "__main__":
    main()
    print("\nScript finished.")