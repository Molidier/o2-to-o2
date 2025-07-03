#!/usr/bin/env python3
"""
X86 SIMD Instruction Detector
Searches for directories containing input.txt files with x86 SIMD instructions
(MMX, SSE, AVX, etc.).
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def detect_simd_instructions(content):
    """
    Detects a wide range of x86 SIMD instructions (MMX, SSE, AVX families).
    
    Args:
        content (str): The content of the input.txt file.
        
    Returns:
        list: A list of tuples, where each tuple contains the 
              line number and the full line of a matched instruction.
    """
    matches = []
    lines = content.split('\n')
    
    # A comprehensive, case-insensitive pattern to match a wide range of SIMD instructions.
    # This is not exhaustive but covers the vast majority of common cases by looking for
    # characteristic prefixes and suffixes.
    # It is broken down using re.VERBOSE for readability.
    simd_pattern = re.compile(r"""
        ^\s*           # Start of the line with optional whitespace
        (
            # Part 1: AVX, AVX2, AVX-512 (most start with 'v')
            v[a-zA-Z0-9]+
            
            | # OR
            
            # Part 2: MMX and SSE packed integer instructions (often start with 'p')
            # Examples: paddb, pshufb, pmovmskb, pcmpeqb
            p(add|sub|mul|avg|sad|shuf|sl|sr|and|or|xor|cmp|mov|pack|unpck|alignr|hadd|hsub|madd|sign|abs)\w*
            
            | # OR
            
            # Part 3: SSE instructions with data type suffixes
            # ps: packed single, pd: packed double, ss: scalar single, sd: scalar double
            # Examples: addps, movaps, subsd, sqrtss, divpd
            (add|sub|mul|div|sqrt|rcp|rsqrt|max|min|cmp|and|or|xor|mov|shuf|unpck|blend|dp|round|insert|extract)\w*(ps|pd|ss|sd)

            | # OR

            # Part 4: Other specific but common SSE instructions not caught above
            # Examples: movaps, movdqa, shufpd, blendps
            (mov(aps|ups|dqa|dqu|hlps|lhps|mskpd|mskps)|(shuf|blend|dp)(ps|pd))

        )\b             # Word boundary to avoid matching parts of other words (e.g., 'vmlinuz')
    """, re.IGNORECASE | re.VERBOSE)
    
    for i, line in enumerate(lines, 1):
        # We search within the line, not just match the start, to find instructions
        # that might be indented.
        if simd_pattern.search(line):
            matches.append((i, line.strip()))
            
    return matches


def analyze_directory(dir_path):
    """
    Analyzes a single directory for an input.txt file and searches for SIMD instructions.
    
    Args:
        dir_path (Path): The path to the directory to analyze.
        
    Returns:
        dict: Analysis results if SIMD instructions are found, otherwise None.
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
    
    # Find all SIMD instructions in the content
    matches = detect_simd_instructions(content)
    
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
    Scans all subdirectories in the given path for input.txt files with SIMD instructions.
    
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
    print("Looking for input.txt files with x86 SIMD instructions...\n")
    
    # Use rglob to recursively find all subdirectories
    for dir_path in root.rglob('*'):
        if dir_path.is_dir():
            result = analyze_directory(dir_path)
            if result:
                results.append(result)
                print(f"✓ Found SIMD instructions in: {dir_path}")
    
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
        
        f.write("X86 SIMD Instruction Detection Results\n")
        f.write("=" * 60 + "\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total directories with matching instructions found: {len(results)}\n\n")
        
        f.write("Pattern Description:\n")
        f.write("Searches for instructions characteristic of x86 SIMD extensions (MMX, SSE, AVX, etc.).\n")
        f.write("The pattern looks for:\n")
        f.write("  - Instructions starting with 'v' (for AVX, AVX2, AVX-512).\n")
        f.write("  - Packed integer instructions, often starting with 'p' (e.g., paddb, pshufb).\n")
        f.write("  - SSE instructions with data type suffixes (e.g., addps, subsd, movaps).\n\n")
        
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
    print("SCAN RESULTS - X86 SIMD Instruction Detection")
    print(f"{'='*70}")
    
    if not results:
        print("No directories found containing input.txt with x86 SIMD instructions.")
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
        description="Detect x86 SIMD instructions (MMX, SSE, AVX) in input.txt files."
    )
    parser.add_argument(
        "path", 
        help="Root path to scan for directories containing input.txt files."
    )
    parser.add_argument(
        "-o", "--output", 
        default="simd_report.txt",
        help="Output file name (default: simd_report.txt)"
    )
    
    args = parser.parse_args()
    
    # Scan directories for SIMD instructions
    results = scan_directories(args.path)
    
    if not results:
        print("\nNo directories found containing input.txt with x86 SIMD instructions.")
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