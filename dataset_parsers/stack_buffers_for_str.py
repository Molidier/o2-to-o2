#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Unsafe String Operation Parser

This script scans directories named 'problem#_code.c' and looks for 'problem#_code.cpp' 
files inside them. It identifies files that use potentially unsafe C-style string functions
(like strcpy, strcat, sprintf) on fixed-size stack buffers.
"""

import os
import re
from typing import List, Tuple, Dict

# List of unsafe C-style string functions to search for.
# 'gets' is extremely unsafe, sprintf is often misused.
UNSAFE_STRING_FUNCTIONS = ['strcpy', 'strcat', 'strncat', 'sprintf', 'gets']

def _extract_first_arg_name(line: str, match_start_index: int) -> str:
    """
    A helper to extract the variable name of the first argument from a function call.
    It's a simple parser, not a full AST builder.
    
    Args:
        line (str): The full line of code containing the function call.
        match_start_index (int): The starting index of the function name match.
        
    Returns:
        str: The extracted variable name, or an empty string if it can't be found.
    """
    try:
        # Find the opening parenthesis of the function call
        open_paren_index = line.index('(', match_start_index)
        
        # The content of the arguments
        arg_content = line[open_paren_index + 1:]
        
        # Simple parenthesis balancing to find the end of the argument list
        paren_level = 1
        end_paren_index = -1
        for i, char in enumerate(arg_content):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            if paren_level == 0:
                end_paren_index = i
                break
        
        if end_paren_index != -1:
            arg_content = arg_content[:end_paren_index]

        # The first argument is the string before the first comma
        first_arg = arg_content.split(',')[0].strip()
        
        # Clean up common C-style casting and address-of operators to get the root variable name
        # e.g., "(char*) &buffer" -> "buffer"
        cleaned_name = re.sub(r'[\(\)\[\]\*&]', ' ', first_arg).strip()
        
        # If there are multiple parts (like "struct.member"), take the last part for simplicity,
        # although a more advanced check might be needed for complex cases.
        return cleaned_name.split()[-1] if cleaned_name else ""
        
    except (ValueError, IndexError):
        return ""


def find_unsafe_string_operations(file_content: str) -> List[Tuple[int, str]]:
    """
    Parses C/C++ code to find unsafe string functions used on stack-allocated buffers.
    
    This uses a heuristic:
    1. Find a call to an unsafe function (strcpy, etc.).
    2. Extract the name of the destination buffer (first argument).
    3. Search the code *above* the function call for a stack-based declaration
       of that buffer (e.g., `char buffer[SIZE];`).
       
    Args:
        file_content (str): The content of the C/C++ file.
        
    Returns:
        List[Tuple[int, str]]: A list of tuples, where each tuple contains the
        line number and the line of code with the potential vulnerability.
    """
    vulnerabilities_found = []
    lines = file_content.split('\n')
    
    # Regex to find any of the specified unsafe functions as whole words.
    unsafe_pattern_str = r'\b(' + '|'.join(UNSAFE_STRING_FUNCTIONS) + r')\s*\('
    unsafe_pattern = re.compile(unsafe_pattern_str)

    for i, line in enumerate(lines):
        # Remove comments to avoid false positives
        clean_line = re.sub(r'//.*', '', line)
        if '/*' in clean_line: # Simple block comment check
            clean_line = clean_line.split('/*')[0]

        for match in unsafe_pattern.finditer(clean_line):
            # We found a potentially unsafe function call.
            # Now, let's find out if its destination is a stack buffer.
            
            dest_var_name = _extract_first_arg_name(clean_line, match.start())
            
            if not dest_var_name:
                continue # Couldn't parse the argument, skip.

            # Heuristic: Search all *previous* lines for a stack array declaration of this variable.
            # This is not perfect (scope isn't considered), but it's a strong indicator.
            previous_code = "\n".join(lines[:i])
            
            # Regex to find a declaration like: char var_name[...]; or wchar_t var_name[...]
            declaration_pattern = re.compile(
                r'\b(char|wchar_t)\s+' + re.escape(dest_var_name) + r'\s*\[')

            if declaration_pattern.search(previous_code):
                # We found it! The variable was likely declared as a C-style array on the stack.
                # This is a potential buffer overflow vulnerability.
                vulnerabilities_found.append((i + 1, line.strip()))
                # Break from the inner loop to not double-count if a line has multiple calls
                break

    return sorted(list(set(vulnerabilities_found)))


def get_problem_number_from_dirname(dirname: str) -> int:
    pattern = r'problem(\d+)_code\.c$'
    match = re.match(pattern, dirname.lower())
    return int(match.group(1)) if match else -1


def find_problem_directories(base_directory: str) -> Dict[int, str]:
    problem_directories = {}
    if not os.path.exists(base_directory):
        print(f"Error: Directory '{base_directory}' does not exist.")
        return problem_directories
    try:
        for item in os.listdir(base_directory):
            item_path = os.path.join(base_directory, item)
            if os.path.isdir(item_path):
                problem_num = get_problem_number_from_dirname(item)
                if problem_num != -1:
                    problem_directories[problem_num] = item_path
    except PermissionError as e:
        print(f"Permission error accessing directory '{base_directory}': {e}")
    return problem_directories


def find_cpp_files_in_problem_directory(problem_dir: str, expected_problem_num: int) -> List[str]:
    cpp_files = []
    expected_filename = f"problem{expected_problem_num}_code.cpp"
    try:
        for item in os.listdir(problem_dir):
            item_path = os.path.join(problem_dir, item)
            if os.path.isfile(item_path) and item.lower() == expected_filename.lower():
                cpp_files.append(item_path)
    except PermissionError as e:
        print(f"Permission error accessing directory '{problem_dir}': {e}")
    return cpp_files


def scan_for_unsafe_string_ops(base_directory: str) -> Dict[str, Dict[str, any]]:
    results = {}
    problem_directories = find_problem_directories(base_directory)
    if not problem_directories:
        print(f"No problem directories found in '{base_directory}' matching pattern 'problem#_code.c'")
        return results

    print(f"Found {len(problem_directories)} problem directories. Scanning for C++ files...")
    files_found = 0
    for problem_num in sorted(problem_directories.keys()):
        problem_dir = problem_directories[problem_num]
        cpp_files = find_cpp_files_in_problem_directory(problem_dir, problem_num)
        
        if not cpp_files:
            continue
            
        files_found += len(cpp_files)
        for cpp_file in cpp_files:
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                vulnerabilities = find_unsafe_string_operations(content)
                
                if vulnerabilities:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'unsafe_operations': vulnerabilities,
                        'directory': problem_dir,
                    }
                    print(f"  Problem {problem_num}: {os.path.basename(cpp_file)} -> {len(vulnerabilities)} potential vulnerability(s) found.")
                else:
                    print(f"  Problem {problem_num}: {os.path.basename(cpp_file)} -> Clean.")
            except Exception as e:
                print(f"    -> Error reading or parsing file '{cpp_file}': {e}")
    
    print(f"\nTotal C++ files processed: {files_found}")
    return results


def print_results(results: Dict[str, Dict[str, any]]) -> None:
    if not results:
        print("\n" + "="*70)
        print("No potential unsafe string operations on stack buffers were found.")
        print("="*70)
        return
    
    print(f"\n{'='*70}")
    print("POTENTIAL UNSAFE STRING OPERATIONS FOUND")
    print("Scanned for:", ', '.join(UNSAFE_STRING_FUNCTIONS))
    print(f"{'='*70}")
    
    total_files = len(results)
    total_issues = sum(len(data['unsafe_operations']) for data in results.values())
    
    print(f"Files with potential issues: {total_files}")
    print(f"Total instances found: {total_issues}")
    print(f"{'='*70}\n")
    
    # Group results by problem number for organized output
    by_problem = {}
    for file_path, data in results.items():
        prob_num = data['problem_number']
        if prob_num not in by_problem:
            by_problem[prob_num] = []
        by_problem[prob_num].append((file_path, data))
    
    for problem_num in sorted(by_problem.keys()):
        print(f"🔢 PROBLEM {problem_num}")
        print("-" * 50)
        for file_path, data in by_problem[problem_num]:
            operations = data['unsafe_operations']
            print(f"📄 File: {os.path.basename(file_path)} (in {os.path.basename(data['directory'])})")
            print(f"   Potential issues found: {len(operations)}")
            for line_num, statement in operations:
                display_statement = statement[:120] + "..." if len(statement) > 120 else statement
                print(f"   Line {line_num:4d}: {display_statement}")
            print()
        print()


def main():
    """
    Main function to run the vulnerability scanner.
    """
    directory = input("Enter the base directory path to scan: ").strip()
    if not directory:
        directory = "."  # Default to current directory
    
    print(f"\nScanning base directory: {os.path.abspath(directory)}")
    print("-" * 60)
    
    results = scan_for_unsafe_string_ops(directory)
    print_results(results)
    
    if results:
        save_option = input("\nSave detailed report to 'unsafe_operations_report.txt'? (y/n): ").strip().lower()
        if save_option == 'y':
            output_file = "unsafe_operations_report.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Rerunning print logic but directing to file
                    f.write("UNSAFE STRING OPERATIONS REPORT\n")
                    f.write("=" * 70 + "\n")
                    f.write(f"Scanned for: {', '.join(UNSAFE_STRING_FUNCTIONS)} on stack buffers.\n")
                    f.write("NOTE: This is a heuristic scan. All findings should be manually verified.\n")
                    f.write("=" * 70 + "\n\n")

                    by_problem = {}
                    for file_path, data in results.items():
                        prob_num = data['problem_number']
                        if prob_num not in by_problem:
                            by_problem[prob_num] = []
                        by_problem[prob_num].append((file_path, data))

                    for problem_num in sorted(by_problem.keys()):
                        f.write(f"🔢 PROBLEM {problem_num}\n")
                        f.write("-" * 50 + "\n")
                        for file_path, data in by_problem[problem_num]:
                            operations = data['unsafe_operations']
                            f.write(f"📄 File: {file_path}\n")
                            for line_num, statement in operations:
                                f.write(f"   Line {line_num:4d}: {statement}\n")
                            f.write("\n")
                        f.write("\n")
                
                print(f"Detailed report saved to: {os.path.abspath(output_file)}")
            except Exception as e:
                print(f"Error saving file: {e}")
    
    print("\nScan completed!")


if __name__ == "__main__":
    main()