"""
Antigravity 深度依赖分析器
Deep Dependency Analyzer

功能 / Features:
- AST 解析 import 语句 / Parse import statements using AST
- 构建项目依赖图 / Build project dependency graph
- 最小上下文算法 / Minimal context algorithm
- 支持相对导入 / Support relative imports
"""

import ast
import os
import json
from typing import Dict, List, Set, Optional
from pathlib import Path


class DependencyAnalyzer:
    """
    文件依赖关系分析器
    File Dependency Analyzer
    
    通过 AST 解析构建项目级知识图谱,识别文件间的调用链
    Build project-level knowledge graph through AST parsing
    """
    
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.dependency_graph = {}  # {file: [dependencies]}
        self.reverse_graph = {}     # {file: [dependents]}
        self._cache = {}            # 缓存已解析的文件
    
    def analyze_file(self, file_path: str) -> Set[str]:
        """
        分析单个文件的依赖
        Analyze dependencies of a single file
        
        Args:
            file_path: 文件路径 (相对于 project_root)
        
        Returns:
            Set of file paths this file depends on
        """
        # 检查缓存
        if file_path in self._cache:
            return self._cache[file_path]
        
        dependencies = set()
        full_path = os.path.join(self.project_root, file_path)
        
        if not os.path.exists(full_path):
            return dependencies
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            
            for node in ast.walk(tree):
                # 处理 import xxx
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_file = self._resolve_import(alias.name, file_path)
                        if dep_file:
                            dependencies.add(dep_file)
                
                # 处理 from xxx import yyy
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # 处理相对导入 (from .utils import x)
                        if node.level > 0:
                            dep_file = self._resolve_relative_import(
                                node.module, 
                                node.level, 
                                file_path
                            )
                        else:
                            dep_file = self._resolve_import(node.module, file_path)
                        
                        if dep_file:
                            dependencies.add(dep_file)
        
        except SyntaxError as e:
            print(f"⚠️ Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ Failed to analyze {file_path}: {e}")
        
        # 缓存结果
        self._cache[file_path] = dependencies
        return dependencies
    
    def _resolve_import(self, module_name: str, current_file: str) -> Optional[str]:
        """
        将 import 语句解析为实际文件路径
        Resolve import statement to actual file path
        
        Example:
            "antigravity.utils" -> "antigravity/utils.py"
            "antigravity.api.handler" -> "antigravity/api/handler.py"
        """
        # 转换模块名为路径
        path_parts = module_name.split('.')
        
        # 尝试多种可能的路径
        candidates = [
            os.path.join(*path_parts) + '.py',
            os.path.join(*path_parts, '__init__.py'),
        ]
        
        for candidate in candidates:
            full_path = os.path.join(self.project_root, candidate)
            if os.path.exists(full_path):
                return candidate
        
        return None
    
    def _resolve_relative_import(
        self, 
        module_name: Optional[str], 
        level: int, 
        current_file: str
    ) -> Optional[str]:
        """
        解析相对导入
        Resolve relative import
        
        Example:
            from . import utils (level=1, module=None)
            from ..utils import x (level=2, module="utils")
        
        Args:
            module_name: 模块名 (可能为 None)
            level: 相对层级 (. = 1, .. = 2)
            current_file: 当前文件路径
        
        Returns:
            解析后的文件路径
        """
        # 获取当前文件所在目录
        current_dir = os.path.dirname(current_file)
        
        # 向上回溯 level 层
        for _ in range(level):
            current_dir = os.path.dirname(current_dir)
        
        # 如果有模块名,拼接路径
        if module_name:
            path_parts = module_name.split('.')
            target_path = os.path.join(current_dir, *path_parts)
        else:
            target_path = current_dir
        
        # 尝试多种可能
        candidates = [
            target_path + '.py',
            os.path.join(target_path, '__init__.py'),
        ]
        
        for candidate in candidates:
            if os.path.exists(os.path.join(self.project_root, candidate)):
                return os.path.normpath(candidate).replace('\\', '/')
        
        return None
    
    def build_dependency_graph(self, target_files: Optional[List[str]] = None):
        """
        构建完整的依赖关系图
        Build complete dependency graph
        
        Args:
            target_files: 如果指定,只分析这些文件;否则分析整个项目
        """
        if target_files is None:
            # 扫描整个项目
            target_files = self._scan_project()
        
        print(f"🔍 Analyzing {len(target_files)} files...")
        
        # 构建正向依赖图
        for file_path in target_files:
            deps = self.analyze_file(file_path)
            self.dependency_graph[file_path] = list(deps)
        
        # 构建反向依赖图
        self.reverse_graph = {}
        for file, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in self.reverse_graph:
                    self.reverse_graph[dep] = []
                self.reverse_graph[dep].append(file)
        
        print(f"✅ Dependency graph built: {len(self.dependency_graph)} nodes")
    
    def get_minimal_context(
        self, 
        target_file: str, 
        max_depth: int = 2
    ) -> Set[str]:
        """
        获取最小上下文集合 (手术级精准定位)
        Get minimal context set for a target file
        
        包括:
        1. 目标文件本身
        2. 直接依赖 (imports)
        3. 直接被依赖者 (imported by)
        4. 递归到指定深度
        
        Args:
            target_file: 目标文件路径
            max_depth: 最大递归深度 (默认 2,防止循环依赖)
        
        Returns:
            Set of file paths in minimal context
        """
        context = set()
        visited = set()
        
        def dfs(file, depth, direction="both"):
            """
            DFS 遍历依赖图
            
            Args:
                direction: "forward" (只看依赖), "backward" (只看被依赖), "both"
            """
            if depth > max_depth or file in visited:
                return
            
            visited.add(file)
            context.add(file)
            
            # 添加依赖 (forward)
            if direction in ["forward", "both"]:
                for dep in self.dependency_graph.get(file, []):
                    dfs(dep, depth + 1, "forward")
            
            # 添加被依赖者 (backward)
            if direction in ["backward", "both"]:
                for dependent in self.reverse_graph.get(file, []):
                    dfs(dependent, depth + 1, "backward")
        
        dfs(target_file, 0)
        
        print(f"📊 Minimal context for {target_file}: {len(context)} files")
        return context
    
    def _scan_project(self) -> List[str]:
        """
        扫描项目中所有 Python 文件
        Scan all Python files in project
        """
        python_files = []
        
        # 忽略的目录
        ignore_dirs = {
            '.git', '__pycache__', 'venv', '.venv', 
            'node_modules', '.pytest_cache', 'dist', 'build',
            '.gemini'  # 忽略 Antigravity 自己的工作目录
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_root)
                    python_files.append(rel_path.replace('\\', '/'))
        
        return python_files
    
    def export_graph(self, output_file: str = "dependency_graph.json"):
        """
        导出依赖关系图为 JSON
        Export dependency graph to JSON
        """
        graph_data = {
            "dependencies": self.dependency_graph,
            "reverse_dependencies": self.reverse_graph,
            "stats": {
                "total_files": len(self.dependency_graph),
                "total_edges": sum(len(deps) for deps in self.dependency_graph.values())
            }
        }
        
        output_path = os.path.join(self.project_root, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dependency graph exported to {output_file}")
        return output_path
    
    def get_dependency_chain(self, from_file: str, to_file: str) -> Optional[List[str]]:
        """
        获取两个文件之间的依赖链
        Get dependency chain between two files
        
        Args:
            from_file: 起始文件
            to_file: 目标文件
        
        Returns:
            依赖链路径列表,如果不存在则返回 None
        """
        # BFS 查找最短路径
        from collections import deque
        
        queue = deque([(from_file, [from_file])])
        visited = {from_file}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_file:
                return path
            
            for dep in self.dependency_graph.get(current, []):
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, path + [dep]))
        
        return None
    
    def invalidate_cache(self, file_path: str):
        """
        使缓存失效 (当文件变更时调用)
        Invalidate cache when file changes
        """
        if file_path in self._cache:
            del self._cache[file_path]
            print(f"🔄 Cache invalidated for {file_path}")


if __name__ == "__main__":
    # 测试依赖分析器
    print("🧪 Testing Dependency Analyzer...")
    
    analyzer = DependencyAnalyzer(".")
    
    # 构建依赖图
    analyzer.build_dependency_graph()
    
    # 导出依赖图
    analyzer.export_graph()
    
    # 测试最小上下文
    if analyzer.dependency_graph:
        test_file = list(analyzer.dependency_graph.keys())[0]
        context = analyzer.get_minimal_context(test_file)
        print(f"\n📋 Minimal context for {test_file}:")
        for file in sorted(context):
            print(f"  - {file}")
