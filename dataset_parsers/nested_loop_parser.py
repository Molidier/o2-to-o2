#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Nested Loop Parser

This script scans directories named 'problem#_code.c' and looks for 'problem#_code.cpp' 
files inside them, identifying files that contain nested loops (e.g., a for-loop inside another for-loop).
"""

import os
import re
from typing import List, Tuple, Dict

# No specific problem list - scan all matching directories

def _capture_full_loop_statement(lines: List[str], start_line_index: int) -> str:
    """
    A helper function to capture a full for/while statement, which may span multiple lines,
    by tracking parentheses.
    
    Args:
        lines (List[str]): All lines of the file content.
        start_line_index (int): The line number where the loop keyword was detected.
        
    Returns:
        str: The cleaned, full loop statement (e.g., "for (int i = 0; i < n; i++)").
    """
    full_statement = ""
    paren_count = 0
    statement_started = False
    
    # Regular expression to find the start of the loop keyword
    loop_keyword_pattern = re.compile(r'\b(for|while)\b')
    
    i = start_line_index
    while i < len(lines):
        line = lines[i]
        
        # On the first line, only start processing from the loop keyword itself
        if not statement_started:
            match = loop_keyword_pattern.search(line)
            if match:
                line_content_to_process = line[match.start():]
            else: # Should not happen if called correctly, but as a safeguard
                line_content_to_process = line
        else:
            line_content_to_process = line

        # Add the stripped line to our statement
        full_statement += line.strip() + " "
        
        # Count parentheses to find the end of the condition
        for char in line_content_to_process:
            if char == '(':
                paren_count += 1
                statement_started = True
            elif char == ')':
                paren_count -= 1
        
        # If we have found the start and all parentheses are now closed, the statement is complete.
        if statement_started and paren_count == 0:
            break
            
        i += 1
        
    # Clean up extra whitespace for a neat output
    return re.sub(r'\s+', ' ', full_statement.strip())


def find_nested_loops(file_content: str) -> List[Tuple[int, str]]:
    """
    Parse C/C++ code content to find nested loops (for, while).
    A loop is considered nested if its declaration appears inside the scope of another loop.
    
    Args:
        file_content (str): The content of the C/C++ file.
        
    Returns:
        List[Tuple[int, str]]: A list of tuples, where each tuple contains the
        line number and the code of the detected inner loop.
    """
    nested_loops_found = []
    lines = file_content.split('\n')
    
    # Stack to track the type of scope we are in ('loop' or 'other').
    scope_stack = []
    
    # Regex to find 'for' or 'while' keywords.
    loop_pattern = re.compile(r'\b(for|while)\s*\(')
    
    # A state flag to link a loop statement to its opening brace '{'.
    pending_loop_scope = False

    for i, line in enumerate(lines):
        # Basic cleaning: remove single-line comments and leading/trailing whitespace.
        clean_line = re.sub(r'//.*', '', line).strip()
        
        # Skip empty lines or lines that are part of a block comment (simple check).
        if not clean_line or clean_line.startswith('/*') or clean_line.startswith('*'):
            continue

        # --- Step 1: Check for a new loop declaration ---
        if loop_pattern.search(clean_line):
            # Check if we are already inside a loop's scope.
            if 'loop' in scope_stack:
                # This is a nested loop!
                full_statement = _capture_full_loop_statement(lines, i)
                nested_loops_found.append((i + 1, full_statement))
            
            # Set the flag that the next '{' we find will open a loop scope.
            pending_loop_scope = True

        # --- Step 2: Track scopes using braces ---
        for char in clean_line:
            if char == '{':
                # If we were expecting a loop's body, this '{' starts it.
                if pending_loop_scope:
                    scope_stack.append('loop')
                    pending_loop_scope = False  # Reset flag
                else:
                    scope_stack.append('other') # It's a non-loop scope (if, function, etc.)
            
            elif char == '}':
                # Exiting a scope, pop from the stack.
                if scope_stack:
                    scope_stack.pop()

        # --- Step 3: Handle single-line loops (e.g., for(...) statement;) ---
        # If a semicolon appears after the loop condition, the loop body is a single
        # statement and cannot contain a nested loop block. So, we reset the flag.
        if pending_loop_scope and ';' in clean_line:
            # Ensure the semicolon is not part of the for-loop condition itself
            # by checking its position relative to the closing parenthesis.
            last_paren = clean_line.rfind(')')
            last_semicolon = clean_line.rfind(';')
            if last_semicolon > last_paren:
                pending_loop_scope = False
                
    # Use set to remove duplicates that might arise from complex formatting
    return sorted(list(set(nested_loops_found)))

def get_problem_number_from_dirname(dirname: str) -> int:
    """
    Extract problem number from directory name with format 'problem#_code.c'.
    
    Args:
        dirname (str): The directory name to parse
        
    Returns:
        int: Problem number or -1 if not matching the expected format
    """
    pattern = r'problem(\d+)_code\.c$'
    match = re.match(pattern, dirname.lower())
    
    if match:
        return int(match.group(1))
    return -1

def find_problem_directories(base_directory: str) -> Dict[int, str]:
    """
    Find all directories named 'problem#_code.c' (any problem number).
    
    Args:
        base_directory (str): The base directory to search in
        
    Returns:
        Dict[int, str]: Dictionary mapping problem numbers to directory paths
    """
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
    """
    Find C++ files in a problem directory, looking for 'problem#_code.cpp'.
    
    Args:
        problem_dir (str): Path to the problem directory
        expected_problem_num (int): Expected problem number
        
    Returns:
        List[str]: List of C++ file paths found
    """
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

def scan_problem_directory_structure(base_directory: str) -> Dict[str, Dict[str, any]]:
    """
    Scan the problem directory structure and find nested loops.
    
    Args:
        base_directory (str): The base directory containing problem directories
        
    Returns:
        Dict[str, Dict[str, any]]: Results organized by file path
    """
    results = {}
    
    problem_directories = find_problem_directories(base_directory)
    
    if not problem_directories:
        print(f"No problem directories found in '{base_directory}'")
        print(f"Looking for directories named: problem#_code.c (where # is any number)")
        return results
    
    print(f"Found {len(problem_directories)} problem directories:")
    for problem_num in sorted(problem_directories.keys()):
        print(f"  - Problem {problem_num}: {problem_directories[problem_num]}")
    
    print(f"\nScanning for C++ files in each directory...")
    
    files_found = 0
    for problem_num in sorted(problem_directories.keys()):
        problem_dir = problem_directories[problem_num]
        
        cpp_files = find_cpp_files_in_problem_directory(problem_dir, problem_num)
        
        if not cpp_files:
            print(f"  Problem {problem_num}: No matching C++ file found in {problem_dir}")
            continue
            
        print(f"  Problem {problem_num}: Found {len(cpp_files)} C++ file(s)")
        files_found += len(cpp_files)
        
        for cpp_file in cpp_files:
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # The core logic is called here
                nested_loops = find_nested_loops(content)
                
                if nested_loops:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'nested_loops': nested_loops,
                        'directory': problem_dir,
                    }
                    print(f"    -> {os.path.basename(cpp_file)}: {len(nested_loops)} nested loop(s) found")
                else:
                    print(f"    -> {os.path.basename(cpp_file)}: No nested loops")
                    
            except Exception as e:
                print(f"    -> Error reading file '{cpp_file}': {e}")
    
    print(f"\nTotal C++ files processed: {files_found}")
    return results

def print_results(results: Dict[str, Dict[str, any]]) -> None:
    """
    Print the results in a formatted way organized by problem number.
    
    Args:
        results (Dict[str, Dict[str, any]]): Results from scanning problem files
    """
    if not results:
        print("\n" + "="*70)
        print("No nested loops found in any problem files.")
        print("="*70)
        return
    
    print(f"\n{'='*70}")
    print("NESTED LOOPS FOUND IN PROBLEM DIRECTORIES")
    print(f"{'='*70}")
    
    total_files = len(results)
    total_loops = sum(len(data['nested_loops']) for data in results.values())
    
    print(f"C++ files with nested loops: {total_files}")
    print(f"Total nested loops found: {total_loops}")
    print(f"{'='*70}\n")
    
    by_problem = {}
    for file_path, data in results.items():
        problem_num = data['problem_number']
        if problem_num not in by_problem:
            by_problem[problem_num] = []
        by_problem[problem_num].append((file_path, data))
    
    for problem_num in sorted(by_problem.keys()):
        print(f"🔢 PROBLEM {problem_num}")
        print("-" * 50)
        
        for file_path, data in by_problem[problem_num]:
            loops = data['nested_loops']
            directory = data['directory']
            
            print(f"📁 Directory: {directory}")
            print(f"📄 File: {os.path.basename(file_path)}")
            print(f"   Nested loops found: {len(loops)}")
            
            for line_num, statement in loops:
                display_statement = statement
                if len(statement) > 120:
                    display_statement = statement[:120] + "..."
                print(f"   Line {line_num:4d}: {display_statement}")
            print()
        
        print()

def generate_summary_report(results: Dict[str, Dict[str, any]], base_directory: str) -> str:
    """
    Generate a summary report of the findings.
    
    Args:
        results (Dict[str, Dict[str, any]]): Results from scanning
        base_directory (str): Base directory that was scanned
        
    Returns:
        str: Summary report text
    """
    problem_directories = find_problem_directories(base_directory)
    
    if not results:
        return f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {len(problem_directories)}
Problems with C++ files containing nested loops: 0
No nested loops found in any files.
"""
    
    problems_with_nested_loops = {data['problem_number'] for data in results.values()}
    total_loops = sum(len(data['nested_loops']) for data in results.values())
    
    report = f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {len(problem_directories)}
Problems with nested loops: {len(problems_with_nested_loops)}

Analysis:
- Total C++ files with nested loops: {len(results)}
- Total nested loop instances found: {total_loops}

Problems containing nested loops:
{sorted(list(problems_with_nested_loops))}
"""
    
    return report

def main():
    """
    Main function to run the problem directory structure parser.
    """
    directory = input("Enter the base directory path containing problem directories: ").strip()
    
    if not directory:
        directory = "."  # Default to current directory
    
    print(f"\nScanning base directory: {os.path.abspath(directory)}")
    print(f"Looking for directory structure:")
    print(f"  - Directories named: problem#_code.c")
    print(f"  - Files inside: problem#_code.cpp")
    print("-" * 60)
    
    results = scan_problem_directory_structure(directory)
    print_results(results)
    
    summary = generate_summary_report(results, directory)
    print(summary)
    
    if results:
        save_option = input("\nWould you like to save detailed results to a file? (y/n): ").strip().lower()
        if save_option == 'y':
            output_file = f"{directory}_nested_loop_report.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("NESTED LOOP REPORT\n")
                    f.write("=" * 70 + "\n")
                    f.write(summary)
                    f.write("\n" + "="*70 + "\nDETAILED RESULTS\n" + "="*70 + "\n\n")
                    
                    # You can reuse the print_results logic to write to the file for detail
                    # This is left as an exercise or can be implemented similarly.
                
                print(f"Summary saved to: {output_file}")
            except Exception as e:
                print(f"Error saving file: {e}")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()