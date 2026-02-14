#!/usr/bin/env python3
"""
Integration Test Helper - Creates integration tests for multi-component interactions.

This tool helps create integration tests that verify how different components
of your application work together.
"""

import argparse
import ast
from pathlib import Path
from typing import Any, Dict, List
from generators.integration_generator import IntegrationTestGenerator as BaseGenerator


class IntegrationTestHelper:
    """Helper for generating integration tests."""
    
    def __init__(self):
        self.generator = BaseGenerator()
        
    def generate(self, source_path: Path, output_path: Path) -> List[str]:
        """Generate integration tests from source code.
        
        Args:
            source_path: Path to source file or directory.
            output_path: Path to output directory for tests.
            
        Returns:
            List of generated test file paths.
        """
        # Parse source files
        if source_path.is_file():
            files = [source_path]
        else:
            files = list(source_path.rglob("*.py"))
        
        analysis = {
            "files": [],
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "args": []
                        }
                        analysis["functions"].append(func_info)
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "methods": []
                        }
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info["methods"].append({"name": item.name})
                        analysis["classes"].append(class_info)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append({
                                "module": alias.name,
                                "name": alias.asname or alias.name,
                                "type": "import"
                            })
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append({
                                "module": f"{module}.{alias.name}" if module else alias.name,
                                "name": alias.asname or alias.name,
                                "type": "from_import"
                            })
                        
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        # Generate tests
        output_path.mkdir(parents=True, exist_ok=True)
        generated = self.generator.generate(analysis, output_path)
        
        return generated


def main():
    parser = argparse.ArgumentParser(description="Integration Test Helper")
    parser.add_argument("--source", required=True, help="Source code path")
    parser.add_argument("--output", default="./tests", help="Output directory")
    
    args = parser.parse_args()
    
    helper = IntegrationTestHelper()
    source = Path(args.source)
    output = Path(args.output)
    
    print(f"Generating integration tests from: {source}")
    print(f"Output directory: {output}")
    
    generated = helper.generate(source, output)
    
    print(f"\nGenerated {len(generated)} test files:")
    for f in generated:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
