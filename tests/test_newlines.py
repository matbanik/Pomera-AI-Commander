"""Test if Python string literals with \n work correctly"""

test_str = "VAR1=value1\nVAR2=value2\nVAR3=value3"
print("Test string:")
print(repr(test_str))
print("\nActual string:")
print(test_str)
print(f"\nLength: {len(test_str)}")
print(f"Contains actual newlines: {chr(10) in test_str}")
