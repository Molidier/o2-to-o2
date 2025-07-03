#!/usr/bin/env python3
"""
X86 Assembly Pattern Detector
Searches for directories containing input.txt files with sequences of CMP and TEST instructions.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def detect_cmp_test_sequences(content):
    """
    Detect sequences of CMP and TEST instructions in x86 assembly code.
    
    Args:
        content (str): Content of the input.txt file
        
    Returns:
        list: List of tuples containing (line_number, instruction) for matches
    """
    matches = []
    lines = content.split('\n')
    
    # Pattern to match CMP and TEST instructions (case insensitive)
    # Matches various formats like: cmp eax, ebx; test al, al; CMP [esp+4], 0; etc.
    cmp_pattern = re.compile(r'^\s*cmp\s+', re.IGNORECASE)
    test_pattern = re.compile(r'^\s*test\s+', re.IGNORECASE)
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if cmp_pattern.match(line) or test_pattern.match(line):
            matches.append((i, line))
    
    return matches


def find_sequences(content):
    """
    Find sequences that contain CMP/TEST instructions with results stored in EFLAGS register.
    These are sequences where CMP/TEST instructions set flags that are then used by
    conditional instructions (SET*, J*, CMOV*, etc.) or other flag-dependent operations.
    
    Args:
        content (str): Full content of the file
        
    Returns:
        list: List of sequences containing CMP/TEST with EFLAGS usage
    """
    lines = content.split('\n')
    sequences = []
    
    # Pattern to match CMP and TEST instructions (with various suffixes)
    cmp_test_pattern = re.compile(r'^\s*(cmp|test)[lwbqdm]?\s+', re.IGNORECASE)
    
    # Patterns for instructions that use EFLAGS (flags set by CMP/TEST)
    eflags_dependent_patterns = [
        # SET* instructions (setae, setb, sete, setne, setg, setl, etc.)
        re.compile(r'^\s*set(a|ae|b|be|c|e|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|s|z)\s+', re.IGNORECASE),
        
        # Conditional jumps (ja, jae, jb, jbe, jc, je, jg, jge, jl, jle, etc.)
        re.compile(r'^\s*j(a|ae|b|be|c|cxz|e|ecxz|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|rcxz|s|z)\s+', re.IGNORECASE),
        
        # Conditional moves (cmova, cmovae, cmovb, etc.)
        re.compile(r'^\s*cmov(a|ae|b|be|c|e|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|s|z)\s+', re.IGNORECASE),
        
        # Other flag-dependent instructions
        re.compile(r'^\s*(adc|sbb|rcl|rcr|sal|sar|shl|shr)\s+', re.IGNORECASE),  # Instructions that use carry flag
        re.compile(r'^\s*(into|loop|loope|loopne)\s*', re.IGNORECASE),  # Loop and overflow instructions
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if current line has CMP or TEST
        if cmp_test_pattern.match(line):
            sequence_start = max(0, i - 1)  # Include 1 line before for context
            sequence_lines = []
            found_eflags_usage = False
            
            # Look ahead for EFLAGS-dependent instructions within reasonable distance
            j = sequence_start
            sequence_end = min(len(lines), i + 15)  # Look up to 15 lines ahead for flag usage
            
            while j < sequence_end:
                current_line = lines[j].strip()
                if current_line and not current_line.startswith('#') and not current_line.startswith(';') and not current_line.startswith('//'):
                    sequence_lines.append((j + 1, current_line))
                    
                    # Check if this line uses EFLAGS
                    is_cmp_test = cmp_test_pattern.match(current_line)
                    uses_eflags = any(pattern.match(current_line) for pattern in eflags_dependent_patterns)
                    
                    if uses_eflags:
                        found_eflags_usage = True
                        # Extend search a bit more if we find flag usage
                        sequence_end = min(len(lines), j + 8)
                    
                    # If we find another CMP/TEST, extend the sequence
                    if is_cmp_test and j > i:
                        sequence_end = min(len(lines), j + 10)
                
                j += 1
            
            # Only consider it a valid sequence if:
            # 1. It has meaningful content (at least 2 lines)
            # 2. It contains CMP/TEST instructions
            # 3. It has EFLAGS-dependent instructions
            if len(sequence_lines) >= 2 and found_eflags_usage:
                cmp_test_count = sum(1 for _, line in sequence_lines if cmp_test_pattern.match(line))
                eflags_usage_count = sum(1 for _, line in sequence_lines 
                                       if any(pattern.match(line) for pattern in eflags_dependent_patterns))
                
                if cmp_test_count >= 1 and eflags_usage_count >= 1:
                    sequences.append({
                        'start_line': sequence_start + 1,
                        'end_line': min(sequence_end, len(lines)),
                        'lines': sequence_lines,
                        'cmp_test_count': cmp_test_count,
                        'eflags_usage_count': eflags_usage_count,
                        'total_lines': len(sequence_lines)
                    })
                    
                    # Skip ahead to avoid overlapping sequences
                    i = sequence_end
                    continue
        
        i += 1
    
    return sequences


def analyze_directory(dir_path):
    """
    Analyze a single directory for input.txt file with CMP/TEST sequences that use EFLAGS.
    
    Args:
        dir_path (Path): Path to directory to analyze
        
    Returns:
        dict: Analysis results or None if no input.txt or no sequences found
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
    
    sequences = find_sequences(content)
    
    if not sequences:
        return None
    
    # Extract the first number from the directory name to use as a problem number
    problem_number_match = re.search(r'\d+', dir_path.name)
    problem_number = int(problem_number_match.group(0)) if problem_number_match else None
        
    # Count total CMP/TEST instructions and EFLAGS usage across all sequences
    total_cmp_test = sum(seq['cmp_test_count'] for seq in sequences)
    total_eflags_usage = sum(seq['eflags_usage_count'] for seq in sequences)
    
    return {
        'directory': str(dir_path),
        'problem_number': problem_number,
        'input_file': str(input_file),
        'total_cmp_test': total_cmp_test,
        'total_eflags_usage': total_eflags_usage,
        'sequences': sequences,
        'sequence_count': len(sequences)
    }


def scan_directories(root_path):
    """
    Scan all directories in the given path for the pattern.
    
    Args:
        root_path (str): Root path to scan
        
    Returns:
        list: List of analysis results for directories with sequences
    """
    root = Path(root_path)
    results = []
    
    if not root.exists():
        print(f"Error: Path '{root_path}' does not exist.")
        return results
    
    print(f"Scanning directories in: {root}")
    print("Looking for input.txt files with CMP/TEST→EFLAGS instruction sequences...")
    print("(CMP/TEST instructions that set flags used by subsequent instructions)\n")
    
    # Walk through all subdirectories
    for dir_path in root.rglob('*'):
        if dir_path.is_dir():
            result = analyze_directory(dir_path)
            if result:
                results.append(result)
                print(f"✓ Found CMP/TEST→EFLAGS sequences in: {dir_path}")
    
    return results


def save_results(results, problem_numbers, output_file):
    """
    Save results to a text file.
    
    Args:
        results (list): Sorted list of analysis results
        problem_numbers (list): Sorted list of problem numbers found.
        output_file (Path): Output file path object
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the list of problem numbers at the very top of the report
        f.write(f"{problem_numbers}\n")

        f.write("X86 Assembly CMP/TEST with EFLAGS Pattern Detection Results\n")
        f.write("=" * 60 + "\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total directories with EFLAGS-using sequences found: {len(results)}\n\n")
        
        f.write("Pattern Description:\n")
        f.write("Looking for sequences where CMP/TEST instructions set EFLAGS register\n")
        f.write("and subsequent instructions use those flags (SET*, J*, CMOV*, etc.)\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"[{i}] Directory: {result['directory']}\n")
            f.write(f"    Input file: {result['input_file']}\n")
            f.write(f"    Total CMP/TEST instructions: {result['total_cmp_test']}\n")
            f.write(f"    Total EFLAGS-dependent instructions: {result['total_eflags_usage']}\n")
            f.write(f"    Number of sequences: {result['sequence_count']}\n")
            f.write("    Sequences found:\n")
            
            for j, sequence in enumerate(result['sequences'], 1):
                f.write(f"      Sequence {j} (Lines {sequence['start_line']}-{sequence['end_line']}):\n")
                f.write(f"        CMP/TEST: {sequence['cmp_test_count']}, EFLAGS usage: {sequence['eflags_usage_count']}, Total lines: {sequence['total_lines']}\n")
                for line_num, instruction in sequence['lines']:
                    f.write(f"        Line {line_num}: {instruction}\n")
                f.write("\n")
            f.write("\n")


def print_results(results):
    """
    Print results to console.
    
    Args:
        results (list): List of analysis results
    """
    print(f"\n{'='*70}")
    print("SCAN RESULTS - CMP/TEST with EFLAGS Usage")
    print(f"{'='*70}")
    
    if not results:
        print("No directories found with CMP/TEST instructions that use EFLAGS register.")
        return
        
    print(f"Total directories with CMP/TEST→EFLAGS sequences: {len(results)}\n")
    
    for i, result in enumerate(results, 1):
        print(f"[{i}] {result['directory']}")
        print(f"    • CMP/TEST instructions: {result['total_cmp_test']}")
        print(f"    • EFLAGS-dependent instructions: {result['total_eflags_usage']}")
        print(f"    • Number of sequences: {result['sequence_count']}")
        print("    • Sequences:")
        
        for j, sequence in enumerate(result['sequences'][:3], 1): # Show first 3 sequences for brevity
            print(f"      Sequence {j}: {sequence['total_lines']} lines")
            print(f"        CMP/TEST: {sequence['cmp_test_count']}, EFLAGS usage: {sequence['eflags_usage_count']}")
            # Show first few lines of the sequence
            for line_num, instruction in sequence['lines'][:5]:
                print(f"        Line {line_num}: {instruction}")
            if len(sequence['lines']) > 5:
                print(f"        ... and {len(sequence['lines']) - 5} more lines")
        if result['sequence_count'] > 3:
            print(f"      ... and {result['sequence_count'] - 3} more sequences.")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Detect x86 assembly CMP/TEST instruction sequences in input.txt files"
    )
    parser.add_argument(
        "path", 
        help="Root path to scan for directories containing input.txt files"
    )
    parser.add_argument(
        "-o", "--output", 
        default="cmp_test_eflags_report.txt",
        help="Output file name (default: cmp_test_eflags_report.txt)"
    )
    
    args = parser.parse_args()
    
    # Scan directories
    results = scan_directories(args.path)

    if not results:
        print("\nNo directories found with matching CMP/TEST->EFLAGS sequences.")
        return

    # Sort results based on the extracted problem number for consistent ordering.
    # Put directories without a number at the end.
    results.sort(key=lambda r: r.get('problem_number') if r.get('problem_number') is not None else float('inf'))

    # Extract a sorted list of unique problem numbers from the results
    problem_numbers = sorted(list(set(
        r['problem_number'] for r in results if r.get('problem_number') is not None
    )))
    
    # Print results to console
    print_results(results)
    
    # Define the output directory and create it if it doesn't exist
    output_dir = Path("a_reports")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / args.output

    # Save results to file
    save_results(results, problem_numbers, output_path)
    print(f"\nDetailed report saved to: {output_path}")


if __name__ == "__main__":
    main()