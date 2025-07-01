#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Combined Parser

This script scans directories to find C++ files containing BOTH nested loops 
and complex if statements, then generates a detailed report in a specific format,
saving it to a 'reports' subdirectory.
"""

import os
import re
from typing import List, Tuple, Dict

# --- Parser for Complex If Statements ---

def find_complex_if_statements(file_content: str) -> List[Tuple[int, str]]:
    """Parse C/C++ code content to find complex if statements with && or ||."""
    complex_if_statements = []
    lines = file_content.split('\n')
    if_pattern = r'\bif\s*\('
    i = 0
    while i < len(lines):
        line = lines[i]
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(('//', '/*')):
            i += 1
            continue
        if re.search(if_pattern, line):
            if_statement, line_start = "", i + 1
            paren_count, statement_started = 0, False
            original_i = i
            while i < len(lines):
                current_line = lines[i]
                if_statement += current_line.strip() + " "
                for char in current_line:
                    if char == '(':
                        paren_count += 1
                        statement_started = True
                    elif char == ')':
                        paren_count -= 1
                if statement_started and paren_count == 0:
                    break
                i += 1
            if ('&&' in if_statement or '||' in if_statement):
                clean_statement = re.sub(r'\s+', ' ', if_statement.strip())
                complex_if_statements.append((line_start, clean_statement))
            i = max(i, original_i + 1)
        else:
            i += 1
    return complex_if_statements

# --- Parser for Nested Loops ---

def _capture_full_loop_statement(lines: List[str], start_line_index: int) -> str:
    """Helper to capture a full for/while statement that may span multiple lines."""
    full_statement, paren_count, statement_started = "", 0, False
    loop_keyword_pattern = re.compile(r'\b(for|while)\b')
    i = start_line_index
    while i < len(lines):
        line = lines[i]
        match = loop_keyword_pattern.search(line)
        line_content = line[match.start():] if not statement_started and match else line
        full_statement += line.strip() + " "
        for char in line_content:
            if char == '(':
                paren_count += 1
                statement_started = True
            elif char == ')':
                paren_count -= 1
        if statement_started and paren_count == 0:
            break
        i += 1
    return re.sub(r'\s+', ' ', full_statement.strip())

def find_nested_loops(file_content: str) -> List[Tuple[int, str]]:
    """Parse C/C++ code content to find nested loops (for, while)."""
    nested_loops_found, scope_stack, pending_loop_scope = [], [], False
    lines = file_content.split('\n')
    loop_pattern = re.compile(r'\b(for|while)\s*\(')
    for i, line in enumerate(lines):
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line or clean_line.startswith(('/*', '*')):
            continue
        if loop_pattern.search(clean_line):
            if 'loop' in scope_stack:
                nested_loops_found.append((i + 1, _capture_full_loop_statement(lines, i)))
            pending_loop_scope = True
        for char in clean_line:
            if char == '{':
                scope_stack.append('loop' if pending_loop_scope else 'other')
                pending_loop_scope = False
            elif char == '}' and scope_stack:
                scope_stack.pop()
        if pending_loop_scope and ';' in clean_line and clean_line.rfind(';') > clean_line.rfind(')'):
            pending_loop_scope = False
    return sorted(list(set(nested_loops_found)))

# --- Directory and File Handling ---

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
    Scan directory structure, finding files with BOTH nested loops AND complex ifs.
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
                nested_loops = find_nested_loops(content)
                complex_ifs = find_complex_if_statements(content)
                if nested_loops and complex_ifs:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'nested_loops': nested_loops,
                        'complex_if_statements': complex_ifs,
                        'directory': problem_dir,
                    }
                    print(f"  -> Match found: {os.path.basename(cpp_file)}")
            except Exception as e:
                print(f"    -> Error reading file '{cpp_file}': {e}")
    
    return results, all_problem_dirs

def generate_and_save_report(
    results: Dict[str, Dict],
    all_problem_dirs: Dict[int, str],
    base_directory: str,
    filepath: str
) -> None:
    """Generates a report, prints it, and saves it to the specified filepath."""
    
    # --- 1. Gather Statistics for Summary ---
    all_dirs_found_nums = set(all_problem_dirs.keys())
    matched_problem_nums = set(data['problem_number'] for data in results.values())
    unmatched_problem_nums = all_dirs_found_nums - matched_problem_nums
    
    total_nested_loops = sum(len(data['nested_loops']) for data in results.values())
    total_complex_ifs = sum(len(data['complex_if_statements']) for data in results.values())

    # --- 2. Build Report String ---
    report_lines = []
    
    report_lines.append("COMBINED ANALYSIS REPORT: NESTED LOOPS & COMPLEX IF STATEMENTS")
    report_lines.append("=" * 70)
    report_lines.append("\n")
    report_lines.append("SUMMARY REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Base directory scanned: {base_directory}")
    report_lines.append(f"Problem directories found: {len(all_dirs_found_nums)}")
    report_lines.append(f"Problems with matches (nested loops AND complex ifs): {len(matched_problem_nums)}")
    report_lines.append("\nDirectory Analysis:")
    report_lines.append(f"- Total C++ files with matches: {len(results)}")
    report_lines.append(f"- Total nested loops found in matched files: {total_nested_loops}")
    report_lines.append(f"- Total complex if statements found in matched files: {total_complex_ifs}")
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
        report_lines.append("No files found that contained both nested loops and complex if statements.")
    else:
        for problem_num in sorted(by_problem.keys()):
            report_lines.append(f"PROBLEM {problem_num}")
            report_lines.append("-" * 50)
            for file_path, data in by_problem[problem_num]:
                report_lines.append(f"Directory: {data['directory']}")
                report_lines.append(f"File: {os.path.basename(file_path)}")
                
                report_lines.append(f"Nested Loops: {len(data['nested_loops'])}")
                for line_num, statement in data['nested_loops']:
                    report_lines.append(f"  Line {line_num:4d}: {statement}")

                report_lines.append(f"Complex If Statements: {len(data['complex_if_statements'])}")
                for line_num, statement in data['complex_if_statements']:
                    report_lines.append(f"  Line {line_num:4d}: {statement}")
                report_lines.append("")
            report_lines.append("")

    full_report = "\n".join(report_lines)

    # --- 3. Print to Console ---
    print("\n" + full_report)

    # --- 4. Save to File ---
    try:
        # Save to the specified filepath (which includes the 'reports' directory)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"\n✅ Report saved successfully to '{os.path.abspath(filepath)}'")
    except IOError as e:
        print(f"\n❌ Error: Could not write to file '{os.path.abspath(filepath)}'. Reason: {e}")

def main():
    """Main function to run the combined parser."""
    directory = input("Enter the base directory path to scan: ").strip() or "."
    
    if not os.path.exists(directory):
        print(f"Error: Base directory '{directory}' not found.")
        return

    print("-" * 80)
    
    # Perform the scan
    results, all_problem_dirs = scan_problem_directory_structure(directory)
    
    # Define the output directory and filename
    report_dir = "reports"
    base_filename = f"{directory}_loop_if_combined_analysis_report.txt"
    
    # Create the reports directory if it doesn't exist
    os.makedirs(report_dir, exist_ok=True)
    
    # Construct the full path for the report file
    output_filepath = os.path.join(report_dir, base_filename)
    
    # Generate, print, and save the report
    generate_and_save_report(results, all_problem_dirs, directory, output_filepath)
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()