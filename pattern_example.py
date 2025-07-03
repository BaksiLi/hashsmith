#!/usr/bin/env python3
"""
HashSmith Pattern Engine Example - Showcasing the compositional design

This demonstrates the beauty and expressiveness of the new pattern-based approach.
"""

import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hashsmith.patterns.engine import P, PAnd, POr, Birthday, Transform


def showcase_syntax_beauty():
    """Demonstrate the beautiful, compositional syntax."""
    
    print("🎨 HashSmith Pattern Engine - Compositional Design")
    print("=" * 60)
    
    # Example 1: Simple composition with transforms
    print("\n1. Basic Pattern with Transforms:")
    print("   Code: P(['crypto']).alter(Transform.LOWER, Transform.CAPITALIZE)")
    
    crypto_pattern = P(["crypto"]).alter(
        Transform.LOWER, Transform.CAPITALIZE
    )
    
    for i, result in enumerate(crypto_pattern.generate(), 1):
        print(f"      {i}. {result}")
    
    # Example 2: Sequential composition
    print("\n2. Sequential Pattern Composition (PAnd):")
    print("   Code: PAnd(P(['hello']).alter(Transform.CAPITALIZE), P(['world', 'crypto']))")
    
    sequential_pattern = PAnd(
        P(["hello"]).alter(Transform.CAPITALIZE),
        P(["world", "crypto"])
    )
    
    for i, result in enumerate(sequential_pattern.generate(), 1):
        print(f"      {i}. {result}")
    
    # Example 3: Alternative patterns
    print("\n3. Alternative Pattern (POr - choose one):")
    print("   Code: PAnd(P(['user']), POr(P(['-', '_']), P(['123'])))")
    
    alternative_pattern = PAnd(
        P(["user"]),
        POr(P(["-", "_"]), P(["123"]))
    )
    
    for i, result in enumerate(alternative_pattern.generate(), 1):
        print(f"      {i}. {result}")
    
    # Example 4: Birthday patterns
    print("\n4. Birthday Pattern (date-based numbers):")
    print("   Code: PAnd(P(['pass']), Birthday(years=[1990], formats=['MMDD']))")
    
    birthday_pattern = PAnd(
        P(["pass"]),
        Birthday(years=[1990], formats=["MMDD"])
    )
    
    count = 0
    for result in birthday_pattern.generate():
        if count < 8:  # Limit output for readability
            print(f"      {count + 1}. {result}")
            count += 1
        else:
            break
    print("      ... (and many more birthday combinations)")
    
    # Example 5: The TP Wallet structure (simplified)
    print("\n5. Complete TP Wallet Structure:")
    print("   This demonstrates the full compositional power:")
    
    tp_pattern = PAnd(
        # Text part: base + combo words
        PAnd(
            P(["qunandyun", "lover"]).alter(Transform.CAPITALIZE, Transform.LOWER),
            P(["", "forever", "love"]).alter(Transform.CAPITALIZE, Transform.LOWER)
        ),
        
        # Numeric part: core numbers or birthdays
        POr(
            P(["369", "801166"]),
            Birthday(years=[1990, 1995], formats=["MMDD"])
        ),
        
        # Suffixes
        P(["", "$", "&"]),
        
        name="tp_wallet_demo"
    )
    
    # Show sample outputs
    print("\n   Sample Generated Passwords:")
    count = 0
    for password in tp_pattern.generate(min_len=5, max_len=25):
        if count < 12:
            print(f"      {count + 1:2d}. {password}")
            count += 1
        else:
            break
    print("      ... (showing first 12 of many combinations)")


def compare_old_vs_new():
    """Compare the old approach vs new pattern-based approach."""
    
    print("\n\n🔄 Old vs New Approach Comparison")
    print("=" * 60)
    
    print("\n📜 OLD APPROACH (Imperative):")
    print("""
    # Hard to read, hard to modify
    for base in ['qun', 'lover']:
        for combo in ['', 'forever']:
            for case in [str.lower, str.capitalize]:
                base_var = case(base)
                combo_var = case(combo) if combo else combo
                for number in ['369', '801166']:
                    for suffix in ['', '$']:
                        password = base_var + combo_var + number + suffix
                        if 8 <= len(password) <= 20:
                            yield password
    """)
    
    print("\n✨ NEW APPROACH (Declarative):")
    print("""
    # Beautiful, readable, maintainable
    PAnd(
        PAnd(
            P(['qun', 'lover']).alter(Transform.LOWER, Transform.CAPITALIZE),
            P(['', 'forever']).alter(Transform.LOWER, Transform.CAPITALIZE)
        ),
        P(['369', '801166']),
        P(['', '$'])
    ).generate(min_len=8, max_len=20)
    """)
    
    print("\n💡 Benefits of New Approach:")
    print("   ✅ Compositional - build complex patterns from simple ones")
    print("   ✅ Declarative - describe WHAT you want, not HOW to get it")
    print("   ✅ Extensible - easy to add new pattern types and transforms")
    print("   ✅ Reusable - patterns can be shared and combined")
    print("   ✅ Readable - self-documenting code structure")
    print("   ✅ Functional - no side effects, pure functions")


if __name__ == "__main__":
    showcase_syntax_beauty()
    compare_old_vs_new()
    
    print("\n\n🎯 Ready to use HashSmith!")
    print("   Run: pdm run python solve.py") 