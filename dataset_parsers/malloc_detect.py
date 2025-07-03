#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Malloc Parser

This script scans directories named 'problem#_code.c' and looks for 'problem#_code.cpp' 
files inside them, identifying files that contain `malloc` calls.
"""

import os
import re
from typing import List, Tuple, Dict

# No specific problem list - scan all matching directories

def find_malloc_calls(file_content: str) -> List[Tuple[int, str]]:
    """
    Parse C/C++ code content to find calls to the `malloc` function.
    
    Args:
        file_content (str): The content of the C/C++ file.
        
    Returns:
        List[Tuple[int, str]]: A list of tuples, where each tuple contains the
        line number and the line of code where `malloc` was found.
    """
    malloc_calls_found = []
    lines = file_content.split('\n')
    
    # Regex to find 'malloc' as a whole word, followed by optional whitespace and a parenthesis.
    malloc_pattern = re.compile(r'\bmalloc\s*\(')

    for i, line in enumerate(lines):
        # Basic cleaning: remove single-line comments.
        clean_line = re.sub(r'//.*', '', line)
        
        # Search for the malloc pattern in the cleaned line
        if malloc_pattern.search(clean_line):
            # Found a malloc call. Add the line number and the original, stripped line content.
            malloc_calls_found.append((i + 1, line.strip()))
            
    return malloc_calls_found

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

def scan_for_mallocs(base_directory: str) -> Dict[str, Dict[str, any]]:
    """
    Scan the problem directory structure and find malloc calls.
    
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
                
                # The core logic to find malloc calls is called here
                malloc_calls = find_malloc_calls(content)
                
                if malloc_calls:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'malloc_calls': malloc_calls,
                        'directory': problem_dir,
                    }
                    print(f"    -> {os.path.basename(cpp_file)}: {len(malloc_calls)} malloc call(s) found")
                else:
                    print(f"    -> {os.path.basename(cpp_file)}: No malloc calls")
                    
            except Exception as e:
                print(f"    -> Error reading file '{cpp_file}': {e}")
    
    print(f"\nTotal C++ files processed: {files_found}")
    return results

def print_malloc_results(results: Dict[str, Dict[str, any]]) -> None:
    """
    Print the results of the malloc scan in a formatted way.
    
    Args:
        results (Dict[str, Dict[str, any]]): Results from scanning problem files
    """
    if not results:
        print("\n" + "="*70)
        print("No `malloc` calls found in any problem files.")
        print("="*70)
        return
    
    print(f"\n{'='*70}")
    print("MALLOC CALLS FOUND IN PROBLEM DIRECTORIES")
    print(f"{'='*70}")
    
    total_files = len(results)
    total_mallocs = sum(len(data['malloc_calls']) for data in results.values())
    
    print(f"C++ files with malloc calls: {total_files}")
    print(f"Total malloc calls found: {total_mallocs}")
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
            calls = data['malloc_calls']
            directory = data['directory']
            
            print(f"📁 Directory: {directory}")
            print(f"📄 File: {os.path.basename(file_path)}")
            print(f"   Malloc calls found: {len(calls)}")
            
            for line_num, statement in calls:
                display_statement = statement
                if len(statement) > 120:
                    display_statement = statement[:120] + "..."
                print(f"   Line {line_num:4d}: {display_statement}")
            print()
        
        print()

def generate_malloc_summary_report(results: Dict[str, Dict[str, any]], base_directory: str) -> str:
    """
    Generate a summary report of the findings for malloc calls.
    
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
Problems with C++ files containing malloc calls: 0
No malloc calls found in any files.
"""
    
    problems_with_mallocs = {data['problem_number'] for data in results.values()}
    total_mallocs = sum(len(data['malloc_calls']) for data in results.values())
    
    report = f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {len(problem_directories)}
Problems with malloc calls: {len(problems_with_mallocs)}

Analysis:
- Total C++ files with malloc calls: {len(results)}
- Total malloc instances found: {total_mallocs}

Problems containing malloc calls:
{sorted(list(problems_with_mallocs))}
"""
    
    return report

def main():
    """
    Main function to run the problem directory structure parser for malloc.
    """
    directory = input("Enter the base directory path containing problem directories: ").strip()
    
    if not directory:
        directory = "."  # Default to current directory
    
    print(f"\nScanning base directory: {os.path.abspath(directory)}")
    print(f"Looking for directory structure:")
    print(f"  - Directories named: problem#_code.c")
    print(f"  - Files inside: problem#_code.cpp")
    print("-" * 60)
    
    results = scan_for_mallocs(directory)
    print_malloc_results(results)
    
    summary = generate_malloc_summary_report(results, directory)
    print(summary)
    
    if results:
        save_option = input("\nWould you like to save detailed results to a file? (y/n): ").strip().lower()
        if save_option == 'y':
            output_file = "malloc_scan_report.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("MALLOC CALLS REPORT\n")
                    f.write("=" * 70 + "\n")
                    f.write(summary)
                    f.write("\n" + "="*70 + "\nDETAILED RESULTS\n" + "="*70 + "\n\n")
                    
                    # Recreate the detailed printout for the file
                    by_problem = {}
                    for file_path, data in results.items():
                        problem_num = data['problem_number']
                        if problem_num not in by_problem:
                            by_problem[problem_num] = []
                        by_problem[problem_num].append((file_path, data))
                    
                    for problem_num in sorted(by_problem.keys()):
                        f.write(f"🔢 PROBLEM {problem_num}\n")
                        f.write("-" * 50 + "\n")
                        
                        for file_path, data in by_problem[problem_num]:
                            calls = data['malloc_calls']
                            directory_path = data['directory']
                            
                            f.write(f"📁 Directory: {directory_path}\n")
                            f.write(f"📄 File: {os.path.basename(file_path)}\n")
                            f.write(f"   Malloc calls found: {len(calls)}\n")
                            
                            for line_num, statement in calls:
                                f.write(f"   Line {line_num:4d}: {statement}\n")
                            f.write("\n")
                        f.write("\n")
                
                print(f"Detailed report saved to: {os.path.abspath(output_file)}")
            except Exception as e:
                print(f"Error saving file: {e}")
    
    print("\nScan completed!")

if __name__ == "__main__":
    main()