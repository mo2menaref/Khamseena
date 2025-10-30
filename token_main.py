"""
Main entry point for Khamseena Scanner
Run this file to scan Khamseena source files
"""

import sys
import os
from scanner import Scanner, LexicalError


def scan_file(input_file, output_file=None):
    """
    Scan a Khamseena source file and output tokens
    
    Args:
        input_file: Path to the .kh source file
        output_file: Optional path to write token output
    """
    try:
        # Read source file
        with open(input_file, 'r') as f:
            source_code = f.read()
        
        print(f"\n{'='*70}")
        print(f"Scanning file: {input_file}")
        print(f"{'='*70}\n")
        
        # Create scanner and tokenize
        scanner = Scanner(source_code)
        tokens = scanner.tokenize()
        
        # Print or save tokens
        if output_file:
            scanner.print_tokens(output_file)
        else:
            scanner.print_tokens()
        
        print(f"\n✓ Scanning completed successfully!")
        print(f"✓ Total tokens: {len(tokens)}")
        
        return tokens
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except LexicalError as e:
        print(f"\n✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


def scan_string(source_code):
    """
    Scan Khamseena source code from a string
    
    Args:
        source_code: String containing Khamseena code
    
    Returns:
        List of tokens
    """
    try:
        scanner = Scanner(source_code)
        tokens = scanner.tokenize()
        scanner.print_tokens()
        return tokens
    except LexicalError as e:
        print(f"\n✗ {e}")
        return None


def main():
    """Main function with command-line interface"""
    
    if len(sys.argv) < 2:
        print("Khamseena Scanner")
        print("="*50)
        print("\nUsage:")
        print("  python main.py <input_file.kh> [output_file.txt]")
        print("\nExamples:")
        print("  python main.py examples/test.kh")
        print("  python main.py examples/test.kh output/tokens.txt")
        print("\nOptions:")
        print("  input_file.kh    - Khamseena source file to scan")
        print("  output_file.txt  - Optional output file for tokens")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Scan the file
    scan_file(input_file, output_file)


if __name__ == "__main__":
    main()