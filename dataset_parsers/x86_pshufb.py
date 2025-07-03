#!/usr/bin/env python3
"""
X86 PSHUFB Instruction Detector
Searches for directories containing input.txt files with the `pshufb` instruction.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def detect_pshufb_instruction(content):
    """
    Detects the `pshufb` (Packed Shuffle Bytes) instruction in x86 assembly code.
    
    Args:
        content (str): The content of the input.txt file.
        
    Returns:
        list: A list of tuples, where each tuple contains the 
              line number and the full line of a matched instruction.
    """
    matches = []
    lines = content.split('\n')
    
    # A case-insensitive pattern to match lines starting with the `pshufb` instruction.
    # The `\b` ensures we match the whole word "pshufb" and not part of another word.
    pshufb_pattern = re.compile(r'^\s*pshufb\b', re.IGNORECASE)
    
    for i, line in enumerate(lines, 1):
        # We search the line for the instruction pattern.
        if pshufb_pattern.search(line):
            matches.append((i, line.strip()))
            
    return matches


def analyze_directory(dir_path):
    """
    Analyzes a single directory for an input.txt file and searches for the PSHUFB instruction.
    
    Args:
        dir_path (Path): The path to the directory to analyze.
        
    Returns:
        dict: Analysis results if the PSHUFB instruction is found, otherwise None.
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
    
    # Find all PSHUFB instructions in the content
    matches = detect_pshufb_instruction(content)
    
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
    Scans all subdirectories in the given path for input.txt files with the PSHUFB instruction.
    
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
    print("Looking for input.txt files with the PSHUFB instruction...\n")
    
    # Use rglob to recursively find all subdirectories
    for dir_path in root.rglob('*'):
        if dir_path.is_dir():
            result = analyze_directory(dir_path)
            if result:
                results.append(result)
                print(f"✓ Found PSHUFB instruction in: {dir_path}")
    
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
        
        f.write("X86 PSHUFB Instruction Detection Results\n")
        f.write("=" * 60 + "\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total directories with matching instructions found: {len(results)}\n\n")
        
        f.write("Pattern Description:\n")
        f.write("Searches for the `pshufb` (Packed Shuffle Bytes) instruction, which is part\n")
        f.write("of the SSSE3 instruction set. It performs a parallel, in-register lookup\n")
        f.write("table operation, making it useful for complex byte-level permutations.\n\n")
        
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
    print("SCAN RESULTS - PSHUFB Instruction Detection")
    print(f"{'='*70}")
    
    if not results:
        print("No directories found containing input.txt with the PSHUFB instruction.")
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
        description="Detect the x86 `pshufb` instruction in input.txt files."
    )
    parser.add_argument(
        "path", 
        help="Root path to scan for directories containing input.txt files."
    )
    parser.add_argument(
        "-o", "--output", 
        default="pshufb_report.txt",
        help="Output file name (default: pshufb_report.txt)"
    )
    
    args = parser.parse_args()
    
    # Scan directories for the PSHUFB instruction
    results = scan_directories(args.path)
    
    if not results:
        print("\nNo directories found containing input.txt with the PSHUFB instruction.")
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