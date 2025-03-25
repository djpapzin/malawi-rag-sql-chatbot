from src.query_parser import validate_sector, clean_project_name

def test_sector_validation():
    print("\nTesting sector validation:")
    test_cases = [
        ("healthcare", "Health"),
        ("medical", "Health"),
        ("schools", "Education"),
        ("university", "Education"),
        ("road", "Infrastructure"),
        ("bridge", "Infrastructure"),
        ("power", "Energy"),
        ("electricity", "Energy"),
        ("water supply", "Water"),
        ("sanitation", "Water"),
        ("rural", "Rural Development"),
        ("village", "Rural Development"),
        ("city", "Urban Development"),
        ("town", "Urban Development"),
        ("climate", "Environment"),
        ("forestry", "Environment"),
        ("government", "Governance"),
        ("administration", "Governance")
    ]
    
    for input_sector, expected in test_cases:
        result = validate_sector(input_sector)
        print(f"{input_sector} -> {result} (Expected: {expected})")
        assert result == expected, f"Failed: {input_sector} should map to {expected}, got {result}"

def test_project_name_cleaning():
    print("\nTesting project name cleaning:")
    test_cases = [
        ("The Health Project", "health"),
        ("Education Program", "education"),
        ("A Water Supply Scheme", "water supply"),
        ("The Rural Development Programme", "rural development"),
        ("An Infrastructure Project", "infrastructure"),
        ("Energy Program", "energy"),
        ("The Urban Development Scheme", "urban development"),
        ("Environment Programme", "environment"),
        ("Governance Project", "governance")
    ]
    
    for input_name, expected in test_cases:
        result = clean_project_name(input_name)
        print(f"{input_name} -> {result} (Expected: {expected})")
        assert result == expected, f"Failed: {input_name} should clean to {expected}, got {result}"

if __name__ == "__main__":
    print("Running query parser tests...")
    test_sector_validation()
    test_project_name_cleaning()
    print("\nAll tests passed!") 