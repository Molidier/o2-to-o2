#!/usr/bin/env python3
"""
X86 Assembly LEA/LEAL/LEAQ Instruction Detector
Searches for directories containing input.txt files with `lea`, `leal`, or `leaq` instructions.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def detect_lea_family_instructions(content):
    """
    Detects `lea` (Intel syntax) and `leal`/`leaq` (AT&T syntax) instructions
    in x86 assembly code.
    
    Args:
        content (str): The content of the input.txt file.
        
    Returns:
        list: A list of tuples, where each tuple contains the 
              line number and the full line of a matched instruction.
    """
    matches = []
    lines = content.split('\n')
    
    # A case-insensitive pattern to match lines starting with "lea", "leal", or "leaq".
    # This covers the generic instruction and its size-specific variants in AT&T syntax.
    # `leal` is for 32-bit addresses, `leaq` is for 64-bit addresses.
    lea_family_pattern = re.compile(r'^\s*(lea|leal|leaq)\s+', re.IGNORECASE)
    
    for i, line in enumerate(lines, 1):
        # We strip the line to handle leading whitespace correctly
        line_stripped = line.strip()
        if lea_family_pattern.match(line_stripped):
            matches.append((i, line_stripped))
            
    return matches


def analyze_directory(dir_path):
    """
    Analyzes a single directory for an input.txt file and searches for LEA-family instructions.
    
    Args:
        dir_path (Path): The path to the directory to analyze.
        
    Returns:
        dict: Analysis results if LEA-family instructions are found, otherwise None.
    """
    input_file = dir_path / 'input.txt'
    
    if not input_file.exists():
        return None
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return None
    
    # Find all LEA, LEAL, or LEAQ instructions in the content
    matches = detect_lea_family_instructions(content)
    
    if not matches:
        return None
    
    # Extract the first number from the directory name to use as a problem number
    problem_number_match = re.search(r'\d+', dir_path.name)
    problem_number = int(problem_number_match.group(0)) if problem_number_match else None
    
    # If matches are found, prepare the results dictionary
    return {
        'directory': str(dir_path),
        'problem_number': problem_number,
        'input_file': str(input_file),
        'matches': matches,
        'match_count': len(matches)
    }


def scan_directories(root_path):
    """
    Scans all subdirectories in the given path for input.txt files with LEA-family instructions.
    
    Args:
        root_path (str): The root path to start the scan from.
        
    Returns:
        list: A list of analysis result dictionaries for directories where matches were found.
    """
    root = Path(root_path)
    results = []
    
    if not root.exists():
        print(f"Error: Path '{root_path}' does not exist.")
        return results
    
    print(f"Scanning directories in: {root}")
    print("Looking for input.txt files with LEA, LEAL, or LEAQ instructions...\n")
    
    # Use rglob to recursively find all subdirectories
    for dir_path in root.rglob('*'):
        if dir_path.is_dir():
            result = analyze_directory(dir_path)
            if result:
                results.append(result)
                print(f"✓ Found LEA-family instructions in: {dir_path}")
    
    return results


def save_results(results, problem_numbers, output_file):
    """
    Saves the detection results to a text file.
    
    Args:
        results (list): A sorted list of analysis result dictionaries.
        problem_numbers (list): A sorted list of problem numbers found.
        output_file (Path): The path object for the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the list of problem numbers at the very top of the report
        f.write(f"{problem_numbers}\n")
        
        f.write("X86 Assembly LEA/LEAL/LEAQ Instruction Detection Results\n")
        f.write("=" * 60 + "\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total directories with matching instructions found: {len(results)}\n\n")
        
        f.write("Pattern Description:\n")
        f.write("Looking for `lea` (Load Effective Address) instructions and their\n")
        f.write("size-specific variants `leal` (32-bit) and `leaq` (64-bit).\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"[{i}] Directory: {result['directory']}\n")
            f.write(f"    Input file: {result['input_file']}\n")
            f.write(f"    Total matching instructions found: {result['match_count']}\n")
            f.write("    Instructions found:\n")
            
            for line_num, instruction in result['matches']:
                f.write(f"      Line {line_num}: {instruction}\n")
            f.write("\n")


def print_results(results):
    """
    Prints a summary of the detection results to the console.
    
    Args:
        results (list): A list of analysis result dictionaries.
    """
    print(f"\n{'='*70}")
    print("SCAN RESULTS - LEA/LEAL/LEAQ Instruction Detection")
    print(f"{'='*70}")
    
    if not results:
        print("No directories found containing input.txt with LEA, LEAL, or LEAQ instructions.")
        return
        
    print(f"Total directories with matching instructions: {len(results)}\n")
    
    for i, result in enumerate(results, 1):
        print(f"[{i}] {result['directory']}")
        print(f"    • Matching instructions found: {result['match_count']}")
        # Optionally, show the first few found instructions for a quick look
        print("    • Examples:")
        for line_num, instruction in result['matches'][:5]:
            print(f"      Line {line_num}: {instruction}")
        if result['match_count'] > 5:
            print(f"      ... and {result['match_count'] - 5} more.")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Detect x86 assembly LEA, LEAL, or LEAQ instructions in input.txt files."
    )
    parser.add_argument(
        "path", 
        help="Root path to scan for directories containing input.txt files."
    )
    parser.add_argument(
        "-o", "--output", 
        default="lea_family_report.txt",
        help="Output file name (default: lea_family_report.txt)"
    )
    
    args = parser.parse_args()
    
    # Scan directories for LEA-family instructions
    results = scan_directories(args.path)
    
    if not results:
        print("\nNo directories found containing input.txt with LEA, LEAL, or LEAQ instructions.")
        return

    # Sort results based on the extracted problem number for consistent ordering.
    # Put directories without a number at the end.
    results.sort(key=lambda r: r.get('problem_number') if r.get('problem_number') is not None else float('inf'))

    # Extract a sorted list of unique problem numbers from the results
    problem_numbers = sorted(list(set(
        r['problem_number'] for r in results if r.get('problem_number') is not None
    )))
    
    # Print a summary to the console
    print_results(results)
    
    # Define the output directory and create it if it doesn't exist
    output_dir = Path("a_reports")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / args.output

    # Save the detailed results to a file
    if results:
        save_results(results, problem_numbers, output_path)
        print(f"\nDetailed report saved to: {output_path}")


if __name__ == "__main__":
    main()