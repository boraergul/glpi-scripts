import subprocess
import sys
import os
import argparse
import time

def run_script(script_path, force=False):
    """Executes a python script with optional --force argument."""
    
    # Resolve absolute path relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.abspath(os.path.join(current_dir, script_path))
    
    script_name = os.path.basename(full_path)
    script_dir = os.path.dirname(full_path)
    
    print(f"\n{'='*60}")
    print(f"STEP: Running {script_name}")
    print(f"PATH: {full_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(full_path):
        print(f"ERROR: Script not found at {full_path}")
        return False
        
    cmd = [sys.executable, script_name]
    if force:
        cmd.append("--force")
        
    try:
        # Run the script with its own directory as cwd to ensure relative imports/config work
        # Pass stdout and stderr to parent to see output in real-time
        result = subprocess.run(cmd, cwd=script_dir, check=True)
        print(f"\n[SUCCESS] {script_name} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FAILURE] {script_name} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to execute {script_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GLPI Onboarding Orchestrator")
    parser.add_argument('--force', action='store_true', help="Execute changes in all scripts (Disable Dry-Run)")
    args = parser.parse_args()
    
    print("Starting GLPI Onboarding Process...")
    print(f"Mode: {'LIVE Execution (Force)' if args.force else 'DRY RUN (Simulation)'}")
    
    # Ordered list of scripts to execute
    # Paths are relative to this script (Script/onboarding/)
    scripts = [
        # 1. Email Rules (Setup Email Receiver Rules) - Rank: 1
        "../rules_email/rules_email.py",
        
        # 2. Undefined Domain Rule (Update Catch-all Rule) - Rank: 2
        "../rules_unknowndomain/rules_unknowndomain.py",
        
        # 3. Major Incident Rules (Priority 6) - Rank: 10
        "../rules_business_incident_major/rules_business_incident_major.py",
        
        # 4. SLA Rules (Incident/Request SLAs) - Rank: 15
        "../rules_business_sla/rules_business_sla.py",
        
        # 5. ITIL Category Rules (Group Assignment) - Rank: 20
        "../rules_business_itilcategory_assign/rules_business_itilcategory_assign.py",
        
        # 6. Business Rules (Default Request Assignments) - Rank: 1 (BR)
        "../rules_business/rules_business.py"
    ]
    
    total = len(scripts)
    failed = 0
    
    for i, script_rel_path in enumerate(scripts, 1):
        print(f"\nProcessing {i}/{total}...")
        if not run_script(script_rel_path, force=args.force):
            print("Stopping execution due to failure.")
            sys.exit(1)
        
        # Small pause for readability
        time.sleep(1)
            
    print(f"\n{'='*60}")
    print("ALL STEPS COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
