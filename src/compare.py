# compare.py - Prop Firm Master Comparison (Extended Schema - ALL Metrics)
# Usage: python src\compare.py
# ONE table, categorized by: Type → Size → Difficulty → Firm → Model
# Includes: Trading rules + Pricing + Firm Profile + Reviews + Business Metrics

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from itertools import groupby

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
ACCOUNT_SIZES = [25000, 50000, 100000, 150000]

# Display labels for model types (aligned with FundedNext)
TYPE_LABELS = {
    "speed": "⚡ SPEED-FOCUSED (Rapid)",
    "discipline": "🎯 DISCIPLINE-FOCUSED (Legacy)",
    "instant": "🚀 INSTANT FUNDING (Bolt)",
    "standard": "📊 STANDARD",
    "aggressive": "🔥 AGGRESSIVE",
    "conservative": "🛡️ CONSERVATIVE"
}

# ─────────────────────────────────────────────────────────────────────
# LOAD & FLATTEN DATA (EXTENDED SCHEMA - ALIGNED WITH FUNDEDNEXT)
# ─────────────────────────────────────────────────────────────────────
def load_firm_data(filepath):
    """Load firm JSON with extended schema support (FundedNext structure)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    firm_profile = data.get('🏢 FIRM PROFILE', {})

    # Normalize restricted_countries — some firms store as CSV string, others as list
    raw_restricted = firm_profile.get('restricted_countries')
    if isinstance(raw_restricted, str):
        if raw_restricted.strip().upper() in ('TBD', 'N/A', 'NONE', ''):
            firm_profile['restricted_countries'] = None
        else:
            firm_profile['restricted_countries'] = [
                c.strip() for c in raw_restricted.split(',') if c.strip()
            ]
    elif not isinstance(raw_restricted, list):
        firm_profile['restricted_countries'] = None

    return {
        'firm_name': data.get('firm_name', 'Unknown'),
        'division': data.get('division', 'Unknown'),
        'last_verified': data.get('last_verified'),
        'verified_by': data.get('verified_by'),
        'source_urls': data.get('source_urls', []),
        # 🏢 FIRM PROFILE (FundedNext structure)
        'firm_profile': firm_profile,
        # 💰 PRICING & OFFERS (FundedNext structure)
        'pricing': data.get('💰 PRICING & OFFERS', {}),
        # 📊 CHALLENGE MODELS (FundedNext structure)
        'models': data.get('📊 CHALLENGE MODELS', []),
        # 🏆 AGGREGATE METRICS (FundedNext structure)
        'aggregate': data.get('🏆 AGGREGATE METRICS', {}),
        'still_tbd': data.get('⚠️ STILL TBD', []),
        'source': filepath.name
    }

def flatten_all_models(firms):
    """Flatten ALL firms/models/sizes with EXTENDED metrics aligned to FundedNext."""
    rows = []
    for firm in firms:
        firm_profile = firm.get('firm_profile', {})
        pricing = firm.get('pricing', {})
        aggregate = firm.get('aggregate', {})
        
        for model in firm['models']:
            trading_rules = model.get('trading_rules', {})
            payout_structure = model.get('payout_structure', {})
            restrictions = model.get('restrictions', {})
            risk_limits = model.get('risk_limits', {})
            passing_reqs = model.get('passing_requirements', {})
            transition = model.get('transition_to_funded', {})
            
            for acc in model.get('account_sizes', []):
                rows.append({
                    # ── CORE IDENTIFIERS ──
                    'firm_name': firm['firm_name'],
                    'division': firm.get('division', ''),
                    'model_name': model.get('model_name', 'Unknown'),
                    'model_type': model.get('model_type', 'unknown'),
                    'account_size': acc.get('size'),
                    'account_size_price': acc.get('price_usd'),
                    'account_size_promo': acc.get('promo_code'),
                    
                    # ── TRADING METRICS (FundedNext specific) ──
                    'profit_target': acc.get('profit_target'),
                    'profit_target_pct': acc.get('profit_target_pct'),
                    'max_loss_limit': acc.get('max_loss_limit'),
                    'max_loss_limit_pct': acc.get('max_loss_limit_pct'),
                    'daily_loss_limit': acc.get('daily_loss_limit'),
                    'daily_loss_limit_pct': acc.get('daily_loss_limit_pct'),
                    'max_contracts': acc.get('max_contracts'),
                    'drawdown_model': acc.get('drawdown_model'),
                    'trailing_drawdown': acc.get('trailing_drawdown'),
                    'minimum_trading_days': passing_reqs.get('min_trading_days'),
                    'consistency_rule_challenge': passing_reqs.get('consistency_rule_active'),
                    'consistency_rule_challenge_pct': passing_reqs.get('consistency_rule_pct'),
                    'consistency_rule_penalty': passing_reqs.get('consistency_rule_penalty'),
                    'benchmark_days_required': passing_reqs.get('benchmark_days_required'),
                    
                    # ── TRADING RULES ──
                    'overnight_holding': trading_rules.get('overnight_holding'),
                    'weekend_holding': trading_rules.get('weekend_holding'),
                    'market_close_time_ct': trading_rules.get('market_close_time_ct'),
                    'market_open_time_ct': trading_rules.get('market_open_time_ct'),
                    'news_trading_allowed': trading_rules.get('news_trading_allowed'),
                    'ea_allowed': trading_rules.get('ea_allowed'),
                    'copy_trading_allowed': trading_rules.get('copy_trading_allowed'),
                    'micro_scalping_allowed': trading_rules.get('micro_scalping_allowed'),
                    'micro_scalping_rule': trading_rules.get('micro_scalping_rule'),
                    'price_limit_rule': trading_rules.get('price_limit_rule'),
                    'inactivity_rule': trading_rules.get('inactivity_rule'),
                    'prohibited_strategies': trading_rules.get('prohibited_strategies', []),
                    
                    # ── RISK LIMITS ──
                    'daily_loss_type': risk_limits.get('daily_loss_type'),
                    'daily_loss_includes_float': risk_limits.get('daily_loss_includes_float'),
                    'max_loss_type': risk_limits.get('max_loss_type'),
                    'max_loss_locks_at_initial': risk_limits.get('max_loss_locks_at_initial'),
                    'drawdown_calculation': risk_limits.get('drawdown_calculation'),
                    
                    # ── PAYOUT STRUCTURE ──
                    'profit_split_pct': payout_structure.get('profit_split_pct'),
                    'withdrawal_frequency_days': payout_structure.get('withdrawal_frequency_days'),
                    'min_withdrawal_amount': payout_structure.get('min_withdrawal_amount'),
                    'min_profit_for_withdrawal': payout_structure.get('min_profit_for_withdrawal'),
                    'benchmark_days_for_payout': payout_structure.get('benchmark_days_for_payout'),
                    'consistency_rule_payout': payout_structure.get('consistency_rule_payout'),
                    'consistency_rule_payout_pct': payout_structure.get('consistency_rule_payout_pct'),
                    'performance_reward_cap': payout_structure.get('performance_reward_cap'),
                    'cap_removal': payout_structure.get('cap_removal'),
                    'first_payout_delay_days': payout_structure.get('first_payout_delay_days'),
                    'payout_guarantee': payout_structure.get('payout_guarantee'),
                    'typical_payout_speed_hours': payout_structure.get('typical_payout_speed_hours'),
                    'buffer_requirement': payout_structure.get('buffer_requirement'),
                    'max_withdrawals_total': payout_structure.get('max_withdrawals_total'),
                    'final_withdrawal': payout_structure.get('final_withdrawal'),
                    
                    # ── TRANSITION TO FUNDED ──
                    'transition_consistency_applies': transition.get('consistency_rule_applies'),
                    'transition_daily_loss_applies': transition.get('daily_loss_limit_applies'),
                    'transition_max_loss_applies': transition.get('max_loss_limit_applies'),
                    'transition_earliest_withdrawal_day': transition.get('earliest_withdrawal_day'),
                    'transition_note': transition.get('note'),
                    
                    # ── RESTRICTIONS ──
                    'inactivity_days_breach': restrictions.get('inactivity_days_breach'),
                    'inactivity_days_funded_breach': restrictions.get('inactivity_days_funded_breach'),
                    'disciplinary_program': restrictions.get('disciplinary_program'),
                    'account_reset_allowed': restrictions.get('account_reset_allowed'),
                    'reset_discount_pct': restrictions.get('reset_discount_pct'),
                    
                    # ── PRICING METRICS (from pricing object) ──
                    'challenge_fees_usd': pricing.get('challenge_fees_usd', {}),
                    'one_time_fee_usd': pricing.get('one_time_fee_usd'),
                    'monthly_subscription_usd': pricing.get('monthly_fees_usd'),
                    'inactivity_fees_usd': pricing.get('inactivity_fees_usd'),
                    'commission_per_contract_open': pricing.get('commission_structure', {}).get('per_contract_open'),
                    'commission_per_contract_close': pricing.get('commission_structure', {}).get('per_contract_close'),
                    'commission_roundtrip': pricing.get('commission_structure', {}).get('roundtrip_commission'),
                    'total_cost_roundtrip': pricing.get('commission_structure', {}).get('total_cost_roundtrip_per_contract'),
                    'commission_note': pricing.get('commission_structure', {}).get('note'),
                    'leverage_futures': pricing.get('leverage_offered', {}).get('futures'),
                    'leverage_note': pricing.get('leverage_offered', {}).get('note'),
                    'spreads': pricing.get('spreads'),
                    'withdrawal_fee_pct': pricing.get('withdrawal_fee_pct'),
                    'active_promotions': pricing.get('active_promotions', []),
                    
                    # ── FIRM PROFILE METRICS ──
                    'country_headquarters': firm_profile.get('country_headquarters'),
                    'year_founded': firm_profile.get('year_founded'),
                    'years_in_operation': firm_profile.get('years_in_operation'),
                    'ceo': firm_profile.get('ceo'),
                    'restricted_countries': firm_profile.get('restricted_countries', []),
                    'platforms_offered': firm_profile.get('platforms_offered', []),
                    'brokers': firm_profile.get('brokers', []),
                    'payment_methods': firm_profile.get('payment_methods', []),
                    'payout_methods': firm_profile.get('payout_methods', []),
                    'max_allocation_per_trader': firm_profile.get('max_allocation_per_trader'),
                    'global_traders_funded': firm_profile.get('global_traders_funded'),
                    'total_payouts_usd': firm_profile.get('total_payouts_usd'),
                    'review_score_avg': firm_profile.get('review_score_avg'),
                    'review_count': firm_profile.get('review_count'),
                    'review_breakdown_pct': firm_profile.get('review_breakdown_pct', {}),
                    'key_differentiators': firm_profile.get('key_differentiators', []),
                    
                    # ── AGGREGATE METRICS ──
                    'overall_difficulty_score': aggregate.get('overall_difficulty_score'),
                    'best_for_beginners': aggregate.get('best_for_beginners'),
                    'best_for_scalpers': aggregate.get('best_for_scalpers'),
                    'best_for_swing_traders': aggregate.get('best_for_swing_traders'),
                    'transparency_score': aggregate.get('transparency_score'),
                    'support_quality_score': aggregate.get('support_quality_score'),
                    'payout_speed_score': aggregate.get('payout_speed_score'),
                    'payout_reliability_score': aggregate.get('payout_reliability_score'),
                    'trading_conditions_score': aggregate.get('trading_conditions_score'),
                    'rule_fairness_score': aggregate.get('rule_fairness_score'),
                    'customer_satisfaction_score': aggregate.get('customer_satisfaction_score'),
                    'top_strengths': aggregate.get('top_strengths', []),
                    'key_concerns': aggregate.get('key_concerns', []),
                    'ideal_trader_profile': aggregate.get('ideal_trader_profile'),
                    'not_ideal_for': aggregate.get('not_ideal_for'),
                    
                    # ── METADATA ──
                    'last_verified': firm.get('last_verified'),
                    'verified_by': firm.get('verified_by'),
                    'still_tbd': firm.get('still_tbd', []),
                })
    return rows

def safe_float(val):
    """Safely convert value to float, return None if can't convert."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def safe_int(val):
    """Safely convert value to int, return None if can't convert."""
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def calculate_difficulty_score(row):
    """Calculate extended difficulty score (lower = easier for trader)."""
    score = 0
    
    # Trading factors
    profit_target = safe_float(row.get('profit_target_pct'))
    if profit_target is not None:
        score += profit_target * 10
    
    max_loss = safe_float(row.get('max_loss_limit_pct'))
    if max_loss is not None:
        score -= max_loss * 10
    
    daily_loss = safe_float(row.get('daily_loss_limit_pct'))
    if daily_loss is not None:
        score -= daily_loss * 5
    
    if row.get('consistency_rule_challenge'):
        score += 20  # Consistency rule adds significant difficulty
    
    # Business factors
    # Check if there's a fee from the account size price
    acc_price = safe_float(row.get('account_size_price'))
    if acc_price is not None and acc_price > 200:
        score += 5  # Higher entry cost = higher barrier
    
    restricted = row.get('restricted_countries')
    if restricted and isinstance(restricted, list) and len(restricted) > 30:
        score += 3  # Many restrictions = less accessible
    
    # Popularity factors
    review_score = safe_float(row.get('review_score_avg'))
    if review_score is not None and review_score >= 4.0:
        score -= 2  # High ratings = more trustworthy
    
    return round(score, 1)

def get_difficulty_badge(score):
    """Return emoji + label for difficulty score."""
    if score < 50:
        return "🟢", "Easy"
    elif score < 70:
        return "🟡", "Medium"
    else:
        return "🔴", "Hard"

# ─────────────────────────────────────────────────────────────────────
# CATEGORIZED MASTER TABLE (EXTENDED OUTPUT)
# ─────────────────────────────────────────────────────────────────────
def fmt(val, suffix='', default='TBD'):
    """Format value with suffix, or default if null."""
    if val is None or val == '':
        return default
    return f"{val}{suffix}"

def fmt_bool(val):
    """Format boolean as ✅/❌/?."""
    if val is True:
        return "✅"
    elif val is False:
        return "❌"
    return "?"

def fmt_list(val, max_items=2):
    """Format list as comma-separated, truncated."""
    if not val:
        return "TBD"
    items = [str(v) for v in val[:max_items]]
    if len(val) > max_items:
        items.append(f"+{len(val)-max_items}")
    return ", ".join(items)

def print_categorized_table(rows):
    """Print ONE table with multi-level categorization + extended metrics."""
    
    print("\n" + "╔" + "═" * 200 + "╗")
    print("║  📊 PROP FIRM MASTER COMPARISON - EXTENDED (ALL METRICS)" + " " * 130 + "║")
    print("╚" + "═" * 200 + "╝")
    print()
    print("🔑 Sort: Model Type → Account Size → Difficulty → Firm → Model")
    print("📦 Includes: Trading rules + Pricing + Firm Profile + Reviews + Business metrics")
    print()
    
    # Sort by: type → size → difficulty → firm → model
    sorted_rows = sorted(rows, key=lambda x: (
        x.get('model_type') or 'zzz',
        (int(x.get('account_size', 0)) if isinstance(x.get('account_size'), (int, float)) else 999999),
        calculate_difficulty_score(x),
        x.get('firm_name', 'Unknown'),
        x.get('model_name', 'Unknown')
    ))
    
    # Compact header (key extended fields only)
    header = (f"{'FIRM':<20} {'MODEL':<22} {'SIZE':<7} {'FEE$':<8} {'SPLIT':<7} "
              f"{'PAYOUT':<8} {'RATING':<7} {'DIFF':<10} {'PLATFORM':<12} {'CONSIST':<8}")
    print("  " + header)
    print("  " + "─" * 198)
    
    # Group by model_type (first level)
    for model_type, type_group in groupby(sorted_rows, key=lambda x: x['model_type'] or 'unknown'):
        type_list = list(type_group)
        type_label = TYPE_LABELS.get(model_type, model_type.upper())
        
        print()
        print(f"  ══ {type_label} {'═' * (190 - len(type_label))}")
        print()
        
        # Group by account_size (second level)
        for size, size_group in groupby(type_list, key=lambda x: x['account_size']):
            size_list = list(size_group)
            size_label = f"${int(size) // 1000}K" if size and isinstance(size, (int, float)) else ("TBD" if not size else str(size))
            
            print(f"    ┌─ {size_label} Account {'─' * 180}")
            print()
            
            # Print each row with extended metrics
            for row in size_list:
                diff_score = calculate_difficulty_score(row)
                diff_emoji, diff_label = get_difficulty_badge(diff_score)
                
                # Format key extended fields
                fee = fmt(row.get('account_size_price'), '$', '—')
                split = fmt(row.get('profit_split_pct'), '%', '—')
                payout = fmt(row.get('first_payout_delay_days'), 'd', '—')
                rating = fmt(row.get('review_score_avg'), '⭐', '—')
                platform = fmt_list(row.get('platforms_offered', []), max_items=1)
                consistency = "✅" if row.get('consistency_rule_challenge') else "❌"
                
                # Compact line format
                line = (f"    {row['firm_name']:<20} {row['model_name']:<22} {size_label:<7} "
                       f"{fee:<8} {split:<7} {payout:<8} {rating:<7} "
                       f"{diff_emoji}{diff_score:<4}({diff_label:<6}) "
                       f"{platform:<12} {consistency:<8}")
                print(line)
            
            print()
    
    # Footer legend
    print("  " + "─" * 198)
    print(f"  {get_difficulty_badge(40)[0]} Easy (<50)  |  {get_difficulty_badge(60)[0]} Medium (50-70)  |  {get_difficulty_badge(80)[0]} Hard (>70)")
    print("  ✅ = Yes/Allowed  |  ❌ = No/Not Allowed  |  ? = TBD  |  — = Data not filled")
    print("  💡 Full extended data saved to JSON output file")
    print()

def print_country_restrictions_analysis(firms):
    """Analyse and print cross-firm country restriction intelligence."""

    print("\n" + "╔" + "═" * 100 + "╗")
    print("║  🌍 COUNTRY RESTRICTION ANALYSIS" + " " * 67 + "║")
    print("╚" + "═" * 100 + "╝")

    # Build per-firm restriction data (deduplicate — one entry per firm)
    firm_restrictions = {}
    for firm in firms:
        name = firm['firm_name']
        restricted = firm.get('firm_profile', {}).get('restricted_countries')
        if name not in firm_restrictions:
            firm_restrictions[name] = set(restricted) if restricted else None

    total_firms = len(firm_restrictions)
    firms_with_data = {k: v for k, v in firm_restrictions.items() if v is not None}
    firms_no_data = [k for k, v in firm_restrictions.items() if v is None]

    # ── Section 1: Per-firm accessibility ranking ──
    print("\n  📊 FIRM ACCESSIBILITY RANKING  (fewest restrictions = most accessible)")
    print("  " + "─" * 70)
    ranked = sorted(firms_with_data.items(), key=lambda x: len(x[1]))
    for firm_name, countries in ranked:
        bar_len = min(40, len(countries) // 2)
        bar = "█" * bar_len
        print(f"  {firm_name:<28} {len(countries):>4} restricted  {bar}")
    for firm_name in firms_no_data:
        print(f"  {firm_name:<28}  N/A  (no restriction data)")

    # ── Section 2: Universally restricted countries ──
    if firms_with_data:
        print(f"\n  🚫 UNIVERSALLY RESTRICTED  (blocked by ALL {len(firms_with_data)} firms with data)")
        print("  " + "─" * 70)
        all_sets = list(firms_with_data.values())
        universal = all_sets[0].intersection(*all_sets[1:]) if len(all_sets) > 1 else all_sets[0]
        if universal:
            for i, country in enumerate(sorted(universal)):
                end = "\n" if (i + 1) % 4 == 0 else ""
                print(f"  {country:<30}", end=end)
            print()
        else:
            print("  (none — no country is blocked by every firm)")

        # ── Section 3: Most commonly restricted (>50% of firms) ──
        print(f"\n  ⚠️  COMMONLY RESTRICTED  (blocked by >50% of firms with data)")
        print("  " + "─" * 70)
        country_count = {}
        for countries in firms_with_data.values():
            for c in countries:
                country_count[c] = country_count.get(c, 0) + 1
        threshold = max(2, len(firms_with_data) // 2)
        common = {c: n for c, n in country_count.items() if n >= threshold and c not in universal}
        if common:
            for country, count in sorted(common.items(), key=lambda x: -x[1]):
                firms_blocking = [f for f, s in firms_with_data.items() if country in s]
                print(f"  {country:<30} {count}/{len(firms_with_data)} firms  ({', '.join(firms_blocking)})")
        else:
            print("  (none beyond universal restrictions)")

        # ── Section 4: Firm-unique restrictions ──
        print(f"\n  🔍 FIRM-UNIQUE RESTRICTIONS  (countries only one firm restricts)")
        print("  " + "─" * 70)
        for firm_name, countries in ranked:
            others = set()
            for other_name, other_countries in firms_with_data.items():
                if other_name != firm_name:
                    others.update(other_countries)
            unique = countries - others
            if unique:
                print(f"  {firm_name}: {', '.join(sorted(unique))}")

    print()


def save_comparison_json(rows, output_path):
    """Save ALL extended data with metadata for filtering."""
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_rows': len(rows),
        'firms': list(set(r['firm_name'] for r in rows)),
        'model_types': list(set(r['model_type'] for r in rows if r['model_type'])),
        'account_sizes': sorted(
            [s for s in set(r['account_size'] for r in rows if r['account_size'])
             if isinstance(s, (int, float))],
        ) + [s for s in set(r['account_size'] for r in rows if r['account_size'])
             if not isinstance(s, (int, float))],
        'countries': list(set(r['country_headquarters'] for r in rows if r['country_headquarters'])),
        'platforms': list(set(p for r in rows for p in (r['platforms_offered'] or []) if p)),
        'payment_methods': list(set(m for r in rows for m in (r['payment_methods'] or []) if m)),
        'full_data': rows,
        '_indexes': {
            'by_firm': {f: [i for i, r in enumerate(rows) if r['firm_name'] == f]
                       for f in set(r['firm_name'] for r in rows)},
            'by_platform': {p: [i for i, r in enumerate(rows) if p in (r['platforms_offered'] or [])]
                           for p in set(pf for r in rows for pf in (r['platforms_offered'] or []))},
            'by_hq_country': {c: [i for i, r in enumerate(rows) if r['country_headquarters'] == c]
                          for c in set(r['country_headquarters'] for r in rows if r['country_headquarters'])},
            'restricted_by_firm': {
                f: sorted(set(c for r in rows if r['firm_name'] == f for c in (r['restricted_countries'] or [])))
                for f in set(r['firm_name'] for r in rows)
            },
            'firms_restricting_country': {},  # populated below
        }
    }
    # Build reverse index: country → list of firms that restrict it
    all_restricted_countries = set(
        c for r in rows for c in (r['restricted_countries'] or [])
    )
    output['_indexes']['firms_restricting_country'] = {
        c: sorted(set(r['firm_name'] for r in rows if c in (r['restricted_countries'] or [])))
        for c in sorted(all_restricted_countries)
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "╔" + "═" * 70 + "╗")
    print("║  🚀 EXTENDED CATEGORIZED COMPARISON ENGINE (ALL METRICS)  ║")
    print("╚" + "═" * 70 + "╝")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load firms
    print("\n📁 Loading firm data with extended schema...")
    firms = []
    for filepath in sorted(DATA_DIR.glob("*.json")):
        try:
            firm = load_firm_data(filepath)
            firms.append(firm)
            model_count = len(firm['models'])
            print(f"   ✅ {firm['firm_name']}: {model_count} model(s) + extended metrics")
        except Exception as e:
            print(f"   ❌ {filepath.name}: {e}")
    
    if not firms:
        print("❌ No valid data found in data/ folder")
        return
    
    # Flatten and process
    all_rows = flatten_all_models(firms)
    
    # Summary stats
    firms_count = len(set(r['firm_name'] for r in all_rows))
    models_count = len(set(f"{r['firm_name']}|{r['model_name']}" for r in all_rows))
    sizes_count = len(set(r['account_size'] for r in all_rows if r['account_size']))
    countries_count = len(set(r['country_headquarters'] for r in all_rows if r['country_headquarters']))
    platforms_count = len(set(p for r in all_rows for p in (r['platforms_offered'] or []) if p))
    
    print(f"\n📊 Total rows: {len(all_rows)}")
    print(f"🏢 Firms: {firms_count}")
    print(f"🔄 Models: {models_count}")
    print(f"📏 Account sizes: {sizes_count}")
    print(f"🌍 Countries: {countries_count}")
    print(f"💻 Platforms: {platforms_count}")
    print()
    
    # Print categorized table (compact view)
    print_categorized_table(all_rows)

    # Print country restriction analysis
    print_country_restrictions_analysis(firms)

    # Save output with ALL extended fields
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_file = OUTPUT_DIR / f"categorized-master-{timestamp}.json"
    save_comparison_json(all_rows, output_file)
    
    print("╔" + "═" * 70 + "╗")
    print("║  ✅ EXTENDED COMPARISON COMPLETE - ALL METRICS INCLUDED   ║")
    print("╚" + "═" * 70 + "╝")
    print()
    print(f"📄 Full extended data: {output_file}")
    print(f"💡 Tip: Open in VS Code → Filter by firm, platform, country, fee, rating, etc.")
    print(f"🔍 Available filters: firm_name, model_type, account_size, country_headquarters,")
    print(f"   platforms_offered, payment_methods, one_time_fee_usd, review_score_avg, etc.")
    print()

if __name__ == "__main__":
    main()

