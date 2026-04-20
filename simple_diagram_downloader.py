"""
Simple Diagram Downloader using Online Services
Converts Mermaid diagrams to PNG using public APIs
No installation of Node.js or browsers required
"""

import requests
import base64
import json
import time
import sys
from pathlib import Path
from urllib.parse import quote

class SimpleMermaidConverter:
    """Convert Mermaid diagrams using public APIs"""
    
    @staticmethod
    def mermaid_ink(diagram_content):
        """Use mermaid.ink service"""
        try:
            # Encode diagram
            data = {"code": diagram_content, "mermaid": {"theme": "default"}}
            encoded = base64.urlsafe_b64encode(
                json.dumps(data).encode()
            ).decode().rstrip('=')
            
            # Call API
            url = f"https://mermaid.ink/img/{encoded}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.content
            return None
        except:
            return None
    
    @staticmethod
    def kroki_io(diagram_content):
        """Use kroki.io service"""
        try:
            # Encode for Kroki
            encoded = base64.b64encode(
                diagram_content.encode('utf-8')
            ).decode()
            
            # Call API
            url = f"https://kroki.io/mermaid/png/{encoded}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.content
            return None
        except:
            return None
    
    @staticmethod
    def convert(diagram_content):
        """Try multiple conversion methods"""
        methods = [
            ("mermaid.ink", SimpleMermaidConverter.mermaid_ink),
            ("kroki.io", SimpleMermaidConverter.kroki_io),
        ]
        
        for method_name, method in methods:
            try:
                result = method(diagram_content)
                if result:
                    return method_name, result
            except:
                continue
        
        return None, None

def download_diagrams():
    """Download diagrams as PNG"""
    print("=" * 70)
    print("Downloading Architecture Diagrams as PNG")
    print("(Using public API services - no installation required)")
    print("=" * 70)
    
    # Find .mmd files
    mmd_files = sorted(Path('.').glob('*.mmd'))
    
    if not mmd_files:
        print("\n❌ No .mmd files found")
        return False
    
    print(f"\nFound {len(mmd_files)} diagrams\n")
    
    successful = 0
    failed = 0
    
    for i, mmd_file in enumerate(mmd_files, 1):
        png_file = mmd_file.with_suffix('.png')
        
        try:
            print(f"[{i}/{len(mmd_files)}] {mmd_file.name:<42}", end=' ')
            sys.stdout.flush()
            
            # Read diagram
            with open(mmd_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert
            method, png_data = SimpleMermaidConverter.convert(content)
            
            if png_data:
                # Save file
                with open(png_file, 'wb') as f:
                    f.write(png_data)
                
                size_kb = len(png_data) / 1024
                print(f"✓ ({method}, {size_kb:.1f} KB)")
                successful += 1
                
                # Be nice to API servers
                time.sleep(1)
            else:
                print("✗ (Conversion failed)")
                failed += 1
                
        except Exception as e:
            print(f"✗ ({str(e)[:20]})")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {successful} downloaded, {failed} failed")
    print("=" * 70)
    
    if successful > 0:
        print("\n✓ Successfully downloaded PNG files:\n")
        for mmd_file in mmd_files:
            png_file = mmd_file.with_suffix('.png')
            if png_file.exists():
                size_kb = os.path.getsize(png_file) / 1024
                print(f"  ✓ {png_file.name} ({size_kb:.1f} KB)")
                print(f"    Location: {png_file.absolute()}")
        return True
    else:
        print("\n❌ Failed to download diagrams")
        print("\nAlternative:")
        print("  1. Visit https://mermaid.live")
        print("  2. Open each .mmd file in a text editor")
        print("  3. Copy content to Mermaid Live")
        print("  4. Download as PNG")
        return False

if __name__ == "__main__":
    import os
    
    print("\nChecking internet connection...")
    try:
        requests.get('https://mermaid.ink', timeout=5)
        print("✓ Internet available\n")
    except:
        print("✗ No internet connection - cannot download")
        sys.exit(1)
    
    success = download_diagrams()
    sys.exit(0 if success else 1)
