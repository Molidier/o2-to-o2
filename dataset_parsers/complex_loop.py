#!/usr/bin/env python3
"""
Problem Directory Structure C/C++ Loop Parser for Complex Conditions

This script scans directories named 'problem#_code.c' and looks for 'problem#_code.cpp' 
files inside them. It identifies for/while loops that have a complex condition,
defined as a condition containing logical operators '&&' or '||'.
Example: 'while (x > 0 && y < 10)'
"""

import os
import re
from typing import List, Tuple, Dict

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
    
    loop_keyword_pattern = re.compile(r'\b(for|while)\b')
    
    i = start_line_index
    while i < len(lines):
        line = lines[i]
        
        if not statement_started:
            match = loop_keyword_pattern.search(line)
            if match:
                line_content_to_process = line[match.start():]
            else:
                line_content_to_process = line
        else:
            line_content_to_process = line

        full_statement += line.strip() + " "
        
        for char in line_content_to_process:
            if char == '(':
                paren_count += 1
                statement_started = True
            elif char == ')':
                paren_count -= 1
        
        if statement_started and paren_count == 0:
            break
            
        i += 1
        
    return re.sub(r'\s+', ' ', full_statement.strip())


def condition_is_complex(loop_statement: str) -> bool:
    """
    Analyzes a C/C++ loop statement to determine if its condition is complex,
    meaning it contains logical AND ('&&') or logical OR ('||').

    Examples that return True:
    - for (int i = 0; i < n && valid; i++)
    - while ( (x > 0) || (y < 0) )

    Args:
        loop_statement (str): The full loop statement (e.g., "for(...)").

    Returns:
        bool: True if the condition is complex, False otherwise.
    """
    try:
        content_start = loop_statement.index('(') + 1
        content_end = loop_statement.rindex(')')
        content = loop_statement[content_start:content_end]
    except ValueError:
        return False  # Malformed statement

    condition_part = ""
    if loop_statement.lstrip().startswith('for'):
        # For-loops: for(initialization; condition; increment)
        parts = content.split(';')
        if len(parts) == 3:
            condition_part = parts[1]
        elif ':' in content and len(parts) == 1:
             # This is a range-based for loop (e.g., for(auto x : vec)), no condition.
            return False
        else:
            return False # Malformed or no condition part
    elif loop_statement.lstrip().startswith('while'):
        # While-loops: while(condition)
        condition_part = content

    if not condition_part:
        return False

    # The core check: does the condition contain '&&' or '||'?
    if "&&" in condition_part or "||" in condition_part:
        return True

    return False


def find_loops_with_complex_condition(file_content: str) -> List[Tuple[int, str]]:
    """
    Parse C/C++ code to find ANY loop (for, while) where the condition
    is complex (contains '&&' or '||').
    
    Args:
        file_content (str): The content of the C/C++ file.
        
    Returns:
        List[Tuple[int, str]]: A list of tuples, where each tuple contains the
        line number and the code of the detected loop.
    """
    matching_loops = []
    lines = file_content.split('\n')
    loop_pattern = re.compile(r'\b(for|while)\s*\(')

    for i, line in enumerate(lines):
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line or clean_line.startswith('/*') or clean_line.startswith('*'):
            continue

        if loop_pattern.search(clean_line):
            full_statement = _capture_full_loop_statement(lines, i)
            
            # If the loop's condition is complex, we record it.
            if condition_is_complex(full_statement):
                matching_loops.append((i + 1, full_statement))
                
    return sorted(list(set(matching_loops)))


def get_problem_number_from_dirname(dirname: str) -> int:
    """Extract problem number from directory name 'problem#_code.c'."""
    match = re.match(r'problem(\d+)_code\.c$', dirname.lower())
    return int(match.group(1)) if match else -1


def find_problem_directories(base_directory: str) -> Dict[int, str]:
    """Find all directories named 'problem#_code.c'."""
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
    """Find C++ files named 'problem#_code.cpp'."""
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
    """Scan the directory structure to find loops with complex conditions."""
    results = {}
    problem_directories = find_problem_directories(base_directory)
    if not problem_directories:
        print(f"No problem directories found in '{base_directory}'")
        return results
    
    print(f"Found {len(problem_directories)} problem directories. Scanning C++ files...")
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
                
                complex_loops = find_loops_with_complex_condition(content)
                
                if complex_loops:
                    results[cpp_file] = {
                        'problem_number': problem_num,
                        'complex_loops': complex_loops,
                        'directory': problem_dir,
                    }
                    print(f"  -> Problem {problem_num} ({os.path.basename(cpp_file)}): {len(complex_loops)} complex loop(s) found")
                else:
                    print(f"  -> Problem {problem_num} ({os.path.basename(cpp_file)}): No complex loops found")
                    
            except Exception as e:
                print(f"    -> Error reading file '{cpp_file}': {e}")
    
    print(f"\nTotal C++ files processed: {files_found}")
    return results


def print_results(results: Dict[str, Dict[str, any]]) -> None:
    """Print the results in a formatted way."""
    if not results:
        print("\n" + "="*70)
        print("No loops with complex conditions were found in any files.")
        print("="*70)
        return
    
    print(f"\n{'='*80}")
    print("LOOPS WITH COMPLEX CONDITIONS (&& or ||) FOUND")
    print(f"{'='*80}")
    
    total_files = len(results)
    total_loops = sum(len(data['complex_loops']) for data in results.values())
    
    print(f"C++ files with complex loops: {total_files}")
    print(f"Total complex loop instances found: {total_loops}")
    print(f"{'='*80}\n")
    
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
            loops = data['complex_loops']
            print(f"📄 File: {os.path.basename(file_path)}")
            print(f"   Complex loops found: {len(loops)}")
            for line_num, statement in loops:
                display_statement = statement[:120] + "..." if len(statement) > 120 else statement
                print(f"   Line {line_num:4d}: {display_statement}")
            print()
        print()


def generate_summary_report(results: Dict[str, Dict[str, any]], base_directory: str) -> str:
    """Generate a summary report of the findings."""
    problem_directories = find_problem_directories(base_directory)
    if not results:
        return f"SUMMARY REPORT\n{'='*50}\nNo files with complex loops found."
    
    problems_with_complex_loops = {data['problem_number'] for data in results.values()}
    total_loops = sum(len(data['complex_loops']) for data in results.values())
    
    return f"""
SUMMARY REPORT
{'='*50}
Base directory scanned: {base_directory}
Problem directories found: {len(problem_directories)}
Problems with complex loops: {len(problems_with_complex_loops)}

Analysis:
- Total C++ files with complex loops: {len(results)}
- Total complex loop instances found: {total_loops}

Problems containing complex loops:
{sorted(list(problems_with_complex_loops))}
"""


def main():
    """Main function to run the parser."""
    directory = input("Enter the base directory path to scan: ").strip() or "."
    
    print(f"\nScanning base directory: {os.path.abspath(directory)}")
    print("Looking for loops with complex conditions (containing '&&' or '||')...")
    print("-" * 60)
    
    results = scan_problem_directory_structure(directory)
    print_results(results)
    
    summary = generate_summary_report(results, directory)
    print(summary)
    
    if results:
        if input("\nSave detailed results to a file? (y/n): ").strip().lower() == 'y':
            output_file = "complex_loop_report.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    import sys
                    original_stdout, sys.stdout = sys.stdout, f
                    print("COMPLEX LOOP REPORT")
                    print("="*70)
                    print(summary)
                    print("\n" + "="*70 + "\nDETAILED RESULTS\n" + "="*70 + "\n")
                    print_results(results)
                    sys.stdout = original_stdout
                print(f"Detailed report saved to: {os.path.abspath(output_file)}")
            except Exception as e:
                print(f"Error saving file: {e}")
    
    print("\nScan completed!")


if __name__ == "__main__":
    main()