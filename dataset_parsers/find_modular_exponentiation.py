#!/usr/bin/env python3
"""
Standard Assignment Recurrence Parser for C/C++

This script scans directories to find C/C++ files containing standard assignment
recurrence relations (e.g., `x = x + 1;`). It specifically ignores recurrences
that involve memory allocation functions like `malloc` and `realloc`.

The script then generates a detailed report and saves it to a 'reports' subdirectory.
"""

import os
import re
from typing import List, Tuple, Dict

# --- Parser for Standard Assignment Recurrence ---

def find_standard_assignment_recurrences(file_content: str) -> List[Tuple[int, str]]:
    """
    Parse C/C++ code to find standard assignment recurrences.

    This function finds statements of the form `variable = expression_with_variable;`.
    It explicitly ignores lines containing `malloc` or `realloc` to avoid flagging
    memory management patterns.

    Returns:
        A list of tuples, where each tuple contains: (line_number, full_statement)
    """
    found_patterns = []

    # Regex to capture the LHS variable and the entire RHS expression.
    # Handles simple variables, array elements, and member access (e.g., node->next).
    assignment_pattern = re.compile(
        r"""
        ^                                           # Start of the line (or after strip)
        \s*
        ([a-zA-Z_]\w*(?:\[[^\]]+\]|\->\w+|\.\w+)*) # Group 1: Capture the LHS variable.
        \s*
        =                                           # The assignment operator
        \s*
        ([^=].*)                                    # Group 2: Capture RHS, ensuring it's not another assignment like `==`.
        """,
        re.VERBOSE
    )
    
    # Pattern to filter out memory allocation functions.
    mem_alloc_pattern = re.compile(r'\b(m|re)alloc\b')

    lines = file_content.split('\n')
    for i, line in enumerate(lines):
        # Ignore comments and preprocessor directives
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line or clean_line.startswith(('#', '/*', '*')):
            continue

        # --- EXCLUSION RULE: Skip lines with malloc/realloc ---
        if mem_alloc_pattern.search(clean_line):
            continue

        match = assignment_pattern.search(clean_line)
        if match:
            lhs_var, rhs_expr = match.groups()
            
            # The core validation logic:
            # Does the exact LHS variable appear as a whole word on the RHS?
            # `re.escape` handles special chars in variable names (e.g., `arr[i]`).
            # `\b` ensures we match whole words only (e.g., `x` in `x+1`, not `ax+1`).
            recurrence_check_pattern = r'\b' + re.escape(lhs_var) + r'\b'
            if re.search(recurrence_check_pattern, rhs_expr):
                found_patterns.append((i + 1, clean_line))

    return found_patterns


# --- Directory and File Handling (Unchanged) ---

def get_problem_number_from_dirname(dirname: str) -> int:
    """Extract problem number from directory name 'problem#_code.c'."""
    match = re.match(r'problem(\d+)_code\.c$', dirname.lower())
    return int(match.group(1)) if match else -1

def find_problem_directories(base_directory: str) -> Dict[int, str]:
    """Find all directories matching the 'problem#_code.c' pattern."""
    problem_directories = {}
    if not os.path.exists(base_directory):
        return problem_directories
    try:
        for item in os.listdir(base_directory):
            item_path = os.path.join(base_directory, item)
            if os.path.isdir(item_path):
                if (problem_num := get_problem_number_from_dirname(item)) != -1:
                    problem_directories[problem_num] = item_path
    except PermissionError as e:
        print(f"Permission error accessing directory '{base_directory}': {e}")
    return problem_directories

def find_cpp_files_in_problem_directory(problem_dir: str, num: int) -> List[str]:
    """Find C++ files named 'problem#_code.cpp' in a directory."""
    cpp_files, expected_filename = [], f"problem{num}_code.cpp"
    try:
        for item in os.listdir(problem_dir):
            if os.path.isfile(os.path.join(problem_dir, item)) and item.lower() == expected_filename.lower():
                cpp_files.append(os.path.join(problem_dir, item))
    except PermissionError as e:
        print(f"Permission error accessing directory '{problem_dir}': {e}")
    return cpp_files

# --- Main Scanning and Reporting Logic ---

def scan_problem_directory_structure(base_directory: str) -> Tuple[Dict[str, Dict], Dict[int, str]]:
    """
    Scan directory structure, finding files with standard assignment recurrences.
    Returns the results and a dictionary of all problem directories found.
    """
    results = {}
    all_problem_dirs = find_problem_directories(base_directory)

    if not all_problem_dirs:
        print(f"No problem directories found matching pattern 'problem#_code.c' in '{base_directory}'")
        return results, all_problem_dirs

    print(f"Found {len(all_problem_dirs)} problem directories. Scanning for C++ files...")
    for problem_num, problem_dir in all_problem_dirs.items():
        for cpp_file in find_cpp_files_in_problem_directory(problem_dir, problem_num):
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                recurrences = find_standard_assignment_recurrences(content)
                
                if recurrences:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'recurrences': recurrences,
                        'directory': problem_dir,
                    }
                    print(f"  -> Match found (Standard Recurrence): {os.path.basename(cpp_file)}")
            except Exception as e:
                print(f"    -> Error reading file '{cpp_file}': {e}")
    
    return results, all_problem_dirs

def generate_and_save_report(
    results: Dict[str, Dict],
    all_problem_dirs: Dict[int, str],
    base_directory: str,
    filepath: str
) -> None:
    """Generates a report for standard assignment recurrences, prints it, and saves it."""
    
    # --- 1. Gather Statistics for Summary ---
    all_dirs_found_nums = set(all_problem_dirs.keys())
    matched_problem_nums = set(data['problem_number'] for data in results.values())
    unmatched_problem_nums = all_dirs_found_nums - matched_problem_nums
    total_recurrences_found = sum(len(data['recurrences']) for data in results.values())

    # --- 2. Build Report String ---
    report_lines = []
    
    report_lines.append("STANDARD ASSIGNMENT RECURRENCE REPORT")
    report_lines.append("=" * 70)
    report_lines.append("(Excluding lines with malloc/realloc)")
    report_lines.append("\n")
    report_lines.append("SUMMARY REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Base directory scanned: {os.path.abspath(base_directory)}")
    report_lines.append(f"Problem directories found: {len(all_dirs_found_nums)}")
    report_lines.append(f"Problems with matches (standard recurrences): {len(matched_problem_nums)}")
    report_lines.append("\nAnalysis of Matched Files:")
    report_lines.append(f"- Total C++ files with matches: {len(results)}")
    report_lines.append(f"- Total standard assignment recurrences found: {total_recurrences_found}")
    report_lines.append(f"\nAll problem directories found:\n{sorted(list(all_dirs_found_nums))}")
    report_lines.append(f"\nProblems with matches:\n{sorted(list(matched_problem_nums))}")
    report_lines.append(f"\nProblems with directories but no matches:\n{sorted(list(unmatched_problem_nums))}")
    report_lines.append("\n")
    report_lines.append("=" * 70)
    report_lines.append("DETAILED RESULTS")
    report_lines.append("=" * 70)
    report_lines.append("\n")

    by_problem = {}
    for file_path, data in results.items():
        by_problem.setdefault(data['problem_number'], []).append((file_path, data))

    if not by_problem:
        report_lines.append("No files found containing a standard assignment recurrence.")
    else:
        for problem_num in sorted(by_problem.keys()):
            report_lines.append(f"PROBLEM {problem_num}")
            report_lines.append("-" * 50)
            for file_path, data in by_problem[problem_num]:
                report_lines.append(f"Directory: {data['directory']}")
                report_lines.append(f"File: {os.path.basename(file_path)}")
                
                patterns = data['recurrences']
                report_lines.append(f"Standard Recurrences Found: {len(patterns)}")
                for line_num, statement in patterns:
                    report_lines.append(f"  Line {line_num:4d}: {statement}")
                report_lines.append("")
            report_lines.append("")

    full_report = "\n".join(report_lines)

    # --- 3. Print to Console ---
    print("\n" + full_report)

    # --- 4. Save to File ---
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"\n✅ Report saved successfully to '{os.path.abspath(filepath)}'")
    except IOError as e:
        print(f"\n❌ Error: Could not write to file '{os.path.abspath(filepath)}'. Reason: {e}")

def main():
    """Main function to run the standard assignment recurrence parser."""
    directory = input("Enter the base directory path to scan: ").strip() or "."
    
    if not os.path.exists(directory):
        print(f"Error: Base directory '{directory}' not found.")
        return

    print("-" * 80)
    
    # Perform the scan
    results, all_problem_dirs = scan_problem_directory_structure(directory)
    
    # Define the output directory and filename
    report_dir = "a_reports"
    sanitized_dir_name = re.sub(r'[\\/*?:"<>|]', "_", os.path.basename(os.path.abspath(directory)))
    base_filename = f"{sanitized_dir_name}_standard_recurrence_analysis_report.txt"
    
    # Construct the full path for the report file
    output_filepath = os.path.join(report_dir, base_filename)
    
    # Generate, print, and save the report
    generate_and_save_report(results, all_problem_dirs, directory, output_filepath)
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()