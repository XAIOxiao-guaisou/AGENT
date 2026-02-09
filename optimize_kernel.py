
import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Ensure we can import antigravity
sys.path.insert(0, os.getcwd())

from antigravity.core.local_reasoning import LocalReasoningEngine

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 0
        
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_Try(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

def analyze_method_complexity(node: ast.FunctionDef) -> int:
    visitor = ComplexityVisitor()
    visitor.visit(node)
    return visitor.complexity + 1 # Base complexity is 1

def scan_kernel(target_dir: str = "antigravity/core") -> List[Dict]:
    print(f"🔬 SCANNING KERNEL: {target_dir}...")
    results = []
    
    path = Path(target_dir)
    for file in path.rglob("*.py"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            comp = analyze_method_complexity(method)
                            lines = method.end_lineno - method.lineno
                            
                            results.append({
                                "file": str(file),
                                "class": class_name,
                                "method": method.name,
                                "complexity": comp,
                                "lines": lines,
                                "score": comp * lines # Simple heuristic
                            })
                            
        except Exception as e:
            print(f"⚠️ Error scanning {file}: {e}")
            
    # Sort by score desc
    return sorted(results, key=lambda x: x['score'], reverse=True)

def propose_optimization(candidates: List[Dict]):
    print("\n🏆 TOP 3 COMPLEXITY TARGETS:")
    top_3 = candidates[:3]
    
    engine = LocalReasoningEngine()
    
    for i, target in enumerate(top_3):
        print(f"{i+1}. {target['class']}.{target['method']} (Score: {target['score']})")
        print(f"   Shape: {target['complexity']} cyclomatic / {target['lines']} lines")
        print(f"   File: {target['file']}")
        
        # Simulate Consensus Vote for Refactoring
        proposal = {
            "predicted_lines": int(target['lines'] * 0.85), # Goal: 15% reduction
            "predicted_hash": "optimization_candidate",
            "simulated_content": f"# Optimized version of {target['method']}\n# Logic simplified."
        }
        
        vote = engine.consensus_voter.cast_votes(f"OPT-{i}", proposal)
        print(f"   🗳️ Consensus Vote for Optimization: {vote['status']}")
        if vote['status'] == "CONSENSUS_REACHED":
            print(f"   ✅ APPROVED: Refactoring authorized for >15% reduction.")
        else:
            print(f"   ❌ REJECTED: {vote}")

if __name__ == "__main__":
    candidates = scan_kernel()
    if candidates:
        propose_optimization(candidates)
    else:
        print("🤷 No candidates found.")
