"""
Download Architecture Diagrams as PNG files
Uses Playwright to render Mermaid diagrams and save as PNG
No external dependencies like Node.js required
"""

import os
import sys
from pathlib import Path

def install_playwright():
    """Install playwright if not available"""
    try:
        import playwright
        print("✓ Playwright already installed")
        return True
    except ImportError:
        print("Installing Playwright...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
            print("✓ Playwright installed")
            return True
        except:
            return False

def install_browsers():
    """Install browser support for Playwright"""
    print("Installing browser support...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch()
        print("✓ Browser support installed")
        return True
    except:
        print("⚠ Browser installation may have issues")
        return False

def create_html_with_diagram(mmd_content, title):
    """Create HTML with embedded Mermaid diagram"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: white;
        }}
        .mermaid {{
            max-width: 100%;
            max-height: 100%;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mmd_content}
    </div>
</body>
</html>"""
    return html

def screenshot_diagram(html_content, output_png):
    """Take screenshot of HTML diagram and save as PNG"""
    try:
        from playwright.sync_api import sync_playwright
        
        # Create temporary HTML file
        temp_html = "temp_diagram.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Use Playwright to screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file:///{os.path.abspath(temp_html)}")
            
            # Wait for Mermaid to render
            page.wait_for_load_state("networkidle")
            
            # Get diagram element and take screenshot
            page.screenshot(path=output_png, full_page=True)
            browser.close()
        
        # Clean up temp file
        os.remove(temp_html)
        
        return True
    except Exception as e:
        print(f"  Error: {str(e)}")
        return False

def download_diagrams():
    """Download all diagrams as PNG"""
    print("=" * 70)
    print("Downloading Architecture Diagrams as PNG")
    print("=" * 70)
    
    # Read all .mmd files
    mmd_files = sorted(Path('.').glob('*.mmd'))
    
    if not mmd_files:
        print("\n❌ No .mmd files found")
        return False
    
    print(f"\nFound {len(mmd_files)} diagrams. Converting...\n")
    
    successful = 0
    failed = 0
    
    for mmd_file in mmd_files:
        png_file = mmd_file.with_suffix('.png')
        
        try:
            print(f"  {mmd_file.name:<40}", end=' ')
            sys.stdout.flush()
            
            # Read .mmd content
            with open(mmd_file, 'r', encoding='utf-8') as f:
                mmd_content = f.read()
            
            # Create HTML
            html_content = create_html_with_diagram(mmd_content, mmd_file.stem)
            
            # Screenshot and save
            if screenshot_diagram(html_content, str(png_file)):
                file_size = os.path.getsize(png_file) / 1024
                print(f"✓ ({file_size:.1f} KB)")
                successful += 1
            else:
                print("✗ (Rendering failed)")
                failed += 1
                
        except Exception as e:
            print(f"✗ ({str(e)})")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Download Complete: {successful} successful, {failed} failed")
    print("=" * 70)
    
    if successful > 0:
        print("\n✓ Downloaded PNG files:")
        for mmd_file in mmd_files:
            png_file = mmd_file.with_suffix('.png')
            if png_file.exists():
                size_kb = os.path.getsize(png_file) / 1024
                print(f"  ✓ {png_file.name} ({size_kb:.1f} KB)")
        return True
    else:
        print("\n❌ No diagrams were downloaded")
        return False

def main():
    """Main execution"""
    print("\nChecking dependencies...\n")
    
    # Check requests
    try:
        import requests
        print("✓ requests library")
    except ImportError:
        print("Installing requests...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        print("✓ requests installed")
    
    # Install Playwright
    if not install_playwright():
        print("\n❌ Could not install Playwright")
        print("Trying alternative method...")
        
        # Fallback to simpler approach
        print("\nUsing online API converter as fallback...")
        from simple_kroki_converter import convert_all_diagrams
        return convert_all_diagrams()
    
    print("\nSetting up browser support...")
    install_browsers()
    
    print()
    return download_diagrams()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
