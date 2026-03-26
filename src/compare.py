# compare.py - Prop Firm Master Comparison (Categorized Multi-Level Sort)
# Usage: python src\compare.py
# ONE table, categorized by: Type → Size → Difficulty → Firm → Model

import json
from pathlib import Path
from datetime import datetime
from itertools import groupby

# ─────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
ACCOUNT_SIZES = [25000, 50000, 100000]

# Display labels for model types
TYPE_LABELS = {
    "speed": "⚡ SPEED-FOCUSED",
    "discipline": "🎯 DISCIPLINE-FOCUSED",
    "standard": "📊 STANDARD",
    "aggressive": "🔥 AGGRESSIVE",
    "conservative": "🛡️ CONSERVATIVE"
}

# ─────────────────────────────────────────────────────────────────────
# LOAD & FLATTEN DATA
# ─────────────────────────────────────────────────────────────────────
def load_firm_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        'firm_name': data.get('firm_name', 'Unknown'),
        'division': data.get('division', 'Unknown'),
        'models': data.get('challenge_models', []),
        'source': filepath.name
    }

def flatten_all_models(firms):
    """Flatten ALL firms/models/sizes into single list."""
    rows = []
    for firm in firms:
        for model in firm['models']:
            for acc in model.get('account_sizes', []):
                rows.append({
                    'firm_name': firm['firm_name'],
                    'model_name': model.get('model_name', 'Unknown'),
                    'model_type': model.get('model_type', 'unknown'),
                    'account_size': acc.get('size'),
                    'profit_target_pct': acc.get('profit_target_pct'),
                    'max_loss_limit_pct': acc.get('max_loss_limit_pct'),
                    'daily_loss_limit_pct': acc.get('daily_loss_limit_pct'),
                    'overnight_holding': model.get('trading_rules', {}).get('overnight_holding'),
                    'withdrawal_days': model.get('payout_structure', {}).get('withdrawal_frequency_days'),
                    'profit_split_pct': model.get('payout_structure', {}).get('profit_split_pct'),
                    'consistency_rule': model.get('passing_requirements', {}).get('consistency_rule_active'),
                })
    return rows

def calculate_difficulty_score(row):
    """Lower score = easier for trader."""
    score = 0
    if row.get('profit_target_pct'):
        score += row['profit_target_pct'] * 10
    if row.get('max_loss_limit_pct'):
        score -= row['max_loss_limit_pct'] * 10
    if row.get('daily_loss_limit_pct'):
        score -= row['daily_loss_limit_pct'] * 5
    return round(score, 1)

# ─────────────────────────────────────────────────────────────────────
# CATEGORIZED MASTER TABLE
# ─────────────────────────────────────────────────────────────────────
def print_categorized_table(rows):
    """Print ONE table with multi-level categorization."""
    
    print("\n" + "╔" + "═" * 180 + "╗")
    print("║  📊 PROP FIRM MASTER COMPARISON - CATEGORIZED VIEW" + " " * 120 + "║")
    print("╚" + "═" * 180 + "╝")
    print()
    print("🔑 Sort: Model Type → Account Size → Difficulty → Firm → Model")
    print()
    
    # Sort by: type → size → difficulty → firm → model
    sorted_rows = sorted(rows, key=lambda x: (
        x['model_type'],
        x['account_size'] or 999999,
        calculate_difficulty_score(x),
        x['firm_name'],
        x['model_name']
    ))
    
    # Header
    header = f"{'FIRM':<18} {'MODEL':<22} {'SIZE':<8} {'TARGET%':<10} {'MAX LOSS%':<12} {'DAILY%':<10} {'OVERNIGHT':<10} {'PAYOUT':<8} {'SPLIT%':<8} {'CONSIST':<8} {'DIFF':<10}"
    print("  " + header)
    print("  " + "─" * 178)
    
    # Group by model_type (first level)
    for model_type, type_group in groupby(sorted_rows, key=lambda x: x['model_type']):
        type_list = list(type_group)
        type_label = TYPE_LABELS.get(model_type, model_type.upper())
        
        print()
        print(f"  ══ {type_label} {'═' * (170 - len(type_label))}")
        print()
        
        # Group by account_size (second level)
        for size, size_group in groupby(type_list, key=lambda x: x['account_size']):
            size_list = list(size_group)
            size_label = f"${size // 1000}K" if size else "TBD"
            
            print(f"    ┌─ {size_label} Account {'─' * 160}")
            print()
            
            # Group by difficulty range (third level - visual bands)
            for row in size_list:
                diff_score = calculate_difficulty_score(row)
                diff_band = "🟢 Easy" if diff_score < 50 else ("🟡 Medium" if diff_score < 70 else "🔴 Hard")
                
                # Format values
                target = f"{row['profit_target_pct']}%" if row['profit_target_pct'] else "TBD"
                max_loss = f"{row['max_loss_limit_pct']}%" if row['max_loss_limit_pct'] else "TBD"
                daily = f"{row['daily_loss_limit_pct']}%" if row['daily_loss_limit_pct'] else "TBD"
                overnight = "✅" if row['overnight_holding'] else ("❌" if row['overnight_holding'] is False else "?")
                payout = f"{row['withdrawal_days']}d" if row['withdrawal_days'] else "TBD"
                split = f"{row['profit_split_pct']}%" if row['profit_split_pct'] else "TBD"
                consist = "✅" if row['consistency_rule'] else ("❌" if row['consistency_rule'] is False else "?")
                diff_marker = "🟢" if diff_score < 50 else ("🟡" if diff_score < 70 else "🔴")
                
                line = f"    {row['firm_name']:<18} {row['model_name']:<22} {size_label:<8} {target:<10} {max_loss:<12} {daily:<10} {overnight:<10} {payout:<8} {split:<8} {consist:<8} {diff_marker}{diff_score:<6}({diff_band})"
                print(line)
            
            print()
    
    # Footer legend
    print("  " + "─" * 178)
    print("  🟢 Easy (<50)  |  🟡 Medium (50-70)  |  🔴 Hard (>70)")
    print("  ✅ = Yes/Allowed  |  ❌ = No/Not Allowed  |  ? = TBD  |  TBD = Data not filled")
    print()

def save_comparison_json(rows, output_path):
    """Save all data with metadata for filtering."""
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_rows': len(rows),
        'firms': list(set(r['firm_name'] for r in rows)),
        'model_types': list(set(r['model_type'] for r in rows)),
        'account_sizes': list(set(r['account_size'] for r in rows if r['account_size'])),
        'data': rows
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "╔" + "═" * 60 + "╗")
    print("║  🚀 CATEGORIZED MASTER COMPARISON ENGINE    ║")
    print("╚" + "═" * 60 + "╝")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load firms
    print("\n📁 Loading firm data...")
    firms = []
    for filepath in DATA_DIR.glob("*.json"):
        try:
            firm = load_firm_data(filepath)
            firms.append(firm)
            print(f"   ✅ {firm['firm_name']}: {len(firm['models'])} model(s)")
        except Exception as e:
            print(f"   ❌ {filepath.name}: {e}")
    
    if not firms:
        print("❌ No valid data found")
        return
    
    # Flatten and process
    all_rows = flatten_all_models(firms)
    
    print(f"\n📊 Total rows: {len(all_rows)}")
    print(f"🏢 Firms: {len(set(r['firm_name'] for r in all_rows))}")
    print(f"🔄 Model types: {len(set(r['model_type'] for r in all_rows))}")
    print(f"📏 Account sizes: {len(set(r['account_size'] for r in all_rows if r['account_size']))}")
    print()
    
    # Print categorized table
    print_categorized_table(all_rows)
    
    # Save output
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_file = OUTPUT_DIR / f"categorized-master-{timestamp}.json"
    save_comparison_json(all_rows, output_file)
    
    print("╔" + "═" * 60 + "╗")
    print("║  ✅ CATEGORIZED MASTER TABLE COMPLETE       ║")
    print("╚" + "═" * 60 + "╝")
    print()
    print(f"📄 Full data: {output_file}")
    print(f"💡 Tip: Open JSON in VS Code → Filter by model_type, size, or difficulty")
    print()

if __name__ == "__main__":
    main()