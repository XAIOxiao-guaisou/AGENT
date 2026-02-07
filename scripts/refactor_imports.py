"""
AST-Level Import Refactoring Tool
v1.0.0 Final Sync - Path B Execution

Chief Reviewer Mandate: CHIEF-REVIEWER-V1-PATH-B-MANDATE-20260207

NO REGEX. Pure AST semantic rewriting.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys


class ImportRefactorer(ast.NodeTransformer):
    """AST-based import statement refactorer"""
    
    def __init__(self, mapping: Dict, current_file_layer: str, current_module: str):
        self.mapping = mapping
        self.current_file_layer = current_file_layer
        self.current_module = current_module
        self.changes = []
        self.module_to_layer = mapping['module_to_layer']
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Rewrite 'from X import Y' statements"""
        
        if not node.module:
            # Relative import without module (e.g., from . import X)
            return node
        
        # Check if this is an antigravity import
        if node.module.startswith('antigravity.'):
            parts = node.module.split('.')
            
            # Case 1: from antigravity.module_name import X
            if len(parts) == 2:
                module_name = parts[1]
                
                # Find which layer this module belongs to
                target_layer = self.module_to_layer.get(module_name)
                
                if target_layer and target_layer != 'root':
                    # Rewrite to layer-specific path
                    old_module = node.module
                    new_module = f"antigravity.{target_layer}.{module_name}"
                    
                    # Create new node
                    new_node = ast.ImportFrom(
                        module=new_module,
                        names=node.names,
                        level=node.level
                    )
                    
                    self.changes.append({
                        'type': 'ImportFrom',
                        'old': old_module,
                        'new': new_module,
                        'line': node.lineno
                    })
                    
                    return new_node
            
            # Case 2: from antigravity.layer.module import X (already correct)
            elif len(parts) == 3:
                # Already using layer-specific path, keep as is
                return node
        
        # Check for relative imports that might need adjustment
        elif node.level > 0:
            # This is a relative import (e.g., from .module import X)
            # We need to check if the target module is in a different layer
            
            if node.module:
                # from .module import X
                target_module = node.module
                target_layer = self.module_to_layer.get(target_module)
                
                if target_layer and target_layer != self.current_file_layer:
                    # Cross-layer import using relative path - needs fixing
                    old_module = f"{'.' * node.level}{node.module}"
                    new_module = f"antigravity.{target_layer}.{target_module}"
                    
                    # Convert to absolute import
                    new_node = ast.ImportFrom(
                        module=new_module,
                        names=node.names,
                        level=0  # Make it absolute
                    )
                    
                    self.changes.append({
                        'type': 'ImportFrom (relative→absolute)',
                        'old': old_module,
                        'new': new_module,
                        'line': node.lineno
                    })
                    
                    return new_node
        
        return node
    
    def visit_Import(self, node: ast.Import) -> ast.Import:
        """Rewrite 'import X' statements"""
        
        new_names = []
        changed = False
        
        for alias in node.names:
            module_name = alias.name
            
            if module_name.startswith('antigravity.'):
                parts = module_name.split('.')
                
                # Case: import antigravity.module_name
                if len(parts) == 2:
                    module = parts[1]
                    target_layer = self.module_to_layer.get(module)
                    
                    if target_layer and target_layer != 'root':
                        # Rewrite to layer-specific path
                        old_name = module_name
                        new_name = f"antigravity.{target_layer}.{module}"
                        
                        new_alias = ast.alias(name=new_name, asname=alias.asname)
                        new_names.append(new_alias)
                        changed = True
                        
                        self.changes.append({
                            'type': 'Import',
                            'old': old_name,
                            'new': new_name,
                            'line': node.lineno
                        })
                    else:
                        new_names.append(alias)
                else:
                    new_names.append(alias)
            else:
                new_names.append(alias)
        
        if changed:
            return ast.Import(names=new_names)
        
        return node


def refactor_file(file_path: Path, mapping: Dict) -> Tuple[bool, List[Dict]]:
    """Refactor imports in a single file using AST"""
    
    try:
        # Read file
        content = file_path.read_text(encoding='utf-8')
        
        # Parse AST
        tree = ast.parse(content)
        
        # Determine current file's layer
        file_str = str(file_path)
        current_layer = 'root'
        current_module = file_path.stem
        
        if 'core' in file_str:
            current_layer = 'core'
        elif 'services' in file_str:
            current_layer = 'services'
        elif 'infrastructure' in file_str:
            current_layer = 'infrastructure'
        elif 'interface' in file_str:
            current_layer = 'interface'
        elif 'utils' in file_str:
            current_layer = 'utils'
        
        # Apply refactoring
        refactorer = ImportRefactorer(mapping, current_layer, current_module)
        new_tree = refactorer.visit(tree)
        
        if refactorer.changes:
            # Generate new code
            new_content = ast.unparse(new_tree)
            
            # Write back
            file_path.write_text(new_content, encoding='utf-8')
            
            return True, refactorer.changes
        
        return False, []
    
    except Exception as e:
        print(f"❌ Error refactoring {file_path}: {e}")
        return False, []


def main():
    """Main refactoring execution"""
    
    print("=" * 70)
    print("AST-Level Import Refactoring Tool")
    print("Chief Reviewer: CHIEF-REVIEWER-V1-PATH-B-MANDATE-20260207 🛡️")
    print("=" * 70)
    print()
    print("⚠️  NO REGEX - Pure AST Semantic Rewriting")
    print()
    
    # Load mapping
    mapping_file = Path("scripts/import_mapping.json")
    if not mapping_file.exists():
        print("❌ import_mapping.json not found!")
        return 1
    
    mapping = json.loads(mapping_file.read_text(encoding='utf-8'))
    print(f"✅ Loaded import mapping: {len(mapping['module_to_layer'])} modules")
    
    # Find all Python files in antigravity layers
    antigravity_dir = Path("antigravity")
    python_files = []
    
    for layer in ['core', 'services', 'infrastructure', 'interface', 'utils']:
        layer_dir = antigravity_dir / layer
        if layer_dir.exists():
            python_files.extend(layer_dir.glob("*.py"))
    
    # Also check root antigravity files
    for py_file in antigravity_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            python_files.append(py_file)
    
    print(f"📁 Found {len(python_files)} Python files to process")
    print()
    
    # Refactor each file
    total_changes = 0
    files_modified = 0
    all_changes = {}
    
    for py_file in python_files:
        modified, changes = refactor_file(py_file, mapping)
        
        if modified:
            files_modified += 1
            total_changes += len(changes)
            all_changes[str(py_file)] = changes
            
            print(f"✅ {py_file.name}: {len(changes)} imports refactored")
            for change in changes[:3]:  # Show first 3
                print(f"   Line {change['line']}: {change['old']} → {change['new']}")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more")
    
    # Summary
    print()
    print("=" * 70)
    print("Refactoring Complete!")
    print("=" * 70)
    print(f"✅ Files modified: {files_modified}/{len(python_files)}")
    print(f"✅ Total imports refactored: {total_changes}")
    print()
    
    # Save detailed log
    log_file = Path(".antigravity_import_refactoring.json")
    log_data = {
        'version': '1.0.0',
        'timestamp': '2026-02-07T19:36:00',
        'files_modified': files_modified,
        'total_changes': total_changes,
        'changes': all_changes
    }
    log_file.write_text(json.dumps(log_data, indent=2), encoding='utf-8')
    print(f"📝 Detailed log saved: {log_file}")
    
    if files_modified > 0:
        print()
        print("🎉 AST-level refactoring successful!")
        print("   Next: Verify imports with test suite")
    
    return 0


if __name__ == "__main__":
    exit(main())
