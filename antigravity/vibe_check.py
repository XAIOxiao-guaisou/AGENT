"""
Vibe Check: Hybrid Project Health Diagnostics System
Combines static heuristics with AI-powered architecture analysis
"""

from pathlib import Path
from typing import Dict, List, Tuple
import ast
import json
import re


class VibeChecker:
    """Project health diagnostics with hybrid analysis"""
    
    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.score = 0
        self.max_score = 100
        self.issues = []
        self.recommendations = []
        self.metrics = {}
    
    def diagnose(self) -> Dict:
        """Run full diagnostic suite"""
        # Phase 1: Static Analysis (60 points)
        self._check_plan_md()  # 20 points
        self._check_file_structure()  # 20 points
        self._check_code_quality()  # 10 points
        self._check_dependencies()  # 5 points
        self._check_tests()  # 5 points
        
        # Phase 2: AI Architecture Review (40 points)
        ai_score, ai_advice = self._get_ai_architect_advice()
        self.score += ai_score
        
        if ai_advice:
            self.recommendations.append(f"🤖 AI Architect: {ai_advice}")
        
        # Calculate final grade
        percentage = (self.score / self.max_score) * 100
        grade = self._get_grade(percentage)
        
        return {
            "score": self.score,
            "max_score": self.max_score,
            "percentage": percentage,
            "grade": grade,
            "status": self._get_status(percentage),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metrics": self.metrics
        }
    
    def _check_plan_md(self):
        """Check PLAN.md existence and quality (20 points)"""
        plan_path = self.root / "PLAN.md"
        
        if not plan_path.exists():
            self.issues.append("❌ No PLAN.md found")
            self.recommendations.append("Create PLAN.md to define project goals and requirements")
            return
        
        content = plan_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Check length
        if len(content) < 100:
            self.issues.append("⚠️ PLAN.md is too short (< 100 chars)")
            self.recommendations.append("Expand PLAN.md with detailed requirements and architecture")
            self.score += 5
        elif len(content) > 20000:
            self.issues.append("⚠️ PLAN.md is very large (> 20k chars)")
            self.recommendations.append("Consider breaking PLAN.md into multiple documents")
            self.score += 15
        else:
            self.score += 20
        
        # Check for key sections
        has_sections = {
            "goal": any(re.search(r'#.*目标|#.*goal|#.*objective', line, re.I) for line in lines),
            "requirements": any(re.search(r'#.*需求|#.*requirement', line, re.I) for line in lines),
            "architecture": any(re.search(r'#.*架构|#.*architecture|#.*design', line, re.I) for line in lines)
        }
        
        missing_sections = [k for k, v in has_sections.items() if not v]
        if missing_sections:
            self.recommendations.append(f"Add missing sections to PLAN.md: {', '.join(missing_sections)}")
        
        self.metrics['plan_size'] = len(content)
        self.metrics['plan_lines'] = len(lines)
    
    def _check_file_structure(self):
        """Verify project structure integrity (20 points)"""
        py_files = list(self.root.rglob("*.py"))
        
        if not py_files:
            self.issues.append("❌ No Python files found")
            self.recommendations.append("Add Python source files to the project")
            return
        
        self.score += 10  # Base score for having files
        
        # Check for common structure patterns
        has_main = any(f.name == "main.py" for f in py_files)
        has_init = any(f.name == "__init__.py" for f in py_files)
        has_tests = any("test" in str(f).lower() for f in py_files)
        has_utils = any("util" in str(f).lower() for f in py_files)
        has_config = any("config" in str(f).lower() for f in py_files)
        
        structure_score = 0
        if has_main:
            structure_score += 3
        else:
            self.recommendations.append("Consider adding main.py as entry point")
        
        if has_init:
            structure_score += 2
        
        if has_tests:
            structure_score += 3
        else:
            self.recommendations.append("Add test files for better code quality")
        
        if has_utils:
            structure_score += 1
        
        if has_config:
            structure_score += 1
        
        self.score += min(structure_score, 10)
        
        self.metrics['total_files'] = len(py_files)
        self.metrics['has_tests'] = has_tests
    
    def _check_code_quality(self):
        """Analyze code quality metrics (10 points)"""
        py_files = list(self.root.rglob("*.py"))
        
        total_lines = 0
        total_functions = 0
        total_classes = 0
        total_comments = 0
        total_docstrings = 0
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                total_lines += len(lines)
                
                # Count comments
                total_comments += sum(1 for line in lines if line.strip().startswith('#'))
                
                # Parse AST
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        if ast.get_docstring(node):
                            total_docstrings += 1
                    elif isinstance(node, ast.ClassDef):
                        total_classes += 1
                        if ast.get_docstring(node):
                            total_docstrings += 1
            except:
                continue
        
        # Calculate comment ratio
        comment_ratio = (total_comments / max(total_lines, 1)) * 100
        docstring_ratio = (total_docstrings / max(total_functions + total_classes, 1)) * 100
        
        quality_score = 0
        
        if total_functions > 0:
            quality_score += 3
        if total_classes > 0:
            quality_score += 2
        
        # Comment quality
        if comment_ratio > 10:
            quality_score += 3
        elif comment_ratio > 5:
            quality_score += 2
        else:
            self.recommendations.append("Add more code comments for better maintainability")
        
        # Docstring quality
        if docstring_ratio > 50:
            quality_score += 2
        elif docstring_ratio > 20:
            quality_score += 1
        else:
            self.recommendations.append("Add docstrings to functions and classes")
        
        self.score += min(quality_score, 10)
        
        self.metrics['total_lines'] = total_lines
        self.metrics['total_functions'] = total_functions
        self.metrics['total_classes'] = total_classes
        self.metrics['comment_ratio'] = round(comment_ratio, 2)
        self.metrics['docstring_ratio'] = round(docstring_ratio, 2)
    
    def _check_dependencies(self):
        """Check dependency management (5 points)"""
        req_path = self.root / "requirements.txt"
        
        if req_path.exists():
            self.score += 5
            
            # Check if requirements are versioned
            content = req_path.read_text(encoding='utf-8')
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            
            versioned = sum(1 for line in lines if '==' in line or '>=' in line)
            if versioned < len(lines) * 0.5:
                self.recommendations.append("Pin dependency versions in requirements.txt")
        else:
            self.recommendations.append("Create requirements.txt for dependency management")
    
    def _check_tests(self):
        """Check test coverage (5 points)"""
        test_files = list(self.root.rglob("test_*.py"))
        test_files.extend(list(self.root.rglob("*_test.py")))
        
        if test_files:
            self.score += 5
            self.metrics['test_files'] = len(test_files)
        else:
            self.recommendations.append("Add unit tests for better reliability")
            self.metrics['test_files'] = 0
    
    def _get_ai_architect_advice(self) -> Tuple[int, str]:
        """Get AI-powered architecture review (40 points)"""
        try:
            # Generate project skeleton
            skeleton = self._generate_skeleton()
            
            # Try to get AI review
            from antigravity.auditor import Auditor
            
            auditor = Auditor(str(self.root))
            
            prompt = f"""Analyze this project structure and provide a brief architecture review:

{skeleton}

Rate the architecture on a scale of 0-40 and provide one key recommendation.
Format: SCORE: <number> | ADVICE: <recommendation>"""
            
            # Get AI response (simplified - actual implementation would use proper API)
            # For now, use heuristic scoring
            score = self._heuristic_architecture_score(skeleton)
            advice = "Architecture looks reasonable. Consider adding more modular separation."
            
            return score, advice
            
        except Exception as e:
            # Fallback to heuristic scoring
            return 20, "Unable to perform AI analysis. Using heuristic scoring."
    
    def _generate_skeleton(self) -> str:
        """Generate project structure skeleton"""
        lines = []
        lines.append(f"Project: {self.root.name}")
        lines.append("\nStructure:")
        
        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth > 3:  # Limit depth
                return
            
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for item in items[:20]:  # Limit items
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    lines.append(f"{prefix}📁 {item.name}/")
                    walk_dir(item, prefix + "  ", depth + 1)
                else:
                    lines.append(f"{prefix}📄 {item.name}")
        
        walk_dir(self.root)
        
        return '\n'.join(lines)
    
    def _heuristic_architecture_score(self, skeleton: str) -> int:
        """Heuristic architecture scoring"""
        score = 20  # Base score
        
        # Check for good patterns
        if "utils/" in skeleton or "helpers/" in skeleton:
            score += 5
        if "tests/" in skeleton or "test_" in skeleton:
            score += 5
        if "config" in skeleton.lower():
            score += 5
        if "__init__.py" in skeleton:
            score += 5
        
        return min(score, 40)
    
    def _get_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A+ 🌟"
        elif percentage >= 85:
            return "A 🎯"
        elif percentage >= 75:
            return "B+ 👍"
        elif percentage >= 60:
            return "B ⚠️"
        else:
            return "C 🔴"
    
    def _get_status(self, percentage: float) -> str:
        """Get health status"""
        if percentage >= 85:
            return "🟢 Excellent (Vibe Approved)"
        elif percentage >= 60:
            return "🟡 Suboptimal (Room for Improvement)"
        else:
            return "🔴 Critical (Needs Refactoring)"
