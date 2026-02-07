"""
Context Compressor - 上下文压缩器
================================

Phase 21 Step 2: Dependency-aware semantic compression
Target: >= 92% compression ratio

Dual-Skeleton Strategy:
- 1-hop: Full text (modified + direct dependencies)
- 2-hop: Signatures + docstrings + class attributes
- 3-hop+: Class/def shells only

Phase 21 Enhancements:
- Cross-platform hash normalization (CRLF → LF)
- BFS for circular dependency handling
- Soft fallback for context insufficiency
"""

import ast
import hashlib
import networkx as nx
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass, field
import re
from antigravity.utils.io_utils import safe_read


@dataclass
class CompressionResult:
    """Compression result with metrics"""
    compressed_context: Dict[str, dict]
    original_size: int
    compressed_size: int
    compression_ratio: float
    context_checksum: str
    file_count: int
    hop_distribution: Dict[int, int] = field(default_factory=dict)
    
    @property
    def savings_percent(self) -> float:
        """Calculate savings percentage"""
        return (1 - self.compression_ratio) * 100


class ContextCompressor:
    """
    Dependency-aware semantic compression
    
    Phase 21 Enhancement: Dual-skeleton strategy with >= 92% target
    
    Features:
    - Cross-platform hash normalization
    - BFS-based circular dependency handling
    - Incremental hash caching
    - Soft fallback mechanism
    """
    
    def __init__(self, project_root: str):
        """
        Initialize context compressor
        
        Args:
            project_root: Absolute path to project root
        """
        self.project_root = Path(project_root)
        self.dependency_graph = nx.DiGraph()
        
        # Phase 21 Enhancement: Hash cache for incremental calculation
        self._hash_cache: Dict[str, Tuple[str, float]] = {}  # path → (hash, mtime)
        
        # Compression level configuration
        self.compression_level = 2  # Default: dual-skeleton
        self.max_compression_level = 3  # Maximum compression
    
    def compress_with_dependencies(
        self,
        modified_files: Set[str],
        all_files: Dict[str, str],
        compression_level: Optional[int] = None
    ) -> CompressionResult:
        """
        Compress context based on dependency distance
        
        Phase 21 Dual-Skeleton Strategy:
        - 0-hop (modified): Full text
        - 1-hop (direct deps): Full text
        - 2-hop (indirect): Signatures + docstrings
        - 3-hop+ (distant): Shells only
        
        Args:
            modified_files: Set of modified file paths
            all_files: Dict of all file paths to content
            compression_level: Override default compression level
        
        Returns:
            CompressionResult with compressed context and metrics
        """
        if compression_level is not None:
            self.compression_level = compression_level
        
        print("\n" + "="*70)
        print("🗜️ CONTEXT COMPRESSION - Dependency-Aware Strategy")
        print("="*70)
        print(f"Compression level: {self.compression_level}")
        print(f"Modified files: {len(modified_files)}")
        print(f"Total files: {len(all_files)}")
        
        # Step 1: Build dependency graph
        print("\n📊 Step 1: Building dependency graph...")
        self._build_dependency_graph(all_files)
        print(f"   Graph nodes: {self.dependency_graph.number_of_nodes()}")
        print(f"   Graph edges: {self.dependency_graph.number_of_edges()}")
        
        # Step 2: Calculate hop distances (BFS for circular dependency handling)
        print("\n📏 Step 2: Calculating hop distances (BFS)...")
        hop_distances = self._calculate_hop_distances_bfs(modified_files)
        
        # Distribution analysis
        hop_distribution = {}
        for distance in hop_distances.values():
            hop_distribution[distance] = hop_distribution.get(distance, 0) + 1
        
        print(f"   Modified files (0-hop): {hop_distribution.get(0, 0)}")
        print(f"   Direct deps (1-hop): {hop_distribution.get(1, 0)}")
        print(f"   Indirect deps (2-hop): {hop_distribution.get(2, 0)}")
        print(f"   Distant deps (3-hop+): {sum(v for k, v in hop_distribution.items() if k >= 3)}")
        
        # Step 3: Compress based on distance
        print("\n🗜️ Step 3: Applying dual-skeleton compression...")
        compressed = {}
        original_size = 0
        compressed_size = 0
        
        for file_path, code in all_files.items():
            distance = hop_distances.get(file_path, 999)
            original_size += len(code)
            
            if distance <= 1:
                # Full text for modified + direct dependencies
                compressed[file_path] = {
                    'type': 'full',
                    'content': code,
                    'distance': distance
                }
                compressed_size += len(code)
                
            elif distance == 2:
                # Signatures + docstrings for indirect dependencies
                skeleton = self._extract_signatures_skeleton(code)
                compressed[file_path] = {
                    'type': 'signatures',
                    'content': skeleton,
                    'distance': distance
                }
                compressed_size += len(skeleton)
                
            else:
                # Shells only for distant dependencies
                shell = self._extract_shell_skeleton(code)
                compressed[file_path] = {
                    'type': 'shell',
                    'content': shell,
                    'distance': distance
                }
                compressed_size += len(shell)
        
        # Step 4: Calculate context checksum (with normalization)
        print("\n🔒 Step 4: Calculating context checksum...")
        checksum = self._calculate_context_checksum(compressed)
        
        # Calculate compression ratio
        ratio = compressed_size / original_size if original_size > 0 else 0
        savings = (1 - ratio) * 100
        
        print("\n📊 Compression Results:")
        print(f"   Original size: {original_size:,} bytes")
        print(f"   Compressed size: {compressed_size:,} bytes")
        print(f"   Compression ratio: {ratio:.1%}")
        print(f"   Savings: {savings:.1f}%")
        print(f"   Context checksum: {checksum[:32]}...")
        
        if savings >= 92:
            print(f"   ✅ Target achieved: {savings:.1f}% >= 92%")
        else:
            print(f"   ⚠️ Below target: {savings:.1f}% < 92%")
        
        print("="*70)
        
        return CompressionResult(
            compressed_context=compressed,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=ratio,
            context_checksum=checksum,
            file_count=len(all_files),
            hop_distribution=hop_distribution
        )
    
    def _build_dependency_graph(self, all_files: Dict[str, str]):
        """
        Build dependency graph from import statements
        
        Phase 21 Enhancement: Uses networkx for robust graph operations
        """
        self.dependency_graph.clear()
        
        for file_path, code in all_files.items():
            # Add node
            self.dependency_graph.add_node(file_path)
            
            try:
                tree = ast.parse(code)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        # Extract module names
                        if isinstance(node, ast.ImportFrom) and node.module:
                            # Add edge for dependency
                            dep_path = self._resolve_import_path(node.module, file_path, all_files)
                            if dep_path and dep_path in all_files:
                                self.dependency_graph.add_edge(file_path, dep_path)
                        
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                dep_path = self._resolve_import_path(alias.name, file_path, all_files)
                                if dep_path and dep_path in all_files:
                                    self.dependency_graph.add_edge(file_path, dep_path)
            
            except SyntaxError:
                pass  # Skip files with syntax errors
    
    def _calculate_hop_distances_bfs(self, modified_files: Set[str]) -> Dict[str, int]:
        """
        Calculate hop distance from modified files using BFS
        
        Phase 21 Enhancement: BFS prevents infinite recursion in circular dependencies
        
        Args:
            modified_files: Set of modified file paths
        
        Returns:
            Dict mapping file path to hop distance
        """
        distances = {}
        visited = set()  # Phase 21: Visited set for circular dependency handling
        
        # Modified files are 0-hop
        queue = [(file, 0) for file in modified_files]
        for file in modified_files:
            distances[file] = 0
            visited.add(file)
        
        # BFS traversal
        while queue:
            current, current_distance = queue.pop(0)
            
            # Check all neighbors (files that depend on current)
            for neighbor in self.dependency_graph.predecessors(current):
                if neighbor not in visited:
                    # Lock minimum distance on first visit
                    distances[neighbor] = current_distance + 1
                    visited.add(neighbor)
                    queue.append((neighbor, current_distance + 1))
        
        # Files not in graph get max distance
        for file in self.dependency_graph.nodes():
            if file not in distances:
                distances[file] = 999
        
        return distances
    
    def _extract_signatures_skeleton(self, code: str) -> str:
        """
        Extract signatures + docstrings + class attributes
        
        Phase 21 Dual-Skeleton: 2-hop compression
        
        Preserves:
        - Class definitions with docstrings
        - Method signatures with docstrings
        - Class attributes (type-annotated)
        
        This ensures remote experts can understand the API surface
        without being overwhelmed by implementation details.
        """
        try:
            tree = ast.parse(code)
            skeleton_lines = []
            
            # Process module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                skeleton_lines.append(f'"""{module_docstring}"""')
                skeleton_lines.append('')
            
            # Process top-level nodes
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    # Class definition
                    skeleton_lines.append(f"class {node.name}:")
                    
                    # Docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        skeleton_lines.append(f'    """{docstring}"""')
                    
                    # Class attributes
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            # Type-annotated attribute
                            if hasattr(item.target, 'id'):
                                attr_name = item.target.id
                                # Get annotation
                                annotation = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else '...'
                                skeleton_lines.append(f"    {attr_name}: {annotation}")
                        
                        elif isinstance(item, ast.FunctionDef):
                            # Method signature
                            args = ', '.join(arg.arg for arg in item.args.args)
                            skeleton_lines.append(f"    def {item.name}({args}):")
                            
                            # Method docstring
                            method_docstring = ast.get_docstring(item)
                            if method_docstring:
                                skeleton_lines.append(f'        """{method_docstring}"""')
                            
                            skeleton_lines.append("        ...")
                    
                    skeleton_lines.append('')
                
                elif isinstance(node, ast.FunctionDef):
                    # Top-level function signature
                    args = ', '.join(arg.arg for arg in node.args.args)
                    skeleton_lines.append(f"def {node.name}({args}):")
                    
                    # Docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        skeleton_lines.append(f'    """{docstring}"""')
                    
                    skeleton_lines.append("    ...")
                    skeleton_lines.append('')
            
            return '\n'.join(skeleton_lines)
        
        except SyntaxError:
            return "# Syntax error in file"
    
    def _extract_shell_skeleton(self, code: str) -> str:
        """
        Extract class/def shells only
        
        Phase 21 Dual-Skeleton: 3-hop+ compression
        
        Minimal representation for distant dependencies.
        """
        try:
            tree = ast.parse(code)
            skeleton_lines = []
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    skeleton_lines.append(f"class {node.name}: ...")
                
                elif isinstance(node, ast.FunctionDef):
                    args = ', '.join(arg.arg for arg in node.args.args)
                    skeleton_lines.append(f"def {node.name}({args}): ...")
            
            return '\n'.join(skeleton_lines)
        
        except SyntaxError:
            return "# Syntax error in file"
    
    def _calculate_context_checksum(self, compressed: Dict[str, dict]) -> str:
        """
        Calculate SHA256 checksum of compressed context
        
        Phase 21 Enhancement: Cross-platform normalization
        Normalizes line endings (CRLF → LF) to ensure consistent hashes
        across Windows/Linux environments.
        
        Args:
            compressed: Compressed context dict
        
        Returns:
            SHA256 hex digest
        """
        hasher = hashlib.sha256()
        
        # Sort for consistency
        for file_path in sorted(compressed.keys()):
            if isinstance(compressed[file_path], dict):
                content = compressed[file_path].get('content', '')
                
                # Phase 21 Enhancement: Normalize line endings
                normalized_content = self._normalize_line_endings(content)
                
                hasher.update(normalized_content.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize line endings to LF
        
        Phase 21 Enhancement: Cross-platform hash stability
        
        Converts CRLF (\\r\\n) to LF (\\n) to ensure consistent hashes
        across different operating systems.
        
        Args:
            text: Input text with potentially mixed line endings
        
        Returns:
            Text with normalized LF line endings
        """
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    def _resolve_import_path(
        self, 
        module: str, 
        current_file: str,
        all_files: Dict[str, str]
    ) -> Optional[str]:
        """
        Resolve import module to file path
        
        Step 1.2.1 EMERGENCY FIX: Enhanced to handle simple module names in test scenarios
        
        Args:
            module: Module name (e.g., 'antigravity.utils' or 'module_abc123')
            current_file: Current file path
            all_files: All available files
        
        Returns:
            Resolved file path or None
        """
        # Convert module to path
        module_path = module.replace('.', '/')
        
        # Try common patterns
        candidates = [
            f"{module_path}.py",
            f"{module_path}/__init__.py",
        ]
        
        for candidate in candidates:
            for file_path in all_files.keys():
                if file_path.endswith(candidate):
                    return file_path
        
        # Step 1.2.1: Handle simple module names (e.g., 'module_abc123')
        # For test scenarios where files are named like 'module_abc123.py'
        simple_name = f"{module}.py"
        for file_path in all_files.keys():
            # Match by filename only (not full path)
            if file_path.endswith(f"/{simple_name}") or file_path.endswith(f"\\{simple_name}"):
                return file_path
            # Also try exact match on basename
            if Path(file_path).name == simple_name:
                return file_path
        
        return None
    
    def get_cached_hash(self, file_path: Path) -> str:
        """
        Get cached file hash or calculate new one
        
        Phase 21 Enhancement: Incremental hash caching
        Target: < 500ms audit startup
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 hash of file content (normalized)
        """
        file_path_str = str(file_path)
        mtime = file_path.stat().st_mtime
        
        # Check cache
        if file_path_str in self._hash_cache:
            cached_hash, cached_mtime = self._hash_cache[file_path_str]
            if cached_mtime == mtime:
                return cached_hash
        
        # Calculate and cache
        # v1.0.1 Hotfix: Use safe_read for UTF-8 resilience
        content = safe_read(file_path)
        normalized_content = self._normalize_line_endings(content)
        file_hash = hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
        
        self._hash_cache[file_path_str] = (file_hash, mtime)
        
        return file_hash
    
    def reduce_compression_level(self) -> bool:
        """
        Reduce compression level for soft fallback
        
        Phase 21 Enhancement: Soft fallback mechanism
        
        When remote audit fails due to CONTEXT_INSUFFICIENT,
        automatically reduce compression level and retry.
        
        Returns:
            True if level was reduced, False if already at minimum
        """
        if self.compression_level > 1:
            self.compression_level -= 1
            print(f"\n⚠️ Reducing compression level to {self.compression_level}")
            return True
        return False


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        compressor = ContextCompressor(project_root="./")
        
        # Example: compress context
        modified_files = {"antigravity/utils.py"}
        all_files = {
            "antigravity/utils.py": "def foo(): pass",
            "antigravity/core.py": "from .utils import foo\ndef bar(): pass",
            "antigravity/api.py": "from .core import bar\ndef baz(): pass",
        }
        
        result = compressor.compress_with_dependencies(
            modified_files=modified_files,
            all_files=all_files
        )
        
        print(f"\n✅ Compression complete!")
        print(f"   Savings: {result.savings_percent:.1f}%")
        print(f"   Checksum: {result.context_checksum[:16]}...")
    
    asyncio.run(main())
