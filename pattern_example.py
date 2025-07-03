from hashsmith.patterns import P, Birthday, Transform

# Build a pattern: [word][numbers][suffix]
# using the new | and & operators
pattern = (
    P(["crypto", "bitcoin"]).alter(Transform.CAPITALIZE) &
    (
        P(["123", "456", "789"]) |
        Birthday(years=[1990, 1995], formats=["MMDD"])
    ) &
    P(["", "!", "$"])
)

# Generate passwords with length constraints
passwords = list(pattern.generate(min_len=6, max_len=15))
print(f"Generated {len(passwords)} passwords.")
print("First 10 passwords:")
for p in passwords[:10]:
    print(p)

# Example output might look like this (due to birthday variations):
# Generated 1482 passwords.
# First 10 passwords:
# crypto123
# crypto123!
# crypto123$
# crypto456
# crypto456!
# crypto456$
# crypto789
# crypto789!
# crypto789$
# crypto0101 