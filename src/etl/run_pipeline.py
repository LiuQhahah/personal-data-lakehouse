#!/usr/bin/env python3
"""
一键运行所有 ETL 流程
"""
import subprocess
import sys
import os

SCRIPTS = [
    ("Transform Silver", "src/etl/transform_silver.py"),
    ("Transform Gold", "src/etl/transform_gold.py"),
]

def run_script(name, script_path):
    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print('='*50)
    
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=os.path.expanduser("~/workspace/personal-lakehouse")
    )
    
    if result.returncode != 0:
        print(f"❌ {name} failed")
        return False
    print(f"✅ {name} complete")
    return True

def main():
    os.chdir(os.path.expanduser("~/workspace/personal-lakehouse"))
    
    print("🚀 Starting Lakehouse ETL Pipeline")
    
    for name, script in SCRIPTS:
        if not run_script(name, script):
            print(f"\n❌ Pipeline failed at {name}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 All pipelines complete!")
    print("="*50)
    
    # 查询结果
    print("\n📊 Query results:")
    os.system(f"{sys.executable} src/etl/query_data.py")

if __name__ == "__main__":
    main()
