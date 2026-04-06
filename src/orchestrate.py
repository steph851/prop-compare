#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.local')

PROJECT_ROOT = os.getenv('PROJECT_ROOT', os.getcwd())
STAGING_DIR = os.getenv('STAGING_DIR', os.path.join(PROJECT_ROOT, 'staging'))
DATA_DIR = os.getenv('DATA_DIR', os.path.join(PROJECT_ROOT, 'data'))
LOGS_DIR = os.getenv('LOGS_DIR', os.path.join(PROJECT_ROOT, 'logs'))

def log_step(msg): print(f'\n▶️  {msg}')
def log_success(msg): print(f'✅ {msg}')
def log_info(msg): print(f'ℹ️  {msg}')
def log_error(msg): print(f'❌ {msg}')

class Orchestrator:
    def __init__(self, firm_name):
        self.firm_name = firm_name
        self.key = firm_name.lower().replace(' ', '_')
    
    def step_1_discover(self):
        log_step('DISCOVERING URLS WITH CLAUDE')
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(PROJECT_ROOT, 'src', 'discover.py'),
                 '--firm', self.firm_name],
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
            )
            
            if result.returncode != 0:
                log_error('Discovery failed')
                return False
            
            discovery = json.loads(result.stdout)
            staging_file = os.path.join(STAGING_DIR, f'{self.key}_discovery.json')
            with open(staging_file, 'w') as f:
                json.dump(discovery, f, indent=2)
            
            log_success('URLs discovered by Claude')
            log_info(f'Found {len(discovery.get("discovered_urls", []))} URLs')
            return True
        except Exception as e:
            log_error(f'Step 1 error: {str(e)}')
            return False
    
    def step_2_extract(self):
        log_step('EXTRACTING DATA WITH CLAUDE')
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(PROJECT_ROOT, 'src', 'extract.py'),
                 self.firm_name],
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
            )
            
            if result.returncode != 0:
                log_error('Extraction failed')
                return False
            
            extracted = json.loads(result.stdout)
            staging_file = os.path.join(STAGING_DIR, f'{self.key}_extracted.json')
            with open(staging_file, 'w') as f:
                json.dump(extracted, f, indent=2)
            
            log_success('Data extracted by Claude')
            return True
        except Exception as e:
            log_error(f'Step 2 error: {str(e)}')
            return False
    
    def step_3_score(self):
        log_step('SCORING WITH CLAUDE')
        try:
            extracted_file = os.path.join(STAGING_DIR, f'{self.key}_extracted.json')
            result = subprocess.run(
                [sys.executable, os.path.join(PROJECT_ROOT, 'src', 'score.py'),
                 extracted_file],
                capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
            )
            
            if result.returncode != 0:
                log_error('Scoring failed')
                return False
            
            scored = json.loads(result.stdout)
            scored_file = os.path.join(STAGING_DIR, f'{self.key}_scored.json')
            with open(scored_file, 'w') as f:
                json.dump(scored, f, indent=2)
            
            log_success('Data scored by Claude')
            difficulty = scored.get('🤖 AI_SCORING', {}).get('difficulty_score', 'N/A')
            log_info(f'Difficulty score: {difficulty}/100')
            return True
        except Exception as e:
            log_error(f'Step 3 error: {str(e)}')
            return False
    
    def step_4_await_approval(self):
        log_step('AWAITING YOUR APPROVAL')
        scored_file = os.path.join(STAGING_DIR, f'{self.key}_scored.json')
        
        log_info(f'Open in VS Code: {scored_file}')
        log_info('Add at TOP: // APPROVED: ' + datetime.now().isoformat())
        log_info('Save and script will detect...')
        
        max_wait = 3600
        start = time.time()
        
        while True:
            try:
                with open(scored_file, 'r') as f:
                    if 'APPROVED:' in f.read():
                        log_success('Approval detected!')
                        return True
                
                if time.time() - start > max_wait:
                    log_error('Approval timeout')
                    return False
                
                time.sleep(5)
            except:
                time.sleep(5)
    
    def step_5_save(self):
        log_step('SAVING TO PRODUCTION')
        try:
            scored_file = os.path.join(STAGING_DIR, f'{self.key}_scored.json')
            with open(scored_file, 'r') as f:
                content = f.read()
            
            lines = [l for l in content.split('\n') if 'APPROVED:' not in l]
            approved_data = json.loads('\n'.join(lines))
            
            prod_file = os.path.join(DATA_DIR, f'{self.key}.json')
            with open(prod_file, 'w') as f:
                json.dump(approved_data, f, indent=2)
            
            log_success('Saved to production')
            
            log_file = os.path.join(LOGS_DIR, 'decisions.log')
            with open(log_file, 'a') as f:
                f.write(f'\n[{datetime.now().isoformat()}] APPROVED: {self.firm_name}\n')
            
            return True
        except Exception as e:
            log_error(f'Step 5 error: {str(e)}')
            return False
    
    def run_full_pipeline(self):
        print(f'\n{"="*70}')
        print(f'PHASE 6 ORCHESTRATOR: {self.firm_name}')
        print(f'{"="*70}')
        
        steps = [
            ('Discover URLs', self.step_1_discover),
            ('Extract Data', self.step_2_extract),
            ('Score Difficulty', self.step_3_score),
            ('Await Approval', self.step_4_await_approval),
            ('Save to Production', self.step_5_save),
        ]
        
        for name, func in steps:
            if not func():
                log_error(f'FAILED: {name}')
                return False
        
        print(f'\n{"="*70}')
        log_success(f'PIPELINE COMPLETE: {self.firm_name}')
        print(f'{"="*70}\n')
        return True

def main():
    if len(sys.argv) < 2:
        print('Usage: orchestrate.py <FirmName>')
        exit(1)
    
    orch = Orchestrator(sys.argv[1])
    exit(0 if orch.run_full_pipeline() else 1)

if __name__ == '__main__':
    main()
