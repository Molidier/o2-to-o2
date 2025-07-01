#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Complex If Statement Parser

This script scans directories named 'problem#_code.c' and looks for 'problem#_code.cpp' 
files inside them, identifying complex if statements with logical operators (&& or ||).
"""

import os
import re
from typing import List, Tuple, Dict, Set

# No specific problem list - scan all matching directories

def find_complex_if_statements(file_content: str) -> List[Tuple[int, str]]:
    """
    Parse C/C++ code content and find complex if statements containing && or ||.
    
    Args:
        file_content (str): The content of the C/C++ file
        
    Returns:
        List[Tuple[int, str]]: List of tuples containing (line_number, if_statement)
    """
    complex_if_statements = []
    lines = file_content.split('\n')
    
    # Pattern to match if statements with && or ||
    if_pattern = r'\bif\s*\('
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip comments and empty lines
        if line.startswith('//') or line.startswith('/*') or not line:
            i += 1
            continue
            
        # Check if line contains start of an if statement
        if re.search(if_pattern, line):
            # Collect the complete if statement (may span multiple lines)
            if_statement = ""
            line_start = i + 1  # Store 1-based line number
            paren_count = 0
            statement_started = False
            
            # Process lines until we find the complete if condition
            while i < len(lines):
                current_line = lines[i].strip()
                
                # Skip comment lines within the if statement
                if current_line.startswith('//') or current_line.startswith('/*'):
                    i += 1
                    continue
                
                if_statement += current_line + " "
                
                # Count parentheses to handle nested conditions
                for char in current_line:
                    if char == '(':
                        paren_count += 1
                        statement_started = True
                    elif char == ')':
                        paren_count -= 1
                
                # If we've closed all parentheses and found the opening brace or semicolon
                if statement_started and paren_count == 0:
                    if '{' in current_line or ';' in current_line:
                        break
                
                i += 1
            
            # Check if the collected if statement contains complex logical operators
            if ('&&' in if_statement or '||' in if_statement):
                # Clean up the statement for better readability
                clean_statement = re.sub(r'\s+', ' ', if_statement.strip())
                complex_if_statements.append((line_start, clean_statement))
        
        i += 1
    
    return complex_if_statements

def get_problem_number_from_dirname(dirname: str) -> int:
    """
    Extract problem number from directory name with format 'problem#_code.c'.
    
    Args:
        dirname (str): The directory name to parse
        
    Returns:
        int: Problem number or -1 if not matching the expected format
    """
    # Pattern to match problem#_code.c directory format
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
    
    # Look for directories in the base directory
    try:
        for item in os.listdir(base_directory):
            item_path = os.path.join(base_directory, item)
            
            # Check if it's a directory
            if os.path.isdir(item_path):
                problem_num = get_problem_number_from_dirname(item)
                
                # Include any directory that matches the pattern
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
            
            # Check if it's a file and matches our expected name
            if os.path.isfile(item_path) and item.lower() == expected_filename.lower():
                cpp_files.append(item_path)
                
            # Also check for any .cpp files in case naming is slightly different
            elif os.path.isfile(item_path) and item.lower().endswith('.cpp'):
                # Check if it contains the problem number
                if f"problem{expected_problem_num}" in item.lower():
                    cpp_files.append(item_path)
                    
    except PermissionError as e:
        print(f"Permission error accessing directory '{problem_dir}': {e}")
    
    return cpp_files

def scan_problem_directory_structure(base_directory: str) -> Dict[str, Dict[str, any]]:
    """
    Scan the problem directory structure and find complex if statements.
    
    Args:
        base_directory (str): The base directory containing problem directories
        
    Returns:
        Dict[str, Dict[str, any]]: Results organized by file path
    """
    results = {}
    
    # Find all problem directories
    problem_directories = find_problem_directories(base_directory)
    
    if not problem_directories:
        print(f"No problem directories found in '{base_directory}'")
        print(f"Looking for directories named: problem#_code.c (where # is any number)")
        return results
    
    print(f"Found {len(problem_directories)} problem directories:")
    for problem_num in sorted(problem_directories.keys()):
        print(f"  - Problem {problem_num}: {problem_directories[problem_num]}")
    
    print(f"\nScanning for C++ files in each directory...")
    
    # Process each problem directory
    files_found = 0
    for problem_num in sorted(problem_directories.keys()):
        problem_dir = problem_directories[problem_num]
        
        # Find C++ files in this directory
        cpp_files = find_cpp_files_in_problem_directory(problem_dir, problem_num)
        
        if not cpp_files:
            print(f"  Problem {problem_num}: No C++ files found in {problem_dir}")
            continue
            
        print(f"  Problem {problem_num}: Found {len(cpp_files)} C++ file(s)")
        files_found += len(cpp_files)
        
        # Process each C++ file
        for cpp_file in cpp_files:
            try:
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                complex_ifs = find_complex_if_statements(content)
                
                if complex_ifs:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'complex_if_statements': complex_ifs,
                        'directory': problem_dir,
                        'file_type': 'C++'
                    }
                    print(f"    -> {os.path.basename(cpp_file)}: {len(complex_ifs)} complex if statement(s) found")
                else:
                    print(f"    -> {os.path.basename(cpp_file)}: No complex if statements")
                    
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
        print("No complex if statements found in any problem files.")
        print("="*70)
        return
    
    print(f"\n{'='*70}")
    print("COMPLEX IF STATEMENTS FOUND IN PROBLEM DIRECTORIES")
    print(f"{'='*70}")
    
    total_files = len(results)
    total_statements = sum(len(data['complex_if_statements']) for data in results.values())
    
    print(f"C++ files with complex if statements: {total_files}")
    print(f"Total complex if statements found: {total_statements}")
    print(f"{'='*70}\n")
    
    # Group results by problem number for better organization
    by_problem = {}
    for file_path, data in results.items():
        problem_num = data['problem_number']
        if problem_num not in by_problem:
            by_problem[problem_num] = []
        by_problem[problem_num].append((file_path, data))
    
    # Print results organized by problem number
    for problem_num in sorted(by_problem.keys()):
        print(f"🔢 PROBLEM {problem_num}")
        print("-" * 50)
        
        for file_path, data in by_problem[problem_num]:
            statements = data['complex_if_statements']
            directory = data['directory']
            
            print(f"📁 Directory: {directory}")
            print(f"📄 File: {os.path.basename(file_path)}")
            print(f"   Complex if statements: {len(statements)}")
            
            for line_num, statement in statements:
                # Truncate very long statements for readability
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
    # Find all problem directories that exist
    problem_directories = find_problem_directories(base_directory)
    
    if not results:
        return f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {len(problem_directories)}
Problems with C++ files containing complex if statements: 0

Directory structure expected:
- Directories named: problem#_code.c (where # is any number)
- Files inside: problem#_code.cpp

No complex if statements found in any files.
"""
    
    # Analyze results
    problems_with_complex_ifs = set()
    total_statements = 0
    
    for file_path, data in results.items():
        problems_with_complex_ifs.add(data['problem_number'])
        total_statements += len(data['complex_if_statements'])
    
    problems_analyzed = len(problems_with_complex_ifs)
    total_directories_found = len(problem_directories)
    problems_in_directories = set(problem_directories.keys())
    
    report = f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {total_directories_found}
Problems with complex if statements: {problems_analyzed}

Directory Analysis:
- Total C++ files processed: {len(results)}
- Complex if statements found: {total_statements}

All problem numbers found:
{sorted(problems_in_directories)}

Problems with complex if statements:
{sorted(problems_with_complex_ifs)}

Problems with directories but no complex if statements:
{sorted(problems_in_directories - problems_with_complex_ifs)}
"""
    
    return report

def main():
    """
    Main function to run the problem directory structure parser.
    """
    # Get directory path from user
    directory = input("Enter the base directory path containing problem directories: ").strip()
    
    if not directory:
        directory = "."  # Current directory if nothing entered
    
    print(f"\nScanning base directory: {os.path.abspath(directory)}")
    print(f"Looking for directory structure:")
    print(f"  - Directories named: problem#_code.c (where # is any number)")
    print(f"  - Files inside: problem#_code.cpp")
    print("-" * 60)
    
    # Scan the directory structure
    results = scan_problem_directory_structure(directory)
    
    # Print detailed results
    print_results(results)
    
    # Print summary
    summary = generate_summary_report(results, directory)
    print(summary)
    
    # Option to save results to file
    if results:
        save_option = input("\nWould you like to save detailed results to a file? (y/n): ").strip().lower()
        if save_option == 'y':
            output_file = f"{directory}_complex_if_report.txt"
            try:
                with open(output_file, 'w') as f:
                    f.write("PROBLEM DIRECTORY STRUCTURE COMPLEX IF STATEMENTS REPORT\n")
                    f.write("=" * 70 + "\n\n")
                    
                    # Write summary first
                    f.write(summary)
                    f.write("\n" + "="*70 + "\n")
                    f.write("DETAILED RESULTS\n")
                    f.write("="*70 + "\n\n")
                    
                    # Group by problem number
                    by_problem = {}
                    for file_path, data in results.items():
                        problem_num = data['problem_number']
                        if problem_num not in by_problem:
                            by_problem[problem_num] = []
                        by_problem[problem_num].append((file_path, data))
                    
                    for problem_num in sorted(by_problem.keys()):
                        f.write(f"PROBLEM {problem_num}\n")
                        f.write("-" * 50 + "\n")
                        
                        for file_path, data in by_problem[problem_num]:
                            f.write(f"Directory: {data['directory']}\n")
                            f.write(f"File: {os.path.basename(file_path)}\n")
                            f.write(f"Complex if statements: {len(data['complex_if_statements'])}\n\n")
                            
                            for line_num, statement in data['complex_if_statements']:
                                f.write(f"Line {line_num:4d}: {statement}\n")
                            f.write("\n")
                        f.write("\n")
                
                print(f"Results saved to: {output_file}")
            except Exception as e:
                print(f"Error saving file: {e}")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()