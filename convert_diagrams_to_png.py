"""
Convert Mermaid diagrams to PNG using Kroki API (no installation required)
Kroki is a free online service that renders diagrams to various formats
"""

import requests
import os
from pathlib import Path
import sys

# Kroki API endpoint for Mermaid diagrams
KROKI_API_URL = "https://kroki.io/mermaid/png"

def convert_mermaid_to_png(mmd_file, output_png):
    """
    Convert a Mermaid diagram to PNG using Kroki API
    
    Args:
        mmd_file: Path to .mmd file
        output_png: Path to save PNG file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the Mermaid diagram
        with open(mmd_file, 'r', encoding='utf-8') as f:
            diagram_content = f.read()
        
        print(f"Converting {os.path.basename(mmd_file)}...", end=' ')
        
        # Send to Kroki API
        response = requests.post(
            KROKI_API_URL,
            data=diagram_content.encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code == 200:
            # Save PNG file
            with open(output_png, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_png)
            print(f"✓ ({file_size:,} bytes)")
            return True
        else:
            print(f"✗ (HTTP {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ (No internet connection)")
        return False
    except requests.exceptions.Timeout:
        print("✗ (Request timeout)")
        return False
    except Exception as e:
        print(f"✗ ({str(e)})")
        return False

def main():
    """Main execution"""
    print("=" * 70)
    print("Mermaid Diagram to PNG Converter (Using Kroki API)")
    print("=" * 70)
    
    # Find all .mmd files in current directory
    mmd_files = list(Path('.').glob('*.mmd'))
    
    if not mmd_files:
        print("❌ No .mmd files found in current directory")
        print("\nExpected files:")
        expected = [
            "1_detailed_system_architecture.mmd",
            "2_component_interaction.mmd",
            "3_deployment_architecture.mmd",
            "4_data_flow.mmd",
            "5_components_dependencies.mmd"
        ]
        for f in expected:
            print(f"  - {f}")
        return False
    
    print(f"\nFound {len(mmd_files)} Mermaid diagram(s):\n")
    
    successful = 0
    failed = 0
    
    # Convert each diagram
    for mmd_file in sorted(mmd_files):
        png_file = mmd_file.with_suffix('.png')
        
        if convert_mermaid_to_png(str(mmd_file), str(png_file)):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Conversion Complete: {successful} successful, {failed} failed")
    print("=" * 70)
    
    if successful > 0:
        print("\n✓ Generated PNG files:")
        for mmd_file in sorted(mmd_files):
            png_file = mmd_file.with_suffix('.png')
            if png_file.exists():
                print(f"  - {png_file.name}")
        return True
    else:
        print("\n❌ No diagrams were converted successfully")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Try again (Kroki API may be temporarily unavailable)")
        print("3. Alternative: Use Mermaid Live Editor (https://mermaid.live)")
        return False

if __name__ == "__main__":
    print("\nChecking dependencies...")
    try:
        import requests
        print("✓ requests library available\n")
    except ImportError:
        print("✗ requests library not found")
        print("\nInstalling requests...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        print("✓ requests installed\n")
    
    success = main()
    sys.exit(0 if success else 1)
