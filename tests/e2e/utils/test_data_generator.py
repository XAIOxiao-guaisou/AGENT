"""
Test Data Generator - 测试数据生成器
===================================

E2E Hell-Level Testing Utility
Generates complex test scenarios for stress testing

Phase 21 E2E Testing
"""

import os
from pathlib import Path
from typing import List, Dict, Set
import random
import string


class TestDataGenerator:
    """
    Test data generator for E2E hell-level tests
    
    Generates:
    - Complex module hierarchies
    - Circular dependencies
    - Large-scale file structures
    """
    
    @staticmethod
    def generate_module_name() -> str:
        """Generate random module name"""
        return f"module_{''.join(random.choices(string.ascii_lowercase, k=8))}"
    
    @staticmethod
    def generate_circular_dependency_project(
        output_dir: Path,
        module_count: int = 50,
        cycle_depth: int = 7
    ) -> Dict[str, str]:
        """
        Generate project with circular dependencies
        
        Args:
            output_dir: Output directory
            module_count: Number of modules to generate
            cycle_depth: Depth of circular dependency chain
        
        Returns:
            Dict mapping file paths to content
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        module_names = [TestDataGenerator.generate_module_name() for _ in range(module_count)]
        
        # Create circular dependency chain
        for i, module_name in enumerate(module_names):
            file_path = output_dir / f"{module_name}.py"
            
            # Import next module in chain (circular)
            next_module = module_names[(i + 1) % cycle_depth]
            
            # Also import some random modules
            random_imports = random.sample(module_names, min(3, len(module_names)))
            
            content = f'''"""
{module_name} - Auto-generated test module
"""

# Circular dependency
from . import {next_module}

# Random dependencies
'''
            
            for imp in random_imports:
                if imp != module_name:
                    content += f"from . import {imp}\n"
            
            content += f'''

class {module_name.title().replace('_', '')}:
    """Test class for {module_name}"""
    
    def __init__(self):
        self.name = "{module_name}"
        self.dependencies = {random_imports}
    
    def process(self):
        """Process method"""
        return f"Processing {{self.name}}"
    
    def get_next(self):
        """Get next in chain"""
        return {next_module}.{next_module.title().replace('_', '')}()


def test_function_{i}():
    """Test function {i}"""
    obj = {module_name.title().replace('_', '')}()
    return obj.process()
'''
            
            files[str(file_path)] = content
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create __init__.py
        init_path = output_dir / "__init__.py"
        init_content = "# Auto-generated test package\n"
        files[str(init_path)] = init_content
        
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        print(f"✅ Generated {len(files)} files with circular dependencies")
        print(f"   Output: {output_dir}")
        print(f"   Modules: {module_count}")
        print(f"   Cycle depth: {cycle_depth}")
        
        return files
    
    @staticmethod
    def generate_large_project(
        output_dir: Path,
        file_count: int = 1000
    ) -> Dict[str, str]:
        """
        Generate large project with many files
        
        Args:
            output_dir: Output directory
            file_count: Number of files to generate
        
        Returns:
            Dict mapping file paths to content
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Create directory structure
        dirs_count = file_count // 20
        for i in range(dirs_count):
            dir_path = output_dir / f"package_{i:03d}"
            dir_path.mkdir(exist_ok=True)
        
        # Generate files
        for i in range(file_count):
            dir_index = i % dirs_count
            dir_path = output_dir / f"package_{dir_index:03d}"
            file_path = dir_path / f"module_{i:04d}.py"
            
            content = f'''"""
module_{i:04d} - Auto-generated test module
File {i+1} of {file_count}
"""

import hashlib
from typing import List, Dict, Any


class Module{i:04d}:
    """Test class {i}"""
    
    def __init__(self):
        self.id = {i}
        self.name = "module_{i:04d}"
        self.data = {{"key": "value_{i}"}}
    
    def compute_hash(self) -> str:
        """Compute hash of module data"""
        data_str = str(self.data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data"""
        return {{
            "module_id": self.id,
            "input": input_data,
            "hash": self.compute_hash()
        }}


def test_function_{i}():
    """Test function {i}"""
    module = Module{i:04d}()
    result = module.process("test_input_{i}")
    return result
'''
            
            files[str(file_path)] = content
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create __init__.py for each package
            init_path = dir_path / "__init__.py"
            if not init_path.exists():
                init_content = f"# Package {dir_index}\n"
                files[str(init_path)] = init_content
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write(init_content)
        
        print(f"✅ Generated {len(files)} files in large project")
        print(f"   Output: {output_dir}")
        print(f"   Files: {file_count}")
        print(f"   Directories: {dirs_count}")
        
        return files


# Example usage
if __name__ == "__main__":
    import tempfile
    
    # Test circular dependency generation
    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n🔄 Testing circular dependency generation...")
        TestDataGenerator.generate_circular_dependency_project(
            Path(tmpdir) / "circular_test",
            module_count=10,
            cycle_depth=5
        )
    
    # Test large project generation
    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n📦 Testing large project generation...")
        TestDataGenerator.generate_large_project(
            Path(tmpdir) / "large_test",
            file_count=100
        )
