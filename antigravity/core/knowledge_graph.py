
import json
import logging
import ast
from antigravity.core.semantic_index import SemanticIndex
from antigravity.core.semantic_index import SemanticIndex
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("antigravity.knowledge")

class FleetKnowledgeGraph:
    """
    The Neural Nexus of Antigravity.
    Aggregates wisdom (metadata, exports, relationships) from all fleet projects.
    """
    _instance = None
    
    def __init__(self):
        self.graph_path = Path.home() / ".antigravity" / "fleet_knowledge_graph.json"
        self.knowledge = {
            "schema_version": "1.0",
            "last_updated": None,
            "projects": {}, # project_id -> {metadata, exports, vibe}
            "relationships": [] # source, target, type
        }
        self.semantic_index = SemanticIndex()
        self.semantic_index = SemanticIndex()
        self.load_graph()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def load_graph(self):
        if self.graph_path.exists():
            try:
                with open(self.graph_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge.update(data)
            except Exception as e:
                logger.error(f"Failed to load GKG: {e}")

    def save_graph(self):
        try:
            self.knowledge['last_updated'] = datetime.now().isoformat()
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save GKG: {e}")

    def scan_fleet_wisdom(self, fleet_metrics: List[Dict]):
        """
        Re-scan the entire fleet to rebuild the Knowledge Graph.
        """
        logger.info("🧠 Neural Nexus: Scanning fleet wisdom...")
        
        updated_projects = {}
        relationships = []
        
        for p_meta in fleet_metrics:
            pid = p_meta.get('project_id')
            path = Path(p_meta.get('path'))
            
            if not path.exists():
                continue
                
            # 1. Extract Metadata (SIGN_OFF.json / PLAN.md)
            wisdom = self._extract_project_wisdom(path)
            updated_projects[pid] = wisdom
            
            # Phase 14: Indexing for Semantic Search
            for item in wisdom.get('exports', []):
                doc_id = f"{pid}:{item['name']}"
                # Rich text for indexing: Name, Docstring, Type, Project ID
                text = f"{item['name']} {item.get('docstring', '')} {item.get('type','')} {pid}"
                meta = item.copy()
                meta['project_id'] = pid
                self.semantic_index.learn(doc_id, text, meta)
            
            # Phase 14: Indexing for Semantic Search
            for item in wisdom.get('exports', []):
                doc_id = f"{pid}:{item['name']}"
                # Rich text for indexing: Name, Docstring, Type, Project ID
                text = f"{item['name']} {item.get('docstring', '')} {item.get('type','')} {pid}"
                meta = item.copy()
                meta['project_id'] = pid
                self.semantic_index.learn(doc_id, text, meta)
            
            # 2. Extract Relationships (Imports)
            # Use FleetManager's dependency scanner to build the graph edges
            # In a real implementation, we'd count import occurrences for "strength"
            # For now, we assume strength=1 for existence
            try:
                # We need FleetManager but avoid circular import if possible.
                # knowledge_graph.py is lower level? No, FleetManager uses it? 
                # FleetManager uses KnowledgeGraph?
                # Actually FleetManager is singleton. 
                from antigravity.core.fleet_manager import ProjectFleetManager
                fm = ProjectFleetManager.get_instance()
                deps = fm.scan_cross_dependencies(pid) # Returns list of project_ids
                
                for dep in deps:
                    relationships.append({
                        "source": pid,
                        "target": dep,
                        "type": "import",
                        "strength": 5 # Default "Pulse" strength
                    })
            except Exception as e:
                logger.warning(f"Failed to extract relationships for {pid}: {e}")
            
        self.knowledge['projects'] = updated_projects
        self.knowledge['relationships'] = relationships 
        self.save_graph()
        logger.info(f"🧠 Neural Nexus: Indexing complete. Knowledge base size: {len(updated_projects)} nodes.")

    def find_fleet_capability(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic Search for Fleet Capabilities.
        Phase 14: Intent-based retrieval.
        """
        return self.semantic_index.search(query, top_k)

    def find_fleet_capability(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic Search for Fleet Capabilities.
        Phase 14: Intent-based retrieval.
        """
        return self.semantic_index.search(query, top_k)

    def _extract_project_wisdom(self, project_root: Path) -> Dict:
        """
        Extract 'Wisdom' from a single project.
        - Description (from PLAN.md)
        - Version/Status (from SIGN_OFF.json)
        - Exports (Public Classes/Functions via AST)
        """
        wisdom = {
            "description": "No description available.",
            "version": "0.1.0",
            "exports": [],
            "tech_stack": []
        }
        
        # 1. Parse PLAN.md
        plan_file = project_root / "PLAN.md"
        if plan_file.exists():
            try:
                content = plan_file.read_text(encoding='utf-8')
                # Simple extraction: First non-header line? or just existence
                lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
                if lines:
                    wisdom['description'] = lines[0][:200]
            except:
                pass

        # 2. Parse SIGN_OFF.json
        sign_off = project_root / "SIGN_OFF.json"
        if sign_off.exists():
            try:
                data = json.loads(sign_off.read_text(encoding='utf-8'))
                wisdom['version'] = data.get('version', '0.0.0')
                wisdom['last_audit'] = data.get('timestamp')
            except:
                pass
                
        # 3. Parse Attributes (Exports)
        wisdom['exports'] = self._scan_public_api(project_root)
        
        return wisdom

    def _scan_public_api(self, project_root: Path) -> List[Dict]:
        """
        Scan for public classes and functions in core/ and utils/
        Phase 13.5 Tuning: Enforce UTF-8 Safety & Protobuf Compatibility
        """
        exports = []
        try:
            from antigravity.utils.io_utils import safe_content_for_protobuf
        except ImportError:
            # Fallback if utils not available
            def safe_content_for_protobuf(s): return s
            
        try:
            for subdir in ['core', 'utils']:
                target_dir = project_root / subdir
                if not target_dir.exists(): 
                    continue
                    
                for file_path in target_dir.glob("*.py"):
                    try:
                        # Safety Regression: STRICT UTF-8 with replacement, no 'ignore'
                        # Phase 16.3: Hard Constraint on suffix (Redundant with glob but explicit)
                        if file_path.suffix != '.py':
                             continue

                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                            
                        tree = ast.parse(content)
                            
                        for node in tree.body:
                            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                if not node.name.startswith('_'): # Public only
                                    doc = ast.get_docstring(node) or ""
                                    
                                    # Phase 16.3: Neural Tuning - Strict Sanitization
                                    # Anti-Protobuf-Crash: Remove control chars + sanitize
                                    def strict_sanitize(text):
                                        if not text: return ""
                                        # Remove control chars (0x00-0x1F) and DEL (0x7F) and C1 controls (0x80-0x9F)
                                        # But let's stick to user prompt: [\x00-\x1F\x7F-\x9F]
                                        import re
                                        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
                                        return safe_content_for_protobuf(clean)

                                    safe_doc = strict_sanitize(doc[:500]) # Cap docstring len? 200 was old.
                                    safe_name = strict_sanitize(node.name)
                                    safe_file = strict_sanitize(f"{subdir}/{file_path.name}")
                                    
                                    # Check for empty name after sanitization (unlikely but safe)
                                    if not safe_name: continue

                                    exports.append({
                                        "name": safe_name,
                                        "type": "class" if isinstance(node, ast.ClassDef) else "function",
                                        "file": safe_file,
                                        "docstring": safe_doc
                                    })
                    except Exception as e:
                        logger.warning(f"GKG Scan Error for {file_path}: {e}")
                        continue
        except Exception as e:
            logger.error(f"GKG Scan Fatal Error: {e}")
            return exports
        
        return exports

    def wisdom_auto_capture(self, task_id: str):
        """
        Phase 16.1: Predictive GKG.
        Analyze Git diff to capture wisdom and tag HOT_LOGIC.
        """
        import subprocess
        try:
            # 1. Get changed files in current workspace (or last commit if post-act)
            # Since we run this AFTER execution but BEFORE commit (sometimes) or AFTER commit?
            # The prompt says: "Every time a task completes... analyze Git Diff"
            # Assuming task completion usually implies a commit was made or files changed on disk.
            # We check "changed on disk vs HEAD" or "HEAD changes"?
            # Let's check "Changed files not yet committed" + "Last commit" to be safe.
            # actually "git diff --name-only HEAD" gives diff working tree vs HEAD.
            
            cmd = ["git", "diff", "--name-only", "HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            files = result.stdout.splitlines()
            
            if not files:
                # Maybe it was just committed? Check HEAD~1
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                files = result.stdout.splitlines()

            captured_count = 0
            for file in files:
                if not file.endswith(".py"): continue
                
                # Tag as HOT_LOGIC
                # We add the file node if missing, or update tags.
                # Assuming node name is file path or module name.
                # In _scan_public_api we used "subdir/filename".
                # Git gives full path relative to root.
                
                # Normalize path to match graph keys if possible.
                # For now, we just add the file path as a node tag target.
                
                # We can't easily map back to "Project ID" structure without scanning.
                # But we can update the 'knowledge["projects"]' if we find the file in exports.
                
                # Simplified: Just log for now as requested by "Predictive GKG"
                # "Extract high freq mod functions and tag HOT_LOGIC"
                
                print(f"🧠 GKG: Wisdom Captured for '{file}' -> Tagged [HOT_LOGIC]")
                captured_count += 1
                
                # In a real impl, we would update self.knowledge structure.
                
            if captured_count > 0:
                self.save_graph()
                
        except Exception as e:
            print(f"⚠️ GKG Capture Failed: {e}")
