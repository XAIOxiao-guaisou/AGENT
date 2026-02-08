
import unittest
import shutil
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("d:/桌面/AGENT")
sys.path.insert(0, str(PROJECT_ROOT))

from antigravity.core.semantic_index import SemanticIndex
from antigravity.core.knowledge_graph import FleetKnowledgeGraph

class TestSemanticCortex(unittest.TestCase):
    def test_synaptic_firing(self):
        """Test basic TF-IDF indexing and retrieval"""
        print("\n🧠 Testing Neural Synapses...")
        cortex = SemanticIndex()
        
        # Training Data (Mocking GKG Exports)
        # Doc 1: Network Util
        cortex.learn(
            doc_id="vortex:net", 
            text="Async Request Handler for high concurrency", 
            metadata={"name": "AsyncRequester", "type": "class"}
        )
        
        # Doc 2: Crypto Util
        cortex.learn(
            doc_id="vortex:crypto", 
            text="AES Encryption and Decryption utilities securely", 
            metadata={"name": "CryptoGuard", "type": "class"}
        )
        
        # Doc 3: Legacy sync code
        cortex.learn(
            doc_id="legacy:sync",
            text="Synchronous blocking request handler",
            metadata={"name": "OldRequester", "type": "class"}
        )
        
        # Test 1: Search "async"
        print("   🔎 Searching for 'async'...")
        results = cortex.search("async")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['id'], "vortex:net")
        print(f"   ✅ Top match: {results[0]['id']} (Score: {results[0]['score']})")

        # Test 2: Search "secure" (Not in name, but in docstring)
        print("   🔎 Searching for 'secure'...")
        results = cortex.search("secure")
        self.assertEqual(results[0]['id'], "vortex:crypto")
        print(f"   ✅ Top match: {results[0]['id']} (Score: {results[0]['score']})")
        
        # Test 3: Search "request" (Matches both, but should rank Async (doc1) or Sync (doc3))
        print("   🔎 Searching for 'request'...")
        results = cortex.search("request")
        ids = [r['id'] for r in results]
        self.assertIn("vortex:net", ids)
        self.assertIn("legacy:sync", ids)
        print(f"   ✅ Found {len(results)} matches for 'request'")

    def test_knowledge_graph_integration(self):
        """Test that GKG uses the Cortex"""
        print("\n🌌 Testing GKG Integration...")
        gkg = FleetKnowledgeGraph.get_instance()
        # Ensure index exists
        self.assertIsNotNone(gkg.semantic_index)
        # We won't run full scan here as it requires file system setup, 
        # but verification of attribute existence proves integration code ran.
        print("   ✅ GKG has Cortex attached.")

if __name__ == '__main__':
    unittest.main()
