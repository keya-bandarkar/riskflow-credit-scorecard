"""
Advanced Diagram Downloader with Multiple API Fallbacks
Better retry logic and multiple service attempts
"""

import requests
import base64
import json
import time
import sys
import os
from pathlib import Path

def encode_for_kroki_svg(diagram_content):
    """Encode for Kroki SVG endpoint"""
    return base64.b64encode(diagram_content.encode('utf-8')).decode()

def try_kroki_render_to_file(diagram_content, output_png):
    """Use Kroki's SVG endpoint then convert to PNG"""
    try:
        # Get SVG from Kroki
        response = requests.post(
            "https://kroki.io/mermaid/svg",
            data=diagram_content.encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            # Try to convert SVG to PNG using online service
            svg_data = response.content
            
            # Save as SVG first (SVG is also useful)
            svg_file = str(output_png).replace('.png', '.svg')
            with open(svg_file, 'wb') as f:
                f.write(svg_data)
            
            return True, f"kroki_svg"
        return False, None
    except Exception as e:
        return False, str(e)

def try_mermaid_ink(diagram_content, output_png):
    """Try mermaid.ink with retry"""
    try:
        data = {"code": diagram_content, "mermaid": {"theme": "default"}}
        encoded = base64.urlsafe_b64encode(
            json.dumps(data).encode()
        ).decode().rstrip('=')
        
        url = f"https://mermaid.ink/img/{encoded}"
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_png, 'wb') as f:
                f.write(response.content)
            return True, "mermaid.ink"
        return False, None
    except Exception as e:
        return False, str(e)

def try_kroki_png_direct(diagram_content, output_png):
    """Try Kroki PNG endpoint directly"""
    try:
        response = requests.post(
            "https://kroki.io/mermaid/png",
            data=diagram_content.encode('utf-8'),
            timeout=15
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_png, 'wb') as f:
                f.write(response.content)
            return True, "kroki_png"
        return False, None
    except Exception as e:
        return False, str(e)

def download_single_diagram(mmd_file, output_png, attempt=1, max_attempts=3):
    """Download a single diagram with retry"""
    
    try:
        with open(mmd_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    methods = [
        ("mermaid.ink", try_mermaid_ink),
        ("kroki_png", try_kroki_png_direct),
        ("kroki_svg", try_kroki_render_to_file),
    ]
    
    for method_name, method_func in methods:
        try:
            success, result = method_func(content, output_png)
            if success:
                return True, result
        except:
            continue
    
    # Retry logic
    if attempt < max_attempts:
        time.sleep(2)  # Wait before retry
        return download_single_diagram(mmd_file, output_png, attempt + 1, max_attempts)
    
    return False

def main():
    """Main execution"""
    print("=" * 75)
    print("Advanced Diagram Downloader with API Fallbacks")
    print("=" * 75)
    
    # Find .mmd files
    mmd_files = sorted(Path('.').glob('*.mmd'))
    
    if not mmd_files:
        print("\n❌ No .mmd files found")
        return False
    
    print(f"\nFound {len(mmd_files)} diagrams. Starting download...\n")
    
    results = []
    
    for i, mmd_file in enumerate(mmd_files, 1):
        png_file = mmd_file.with_suffix('.png')
        svg_file = mmd_file.with_suffix('.svg')
        
        print(f"[{i}/{len(mmd_files)}] {mmd_file.name:<40}", end=' ')
        sys.stdout.flush()
        
        # Skip if already exists
        if png_file.exists():
            size = os.path.getsize(png_file) / 1024
            print(f"✓ (cached, {size:.1f} KB)")
            results.append((mmd_file.name, True, "cached"))
            continue
        
        # Try to download
        success, method = download_single_diagram(str(mmd_file), str(png_file))
        
        if success:
            if png_file.exists():
                size = os.path.getsize(png_file) / 1024
                print(f"✓ ({method}, {size:.1f} KB)")
                results.append((mmd_file.name, True, method))
            elif svg_file.exists():
                size = os.path.getsize(svg_file) / 1024
                print(f"✓ ({method}, {size:.1f} KB)")
                results.append((mmd_file.name, True, f"{method}(svg)"))
            else:
                print(f"✗ (Failed to save)")
                results.append((mmd_file.name, False, "save_failed"))
        else:
            print(f"✗ (All methods failed)")
            results.append((mmd_file.name, False, "all_failed"))
        
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 75)
    successful = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - successful
    
    print(f"Download Summary: {successful} completed, {failed} failed")
    print("=" * 75)
    
    if successful > 0:
        print("\n✓ Downloaded files:\n")
        for name, ok, method in results:
            if ok:
                base_name = name.replace('.mmd', '')
                if Path(f"{base_name}.png").exists():
                    size = os.path.getsize(f"{base_name}.png") / 1024
                    print(f"  ✓ {base_name}.png ({size:.1f} KB)")
                elif Path(f"{base_name}.svg").exists():
                    size = os.path.getsize(f"{base_name}.svg") / 1024
                    print(f"  ✓ {base_name}.svg ({size:.1f} KB)")
    
    if failed > 0:
        print(f"\n⚠ Failed diagrams ({failed}):")
        for name, ok, method in results:
            if not ok:
                print(f"  ✗ {name} ({method})")
    
    return successful == len(results)

if __name__ == "__main__":
    try:
        import requests
    except:
        print("Installing requests...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    
    success = main()
    sys.exit(0 if success else 1)
