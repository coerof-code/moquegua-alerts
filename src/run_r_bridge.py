"""
Hybrid R-Python Bridge for Moquegua Alert System
Calls existing R scripts and processes their output
"""

import subprocess
from pathlib import Path
import pandas as pd
import yaml
from datetime import datetime


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_r_alert_extraction():
    """
    Run the R script to extract alerts
    Returns: Path to generated CSV
    """
    print("🔄 Running R alert extraction script...")
    
    # Path to R script
    r_script = Path(__file__).parent.parent.parent / "get_moquegua_warnings.R"
    
    if not r_script.exists():
        print(f"❌ R script not found: {r_script}")
        return None
    
    try:
        # Run R script
        result = subprocess.run(
            ["Rscript", str(r_script)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ R script executed successfully")
            
            # Find generated CSV
            csv_path = r_script.parent / "moquegua_warnings_detailed.csv"
            if csv_path.exists():
                return csv_path
            else:
                print("⚠️  CSV not found at expected location")
                return None
        else:
            print(f"❌ R script failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ R script timed out")
        return None
    except Exception as e:
        print(f"❌ Error running R script: {e}")
        return None


def copy_r_output_to_python_project(r_csv_path, config):
    """Copy R-generated CSV to Python project data folder"""
    if r_csv_path is None:
        return False
    
    # Destination path
    dest_path = Path(config['paths']['output_csv'])
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    import shutil
    shutil.copy2(r_csv_path, dest_path)
    
    print(f"📋 Copied CSV to: {dest_path}")
    return True


def run_r_map_generation():
    """Run the R script to generate maps"""
    print("\n🗺️  Running R map generation script...")
    
    r_script = Path(__file__).parent.parent.parent / "generate_alert_maps.R"
    
    if not r_script.exists():
        print(f"❌ R script not found: {r_script}")
        return False
    
    try:
        result = subprocess.run(
            ["Rscript", str(r_script)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Maps generated successfully")
            return True
        else:
            print(f"❌ Map generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating maps: {e}")
        return False


def copy_r_maps_to_python_project(config):
    """Copy R-generated maps to Python project"""
    import shutil
    
    r_maps_dir = Path(__file__).parent.parent.parent
    dest_maps_dir = Path(config['paths']['output_maps'])
    dest_maps_dir.mkdir(parents=True, exist_ok=True)
    
    # Find and copy PNG files
    copied = 0
    for png_file in r_maps_dir.glob("mapa_aviso_*.png"):
        dest_file = dest_maps_dir / png_file.name
        shutil.copy2(png_file, dest_file)
        copied += 1
    
    if copied > 0:
        print(f"🗺️  Copied {copied} maps to: {dest_maps_dir}")
        return True
    else:
        print("⚠️  No maps found to copy")
        return False


def main():
    """Main execution - bridge between R and Python"""
    print("=" * 60)
    print("🌉 MOQUEGUA ALERT SYSTEM - R-Python Bridge")
    print("=" * 60)
    print(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    config = load_config()
    
    # Step 1: Run R alert extraction
    r_csv_path = run_r_alert_extraction()
    
    if r_csv_path:
        # Step 2: Copy CSV to Python project
        copy_r_output_to_python_project(r_csv_path, config)
        
        # Step 3: Run R map generation
        if run_r_map_generation():
            # Step 4: Copy maps to Python project
            copy_r_maps_to_python_project(config)
    
    print("\n" + "=" * 60)
    print("✅ BRIDGE EXECUTION COMPLETED")
    print("=" * 60)
    print("\n💡 Tip: The Streamlit dashboard will now show the latest data")


if __name__ == "__main__":
    main()
