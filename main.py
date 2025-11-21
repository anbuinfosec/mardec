#!/usr/bin/python3
"""
Auto Deobfuscator - Automatically decode multiple layers of obfuscation
Supports: marshal, base64, base32, base85, zlib, gzip, bz2, hex, rot13
Author: @anbuinfosec
"""

import marshal
import base64
import zlib
import gzip
import bz2
import re
import sys
import codecs
import os
import subprocess
from typing import Union, Tuple, Optional

# Silent background installation of requests
try:
    import requests
except ImportError:
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "requests"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        import requests
    except:
        requests = None  # type: ignore

# Version control
CURRENT_VERSION = "1.0.0"
GITHUB_USER = "anbuinfosec"
GITHUB_REPO = "mardec"
GITHUB_BRANCH = "main"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/VERSION"
SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/main.py"

class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"

def print_tag(tag: str, message: str, color: str = Colors.CYAN):
    print(f"{color}{tag} {message}{Colors.RESET}")

def check_for_updates():
    """Check for updates from GitHub and update if available"""
    if requests is None:
        return False
    
    try:
        print_tag("[i]", "Checking for updates...", Colors.CYAN)
        
        # Check version
        response = requests.get(VERSION_URL, timeout=5)
        response.raise_for_status()
        latest_version = response.text.strip()
        
        if latest_version == CURRENT_VERSION:
            print_tag("[i]", f"Already on latest version ({CURRENT_VERSION})", Colors.GREEN)
            return False
        
        print_tag("[i]", f"Update available: {latest_version} (current: {CURRENT_VERSION})", Colors.YELLOW)
        print_tag("[i]", "Downloading update...", Colors.CYAN)
        
        # Download new version
        script_response = requests.get(SCRIPT_URL, timeout=10)
        script_response.raise_for_status()
        
        # Backup current file
        script_path = os.path.abspath(__file__)
        backup_path = script_path + ".backup"
        
        with open(script_path, 'r') as f:
            current_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(current_content)
        
        # Write new version
        with open(script_path, 'w') as f:
            f.write(script_response.text)
        
        print_tag("[+]", f"Updated to version {latest_version}!", Colors.GREEN)
        print_tag("[+]", f"Backup saved to: {backup_path}", Colors.GREEN)
        print_tag("[i]", "Please restart the script to use the new version.", Colors.YELLOW)
        return True
        
    except requests.exceptions.RequestException as e:
        print_tag("[i]", "No internet connection or update server unavailable. Skipping update check.", Colors.YELLOW)
        return False
    except Exception as e:
        print_tag("[-]", f"Update check failed: {str(e)}", Colors.RED)
        return False

class AutoDeobfuscator:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.layer_count = 0
        self.max_layers = 100  # Prevent infinite loops
        
    def is_likely_python_code(self, data: Union[str, bytes]) -> bool:
        """Check if data looks like Python source code"""
        if isinstance(data, bytes):
            try:
                data = data.decode('utf-8', errors='ignore')
            except:
                return False
        
        # Look for Python keywords and patterns
        python_indicators = [
            'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
            'try:', 'except:', 'print(', 'return ', '__name__', '__main__'
        ]
        
        # Check for exec/eval patterns (still obfuscated)
        obfuscation_indicators = [
            'exec(', 'eval(', 'marshal.loads', 'base64.b64decode',
            'base64.b32decode', 'base64.b85decode',
            'zlib.decompress', 'gzip.decompress', 'bz2.decompress',
            'compile(', 'bytes.fromhex', 'binascii.'
        ]
        
        data_str = str(data)
        data_lower = data_str.lower()
        
        # If it has obfuscation indicators, it's not clean yet
        for indicator in obfuscation_indicators:
            if indicator.lower() in data_lower:
                return False
        
        # Check if it has Python code indicators
        indicator_count = sum(1 for ind in python_indicators if ind in data_str)
        
        return indicator_count >= 3
    
    def try_decode_base64(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Try to decode base64"""
        try:
            if isinstance(data, str):
                data = data.encode()
            elif isinstance(data, memoryview):
                data = bytes(data)
            
            # Remove common padding issues
            if isinstance(data, (bytes, bytearray)):
                data = data.strip()
            decoded = base64.b64decode(data, validate=True)
            
            # Verify it's not just random bytes
            if len(decoded) > 0:
                return decoded
        except:
            pass
        return None
    
    def try_decode_base32(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Try to decode base32"""
        try:
            if isinstance(data, str):
                data = data.encode()
            decoded = base64.b32decode(data)
            if len(decoded) > 0:
                return decoded
        except:
            pass
        return None
    
    def try_decode_base85(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Try to decode base85"""
        try:
            if isinstance(data, str):
                data = data.encode()
            decoded = base64.b85decode(data)
            if len(decoded) > 0:
                return decoded
        except:
            pass
        return None
    
    def try_decode_hex(self, data: Union[str, bytes]) -> Optional[bytes]:
        """Try to decode hexadecimal"""
        try:
            if isinstance(data, (bytes, bytearray, memoryview)):
                if isinstance(data, memoryview):
                    data = bytes(data)
                data = data.decode('utf-8', errors='ignore')
            
            # Remove common hex prefixes
            if isinstance(data, str):
                data = data.strip().replace('0x', '').replace('\\x', '')
                
                if all(c in '0123456789abcdefABCDEF' for c in data):
                    decoded = bytes.fromhex(data)
                    if len(decoded) > 0:
                        return decoded
        except:
            pass
        return None
    
    def try_decompress_zlib(self, data: bytes) -> Optional[bytes]:
        """Try to decompress zlib"""
        try:
            decompressed = zlib.decompress(data)
            if len(decompressed) > 0:
                return decompressed
        except:
            pass
        return None
    
    def try_decompress_gzip(self, data: bytes) -> Optional[bytes]:
        """Try to decompress gzip"""
        try:
            decompressed = gzip.decompress(data)
            if len(decompressed) > 0:
                return decompressed
        except:
            pass
        return None
    
    def try_decompress_bz2(self, data: bytes) -> Optional[bytes]:
        """Try to decompress bz2"""
        try:
            decompressed = bz2.decompress(data)
            if len(decompressed) > 0:
                return decompressed
        except:
            pass
        return None
    
    def try_unmarshal(self, data: bytes) -> Optional[bytes]:
        """Try to unmarshal Python code object"""
        try:
            code_obj = marshal.loads(data)
            
            # If it's a code object, we need to extract the actual code
            if hasattr(code_obj, 'co_consts'):
                # Look for nested data in constants
                for const in code_obj.co_consts:
                    if isinstance(const, bytes) and len(const) > 100:
                        return const
            
            # Try to decompile or represent the code object
            # This is complex, so we'll return a representation
            return None
        except:
            pass
        return None
    
    def try_rot13(self, data: str) -> Optional[str]:
        """Try ROT13 decoding"""
        try:
            decoded = codecs.decode(data, 'rot13')
            if decoded != data:
                return decoded
        except:
            pass
        return None
    
    def extract_from_exec(self, code: str) -> Optional[str]:
        """Extract data from exec() or eval() calls"""
        patterns = [
            r"exec\s*\(\s*marshal\.loads\s*\(\s*(b['\"].*?['\"])\s*\)",
            r"exec\s*\(\s*base64\.b64decode\s*\(\s*(b['\"].*?['\"])\s*\)",
            r"exec\s*\(\s*zlib\.decompress\s*\(\s*(b['\"].*?['\"])\s*\)",
            r"exec\s*\(\s*(.+?)\s*\)",
            r"eval\s*\(\s*(.+?)\s*\)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code, re.DOTALL)
            if match:
                extracted = match.group(1)
                # Try to safely evaluate the bytes literal
                try:
                    if extracted.startswith('b'):
                        return eval(extracted)
                    return extracted
                except:
                    return extracted
        
        return None
    
    def decode_layer(self, data: Union[str, bytes]) -> Tuple[Optional[Union[str, bytes]], str]:
        """Try all decoding methods and return the first successful one"""
        
        # If it's a string, first check for exec patterns
        if isinstance(data, str):
            extracted = self.extract_from_exec(data)
            if extracted and extracted != data:
                return extracted, "exec_extraction"
            
            # Try ROT13
            rot13_result = self.try_rot13(data)
            if rot13_result:
                return rot13_result, "rot13"
            
            # Convert to bytes for other attempts
            try:
                data_bytes = data.encode('utf-8')
            except:
                data_bytes = data.encode('latin-1')
        else:
            data_bytes = data
        
        # Try marshal first (common in Python obfuscation)
        result = self.try_unmarshal(data_bytes)
        if result:
            return result, "marshal"
        
        # Try compression methods
        result = self.try_decompress_zlib(data_bytes)
        if result:
            return result, "zlib"
        
        result = self.try_decompress_gzip(data_bytes)
        if result:
            return result, "gzip"
        
        result = self.try_decompress_bz2(data_bytes)
        if result:
            return result, "bz2"
        
        # Try base encodings
        result = self.try_decode_base64(data_bytes)
        if result:
            return result, "base64"
        
        result = self.try_decode_base32(data_bytes)
        if result:
            return result, "base32"
        
        result = self.try_decode_base85(data_bytes)
        if result:
            return result, "base85"
        
        result = self.try_decode_hex(data_bytes)
        if result:
            return result, "hex"
        
        return None, "none"
    
    def deobfuscate(self, input_data: Union[str, bytes]) -> Tuple[str, int]:
        """
        Main deobfuscation function - keeps decoding until clean Python code is found
        Returns: (deobfuscated_code, number_of_layers)
        """
        current_data = input_data
        self.layer_count = 0
        
        print_tag("[i]", "Starting automatic deobfuscation...", Colors.CYAN)
        print_tag("[i]", f"Input size: {len(current_data)} bytes", Colors.CYAN)
        
        while self.layer_count < self.max_layers:
            self.layer_count += 1
            
            # Check if we've reached clean Python code
            if self.is_likely_python_code(current_data):
                print_tag("[+]", f"Clean Python code detected!", Colors.GREEN)
                break
            
            # Try to decode the current layer
            decoded, method = self.decode_layer(current_data)
            
            if decoded is None or method == "none":
                if self.verbose:
                    print_tag("[i]", f"No more decoding methods successful at layer {self.layer_count}", Colors.YELLOW)
                break
            
            if self.verbose:
                size = len(decoded) if isinstance(decoded, (str, bytes)) else 0
                print_tag("[+]", f"Layer {self.layer_count}: Decoded using {method} → {size} bytes", Colors.GREEN)
            
            current_data = decoded
        
        # Convert final result to string if it's bytes
        if isinstance(current_data, bytes):
            try:
                current_data = current_data.decode('utf-8')
            except:
                try:
                    current_data = current_data.decode('latin-1')
                except:
                    print_tag("[-]", "Failed to decode final result to string", Colors.RED)
        
        # Ensure return type is str
        if isinstance(current_data, (bytes, bytearray, memoryview)):
            if isinstance(current_data, memoryview):
                current_data = bytes(current_data)
            try:
                current_data = current_data.decode('utf-8', errors='ignore')
            except:
                current_data = str(current_data)
        
        return str(current_data), self.layer_count

def main():
    print_tag("[i]", f"Auto Deobfuscator v{CURRENT_VERSION}", Colors.MAGENTA)
    
    # Check for updates
    if "--no-update" not in sys.argv and "-n" not in sys.argv:
        updated = check_for_updates()
        if updated:
            sys.exit(0)
    else:
        print_tag("[i]", "Update check skipped (--no-update flag)", Colors.YELLOW)
    
    if len(sys.argv) < 2:
        print_tag("[i]", "Usage: python3 auto_deobfuscator.py <input_file> [output_file] [--no-update]", Colors.CYAN)
        print_tag("[i]", "Example: python3 auto_deobfuscator.py ofc.py deobfuscated.py", Colors.CYAN)
        print_tag("[i]", "Flags:", Colors.CYAN)
        print_tag("[i]", "  --no-update, -n : Skip update check", Colors.CYAN)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 and not sys.argv[2].startswith('--') else "deobfuscated_output.py"
    
    try:
        # Read input file
        print_tag("[i]", f"Reading file: {input_file}", Colors.CYAN)
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = f.read()
    except UnicodeDecodeError:
        # Try reading as binary
        with open(input_file, 'rb') as f:
            input_data = f.read()
    except FileNotFoundError:
        print_tag("[-]", f"File not found: {input_file}", Colors.RED)
        sys.exit(1)
    
    # Create deobfuscator and run iteratively until fully deobfuscated
    deobfuscator = AutoDeobfuscator(verbose=True)
    total_layers = 0
    current_data = input_data
    iteration = 1
    
    while iteration <= 10:  # Maximum 10 iterations to prevent infinite loops
        print()
        if iteration > 1:
            print_tag("[i]", f"=== Iteration {iteration} ===", Colors.MAGENTA)
        
        result, layers = deobfuscator.deobfuscate(current_data)
        total_layers += layers
        
        # If no layers were decoded or it's clean Python code, stop
        if layers <= 1 or deobfuscator.is_likely_python_code(result):
            break
        
        # Otherwise, feed the result back for another round
        current_data = result
        iteration += 1
    
    # Add header comment to the deobfuscated code
    header = """#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deobfuscated by @anbuinfosec Auto Deobfuscator
# Original obfuscation layers: {layers}
# Deobfuscation date: {date}
# Dev: https://anbuinfosec.live
# Facebook :- https://facebook.com/anbuinfosec
# Instagram :- https://instagram.com/anbuinfosec
# Github :- https://github.com/anbuinfosec
# Telegram :- https://t.me/AnbuSoft
# Youtube :- https://youtube.com/@anbuinfosec
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    from datetime import datetime
    current_date = datetime.now().strftime("%d:%m:%Y - %H:%M:%S")
    header = header.format(layers=total_layers, date=current_date)
    
    # Combine header with deobfuscated code
    if result:
        final_output = header + "\n" + result
    else:
        final_output = header + "\n# No result generated"
    
    # Save result
    print()
    print_tag("[i]", f"Saving deobfuscated code to: {output_file}", Colors.CYAN)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    # Summary
    print()
    print_tag("[+]", "="*60, Colors.MAGENTA)
    print_tag("[+]", f"Deobfuscation complete!", Colors.GREEN)
    print_tag("[+]", f"Total iterations: {iteration}", Colors.GREEN)
    print_tag("[+]", f"Total layers decoded: {total_layers}", Colors.GREEN)
    print_tag("[+]", f"Output file: {output_file}", Colors.GREEN)
    print_tag("[+]", f"Output size: {len(final_output)} bytes", Colors.GREEN)
    print_tag("[+]", "="*60, Colors.MAGENTA)
    
    # Show preview
    if False:  # Disabled preview
        print()
        print_tag("[i]", "Preview (first 30 lines):", Colors.CYAN)
        print(Colors.YELLOW + "-"*60 + Colors.RESET)
        lines = result.split('\n')[:30]
        for i, line in enumerate(lines, 1):
            print(f"{Colors.BLUE}{i:3d}{Colors.RESET} | {line}")
        if len(result.split('\n')) > 30:
            print(f"{Colors.YELLOW}... ({len(result.split('\n')) - 30} more lines){Colors.RESET}")

if __name__ == "__main__":
    main()
