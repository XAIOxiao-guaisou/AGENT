"""
Antigravity 智能上下文管理器
Intelligent Context Manager

功能 / Features:
- Token 精准计数 / Precise token counting with tiktoken
- 智能上下文优化 / Intelligent context optimization
- 骨架化截断策略 / Skeleton extraction for truncation
- 输出 Token 估算 / Output token estimation
"""

import tiktoken
import re
import ast
from typing import Dict, List, Optional, Tuple


class ContextManager:
    """
    智能上下文管理器
    Intelligent Context Manager
    
    在 Token 限制内最大化有效信息密度
    Maximize information density within token limits
    """
    
    def __init__(self, model: str = "gpt-4", max_tokens: int = 16384):
        """
        初始化上下文管理器
        
        Args:
            model: 模型名称 (用于选择正确的 tokenizer)
            max_tokens: 最大 Token 限制
        """
        self.model = model
        self.max_tokens = max_tokens
        
        # 初始化 tokenizer
        try:
            # DeepSeek 使用 cl100k_base (与 GPT-4 相同)
            self.encoding = tiktoken.get_encoding("cl100k_base")
            print(f"✅ Tokenizer initialized: cl100k_base")
        except Exception as e:
            print(f"⚠️ Failed to load tokenizer: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的 Token 数量
        Count tokens in text
        
        Args:
            text: 要计算的文本
        
        Returns:
            Token 数量
        """
        if self.encoding is None:
            # 降级: 粗略估算 (1 token ≈ 4 chars)
            return len(text) // 4
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            print(f"⚠️ Token counting failed: {e}")
            return len(text) // 4
    
    def optimize_context(
        self, 
        files: Dict[str, str],  # {file_path: content}
        priority_files: Optional[List[str]] = None,
        reserve_tokens: int = 4096  # 为输出预留的 tokens
    ) -> Dict[str, str]:
        """
        优化上下文,确保不超过 Token 限制
        Optimize context to fit within token limit
        
        策略 / Strategy:
        1. 优先保留 priority_files (完整内容)
        2. 其他文件按依赖关系排序
        3. 如果超限,截断或骨架化低优先级文件
        
        Args:
            files: 所有候选文件及其内容
            priority_files: 高优先级文件列表 (目标文件)
            reserve_tokens: 为 LLM 输出预留的 tokens
        
        Returns:
            优化后的文件字典
        """
        available_tokens = self.max_tokens - reserve_tokens
        
        print(f"📊 Optimizing context: {len(files)} files, {available_tokens} tokens available")
        
        # 分类文件
        priority_set = set(priority_files or [])
        priority_content = {}
        normal_content = {}
        
        for file, content in files.items():
            if file in priority_set:
                priority_content[file] = content
            else:
                normal_content[file] = content
        
        # 计算优先级文件的 tokens
        priority_tokens = 0
        for file, content in priority_content.items():
            file_text = self._format_file(file, content)
            priority_tokens += self.count_tokens(file_text)
        
        print(f"📊 Priority files: {len(priority_content)} files, {priority_tokens} tokens")
        
        result = priority_content.copy()
        remaining_tokens = available_tokens - priority_tokens
        
        if remaining_tokens < 0:
            print(f"⚠️ Priority files exceed token limit! Truncating...")
            # 即使优先级文件也需要截断
            return self._truncate_priority_files(priority_content, available_tokens)
        
        # 添加普通文件,直到达到限制
        for file, content in sorted(normal_content.items()):
            file_text = self._format_file(file, content)
            file_tokens = self.count_tokens(file_text)
            
            if file_tokens <= remaining_tokens:
                # 完整保留
                result[file] = content
                remaining_tokens -= file_tokens
                print(f"  ✅ {file}: {file_tokens} tokens (full)")
            else:
                # 尝试骨架化
                skeleton = self._skeletonize(content)
                skeleton_text = self._format_file(file, skeleton)
                skeleton_tokens = self.count_tokens(skeleton_text)
                
                if skeleton_tokens <= remaining_tokens:
                    result[file] = skeleton
                    remaining_tokens -= skeleton_tokens
                    print(f"  📋 {file}: {skeleton_tokens} tokens (skeleton)")
                else:
                    print(f"  ⏭️ {file}: skipped (not enough tokens)")
                break
        
        total_tokens = available_tokens - remaining_tokens
        print(f"📊 Context optimized: {len(result)}/{len(files)} files, {total_tokens}/{available_tokens} tokens ({total_tokens*100//available_tokens}%)")
        
        return result
    
    def _format_file(self, file_path: str, content: str) -> str:
        """格式化文件为上下文字符串"""
        return f"FILE: {file_path}\n```python\n{content}\n```\n"
    
    def _skeletonize(self, content: str) -> str:
        """
        智能"骨架化"算法
        Intelligent skeleton extraction
        
        策略 / Strategy:
        1. 保留所有 import 语句
        2. 保留所有类定义和函数签名
        3. 折叠函数体为 "# ... [Implementation]"
        4. 保留重要的注释和文档字符串
        
        Args:
            content: 原始文件内容
        
        Returns:
            骨架化后的内容
        """
        try:
            # 尝试使用 AST 解析
            return self._skeletonize_ast(content)
        except SyntaxError:
            # 降级到正则表达式
            return self._skeletonize_regex(content)
    
    def _skeletonize_ast(self, content: str) -> str:
        """使用 AST 进行骨架化"""
        tree = ast.parse(content)
        skeleton_lines = []
        
        # 收集所有 import 语句
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.get_source_segment(content, node))
        
        if imports:
            skeleton_lines.extend(imports)
            skeleton_lines.append("")
        
        # 收集类和函数定义
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                skeleton_lines.append(self._extract_class_skeleton(node, content))
            elif isinstance(node, ast.FunctionDef):
                skeleton_lines.append(self._extract_function_signature(node, content))
        
        return "\n".join(skeleton_lines)
    
    def _extract_class_skeleton(self, node: ast.ClassDef, source: str) -> str:
        """提取类的骨架"""
        lines = []
        
        # 类定义行
        class_def = f"class {node.name}"
        if node.bases:
            bases = ", ".join(ast.get_source_segment(source, base) for base in node.bases)
            class_def += f"({bases})"
        class_def += ":"
        lines.append(class_def)
        
        # 文档字符串
        docstring = ast.get_docstring(node)
        if docstring:
            lines.append(f'    """{docstring}"""')
        
        # 方法签名
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                sig = self._extract_function_signature(item, source, indent="    ")
                lines.append(sig)
        
        if len(lines) == 1:
            lines.append("    pass")
        
        return "\n".join(lines)
    
    def _extract_function_signature(self, node: ast.FunctionDef, source: str, indent: str = "") -> str:
        """提取函数签名"""
        lines = []
        
        # 函数定义行
        args_list = []
        for arg in node.args.args:
            args_list.append(arg.arg)
        
        func_def = f"{indent}def {node.name}({', '.join(args_list)}):"
        lines.append(func_def)
        
        # 文档字符串
        docstring = ast.get_docstring(node)
        if docstring:
            # 只保留第一行
            first_line = docstring.split('\n')[0]
            lines.append(f'{indent}    """{first_line}"""')
        
        # 折叠实现
        lines.append(f"{indent}    # ... [Implementation]")
        
        return "\n".join(lines)
    
    def _skeletonize_regex(self, content: str) -> str:
        """使用正则表达式进行骨架化 (降级方案)"""
        lines = content.split('\n')
        skeleton = []
        
        for line in lines:
            stripped = line.strip()
            
            # 保留 import 语句
            if stripped.startswith(('import ', 'from ')):
                skeleton.append(line)
            
            # 保留类定义
            elif stripped.startswith('class '):
                skeleton.append(line)
            
            # 保留函数定义
            elif stripped.startswith('def '):
                skeleton.append(line)
                # 添加折叠标记
                indent = len(line) - len(line.lstrip())
                skeleton.append(' ' * (indent + 4) + '# ... [Implementation]')
            
            # 保留文档字符串的开始
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                skeleton.append(line)
        
        return "\n".join(skeleton)
    
    def _truncate_priority_files(self, files: Dict[str, str], max_tokens: int) -> Dict[str, str]:
        """当优先级文件超限时,进行截断"""
        result = {}
        remaining_tokens = max_tokens
        
        for file, content in files.items():
            skeleton = self._skeletonize(content)
            file_text = self._format_file(file, skeleton)
            tokens = self.count_tokens(file_text)
            
            if tokens <= remaining_tokens:
                result[file] = skeleton
                remaining_tokens -= tokens
            else:
                print(f"⚠️ Skipping priority file {file} (not enough tokens)")
        
        return result
    
    def estimate_output_tokens(self, plan_content: str) -> int:
        """
        估算输出所需的 tokens
        Estimate tokens needed for output
        
        基于 PLAN.md 的复杂度估算
        Based on PLAN.md complexity
        
        Args:
            plan_content: PLAN.md 内容
        
        Returns:
            估算的输出 token 数量
        """
        plan_tokens = self.count_tokens(plan_content)
        
        # 经验公式: 输出 tokens ≈ PLAN tokens * 3
        estimated = plan_tokens * 3
        
        # 最小值和最大值限制
        estimated = max(2048, min(estimated, 8192))
        
        print(f"📊 Estimated output tokens: {estimated} (based on PLAN: {plan_tokens} tokens)")
        
        return estimated
    
    def get_token_stats(self, files: Dict[str, str]) -> Dict[str, int]:
        """
        获取文件的 Token 统计
        Get token statistics for files
        
        Returns:
            {file_path: token_count}
        """
        stats = {}
        for file, content in files.items():
            file_text = self._format_file(file, content)
            stats[file] = self.count_tokens(file_text)
        
        return stats


if __name__ == "__main__":
    # 测试上下文管理器
    print("🧪 Testing Context Manager...")
    
    manager = ContextManager(max_tokens=16384)
    
    # 测试 Token 计数
    test_code = """
def hello():
    print('world')
    
class MyClass:
    def __init__(self):
        pass
"""
    tokens = manager.count_tokens(test_code)
    print(f"\n📊 Test code tokens: {tokens}")
    
    # 测试骨架化
    skeleton = manager._skeletonize(test_code)
    print(f"\n📋 Skeleton:\n{skeleton}")
    
    skeleton_tokens = manager.count_tokens(skeleton)
    print(f"\n📊 Skeleton tokens: {skeleton_tokens} (saved {tokens - skeleton_tokens} tokens)")
    
    # 测试上下文优化
    files = {
        "main.py": test_code * 100,  # 大文件
        "utils.py": test_code * 50,
        "config.py": "CONFIG = {}"
    }
    
    optimized = manager.optimize_context(
        files, 
        priority_files=["main.py"],
        reserve_tokens=4096
    )
    
    print(f"\n✅ Optimized: {len(optimized)}/{len(files)} files retained")
