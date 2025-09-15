#!/usr/bin/env python3
"""
StegHub - Advanced Steganography Toolkit
Main CLI interface that provides access to all tools
"""

import sys
import subprocess
import argparse

TOOLS = {
    'gradus': {
        'description': 'Image steganography using histogram shifting',
        'details': 'Hide text messages in PNG images using advanced histogram manipulation'
    },
    'resono': {
        'description': 'Audio steganography using phase coding', 
        'details': 'Hide text messages in WAV audio files using phase manipulation'
    },
    'shadowbits': {
        'description': 'Image and Audio steganography using LSB',
        'details': 'Hide any file type in images or audio using Least Significant Bit technique'
    }
}

def show_logo():
    """Display StegHub ASCII logo"""
    logo = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  ███████╗████████╗███████╗ ██████╗ ██╗  ██╗██╗   ██╗██████╗  ║
║  ██╔════╝╚══██╔══╝██╔════╝██╔════╝ ██║  ██║██║   ██║██╔══██╗ ║
║  ███████╗   ██║   █████╗  ██║  ███╗███████║██║   ██║██████╔╝ ║
║  ╚════██║   ██║   ██╔══╝  ██║   ██║██╔══██║██║   ██║██╔══██╗ ║
║  ███████║   ██║   ███████╗╚██████╔╝██║  ██║╚██████╔╝██████╔╝ ║
║  ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ║
║                                                       ║
║           ░▒▓█ STEGANOGRAPHY METAPACKAGE █▓▒░         ║
║                                                       ║
║    ┌─[HIDE]───────────────────────────────[SEEK]─┐    ║
║    │    🔐 Advanced Steganography Toolkit 🔐     │    ║
║    │     ∴ What you see is not what you get ∴    │    ║
║    └─────────────────────────────────────────────┘    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    print(logo)

def main():
    if len(sys.argv) >= 2 and sys.argv[1] in TOOLS:
        tool = sys.argv[1]
        tool_args = sys.argv[2:]
        
        try:
            subprocess.run([tool] + tool_args, check=True)
            return
        except FileNotFoundError:
            print(f"Error: {tool} is not installed")
            print(f"Install with: pip install {tool}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    
    # StegHub commands
    parser = argparse.ArgumentParser(
        description='StegHub - Advanced Steganography Toolkit',
        epilog='Use: steghub <tool> --help for tool-specific help'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Tools subparsers (for help display only)
    for tool, info in TOOLS.items():
        subparsers.add_parser(tool, help=info['description'], add_help=False)
    
    # StegHub specific commands
    subparsers.add_parser('info', help='Show detailed information about each tool')
    subparsers.add_parser('list', help='List all available tools')
    
    args = parser.parse_args()
    
    if not args.command:
        show_main_help()
        return
    
    if args.command == 'info':
        show_info()
    elif args.command == 'list':
        list_tools()
    else:
        show_main_help()

def show_main_help():
    """Show main StegHub help"""
    show_logo()
    print("StegHub - Advanced Steganography Toolkit")
    print("=" * 45)
    print()
    print("Available tools:")
    
    for tool, info in TOOLS.items():
        print(f"  {tool:<12} - {info['description']}")
    
    print()
    print("StegHub commands:")
    print("  info         - Show detailed information about each tool")
    print("  list         - List all available tools")
    print()
    print("Usage examples:")
    print("  gradus --help                       # Show gradus help")
    print("  gradus embed --in 'secret' ...      # Use gradus directly")
    print("  resono embed --in 'secret' ...      # Use resono directly")
    print("  steghub info                        # Show tool details")

def show_info():
    """Show detailed information about each tool"""
    print("StegHub - Tool Information")
    print("=" * 30)
    print()
    
    for tool, info in TOOLS.items():
        # Check if tool is installed
        try:
            subprocess.run([tool, '--help'], capture_output=True, timeout=3)
            status = "✓ Installed"
        except FileNotFoundError:
            status = "✗ Not installed (pip install {})".format(tool)
        except:
            status = "? Unknown status"
        
        print(f"{tool.upper()}")
        print(f"  Status: {status}")
        print(f"  Purpose: {info['details']}")
        print(f"  Usage: steghub {tool} --help")
        print()

def list_tools():
    """Simple list of available tools"""
    print("Available StegHub tools:")
    for tool in TOOLS.keys():
        print(f"  - {tool}")

if __name__ == "__main__":
    main()