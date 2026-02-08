
import unittest
import shutil
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("d:/桌面/AGENT")
sys.path.insert(0, str(PROJECT_ROOT))

from antigravity.core.knowledge_graph import FleetKnowledgeGraph
from antigravity.core.fleet_manager import ProjectFleetManager

TEST_ROOT = Path("d:/桌面/AGENT/test_nexus_workspace")

class TestNeuralNexus(unittest.TestCase):
    def setUp(self):
        if TEST_ROOT.exists():
            shutil.rmtree(TEST_ROOT)
        TEST_ROOT.mkdir(parents=True)
        
        # Mock paths
        self.kg = FleetKnowledgeGraph.get_instance()
        self.kg.graph_path = TEST_ROOT / "fleet_kg.json"
        
        self.fm = ProjectFleetManager.get_instance()
        # Mock projects
        self.fm.projects = {} 

    def test_wisdom_extraction(self):
        print("\n🧠 Testing Neural Nexus Wisdom Extraction...")
        
        # 1. Setup Mock Project
        p_path = TEST_ROOT / "alpha_project"
        p_path.mkdir()
        (p_path / "core").mkdir()
        (p_path / "PLAN.md").write_text("# Alpha Project\nThis is a test project.", encoding='utf-8')
        (p_path / "SIGN_OFF.json").write_text(json.dumps({"version": "1.2.3"}), encoding='utf-8')
        (p_path / "core" / "utils.py").write_text("""
class AlphaUtils:
    '''
    A utility class for Alpha.
    '''
    def helper(self):
        pass

def global_func():
    '''Global helper'''
    pass
""", encoding='utf-8')

        # 2. Extract Wisdom direct
        wisdom = self.kg._extract_project_wisdom(p_path)
        
        print(f"📜 Extracted Wisdom: {json.dumps(wisdom, indent=2)}")
        
        self.assertEqual(wisdom['version'], "1.2.3")
        # Fixed Assertion: Expect body text, not header
        self.assertIn("This is a test project", wisdom['description'])
        self.assertEqual(len(wisdom['exports']), 2)
        self.assertEqual(wisdom['exports'][0]['name'], 'AlphaUtils')
        
    def test_gkg_persistence(self):
        self.kg.knowledge['projects']['test_p'] = {'version': '0.0.1'}
        self.kg.save_graph()
        
        # Reload
        new_kg = FleetKnowledgeGraph()
        new_kg.graph_path = self.kg.graph_path
        new_kg.load_graph()
        self.assertIn('test_p', new_kg.knowledge['projects'])
        print("💾 Persistence Verified")

if __name__ == '__main__':
    unittest.main()
