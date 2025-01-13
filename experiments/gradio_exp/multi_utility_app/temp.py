import json
from typing import Any, Dict, List, Union

def analyze_json(json_input: str) -> Dict[str, Any]:
    """
    Analyzes a JSON string and returns various metrics and information about its structure.
    
    Args:
        json_input (str): JSON string to analyze
        
    Returns:
        Dict containing analysis results
    """
    try:
        # Parse JSON
        parsed_json = json.loads(json_input)
        
        # Initialize analysis results
        analysis = {
            "valid_json": True,
            "type": type(parsed_json).__name__,
            "size_bytes": len(json_input),
            "depth": 0,
            "total_keys": 0,
            "total_values": 0,
            "value_types": {},
            "structure_summary": {}
        }
        
        def analyze_element(element: Any, depth: int = 0) -> None:
            analysis["depth"] = max(analysis["depth"], depth)
            
            if isinstance(element, dict):
                analysis["total_keys"] += len(element)
                analysis["total_values"] += len(element)
                
                for key, value in element.items():
                    value_type = type(value).__name__
                    analysis["value_types"][value_type] = analysis["value_types"].get(value_type, 0) + 1
                    analyze_element(value, depth + 1)
                    
            elif isinstance(element, list):
                analysis["total_values"] += len(element)
                for item in element:
                    value_type = type(item).__name__
                    analysis["value_types"][value_type] = analysis["value_types"].get(value_type, 0) + 1
                    analyze_element(item, depth + 1)
                    
            else:
                value_type = type(element).__name__
                analysis["value_types"][value_type] = analysis["value_types"].get(value_type, 0) + 1
        
        # Start analysis
        analyze_element(parsed_json)
        
        # Create structure summary
        if isinstance(parsed_json, dict):
            analysis["structure_summary"] = {
                "type": "object",
                "top_level_keys": list(parsed_json.keys())
            }
        elif isinstance(parsed_json, list):
            analysis["structure_summary"] = {
                "type": "array",
                "length": len(parsed_json)
            }
        else:
            analysis["structure_summary"] = {
                "type": "primitive",
                "value_type": type(parsed_json).__name__
            }
            
        return analysis
        
    except json.JSONDecodeError as e:
        return {
            "valid_json": False,
            "error": str(e)
        }

def print_json_structure(obj, indent=0, prefix=""):
    """
    Prints a tree-like structure of JSON showing types and some sample values.
    
    Args:
        obj: The JSON object to analyze
        indent (int): Current indentation level
        prefix (str): Prefix for the current line
    """
    indent_str = "  " * indent
    
    if isinstance(obj, dict):
        print(f"{indent_str}{prefix}dict:")
        for key, value in list(obj.items())[:50]:  # Limit to first 50 keys
            print(f"{indent_str}  ├─ {key}:")
            print_json_structure(value, indent + 2)
        if len(obj) > 50:
            print(f"{indent_str}  └─ ... ({len(obj) - 5} more keys)")
            
    elif isinstance(obj, list):
        print(f"{indent_str}{prefix}list ({len(obj)} items):")
        for item in list(obj[:30]):  # Show first 30 items
            print(f"{indent_str}  ├─")
            print_json_structure(item, indent + 2)
        if len(obj) > 30:
            print(f"{indent_str}  └─ ... ({len(obj) - 30} more items)")
            
    else:
        value_preview = str(obj)[:50]
        if len(str(obj)) > 50:
            value_preview += "..."
        print(f"{indent_str}{prefix}{type(obj).__name__}: {value_preview}")

# Example usage
if __name__ == "__main__":
    file_path = "files/twitter-Bookmarks-1736733656627.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sample_json = f.read()
    
    # Parse and print the JSON structure as a tree
    parsed_json = json.loads(sample_json)
    print("\nJSON Structure Tree:")
    print("===================")
    print_json_structure(parsed_json)
