"""
RCA Immune System - 免疫系统
============================

Phase 19: Root Cause Analysis and predictive immunity
阶段 19: 根因分析与预测型免疫

Deep Optimization Features:
- Root cause normalization (异常根因归一化)
- Immune memory persistence (免疫记忆持久化)
- Immune fatigue & exponential backoff (免疫疲劳与指数退避)
- Pattern learning (模式学习)
"""

import asyncio
import json
import hashlib
import re
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import traceback


@dataclass
class ErrorFingerprint:
    """
    Error Fingerprint - 错误指纹
    
    Phase 19 Deep Optimization: Normalized error signature
    """
    fingerprint_id: str  # Unique ID for this error pattern
    error_type: str  # Exception type
    error_message_pattern: str  # Normalized error message
    traceback_chain_hash: str  # Abstract hash of traceback chain
    file_path: Optional[str] = None
    function_name: Optional[str] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    occurrence_count: int = 1
    
    def to_dict(self) -> Dict:
        """Serialize fingerprint"""
        return {
            'fingerprint_id': self.fingerprint_id,
            'error_type': self.error_type,
            'error_message_pattern': self.error_message_pattern,
            'traceback_chain_hash': self.traceback_chain_hash,
            'file_path': self.file_path,
            'function_name': self.function_name,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'occurrence_count': self.occurrence_count
        }


@dataclass
class HealingPrescription:
    """
    Healing Prescription - 治愈处方
    
    Phase 19 Deep Optimization: Successful healing action for reuse
    """
    prescription_id: str
    fingerprint_id: str  # Associated error fingerprint
    healing_action: str  # Type of healing applied
    code_patch: Optional[str] = None  # Code changes made
    success_rate: float = 1.0  # Success rate (0.0 - 1.0)
    times_applied: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    last_applied: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Serialize prescription"""
        return {
            'prescription_id': self.prescription_id,
            'fingerprint_id': self.fingerprint_id,
            'healing_action': self.healing_action,
            'code_patch': self.code_patch,
            'success_rate': self.success_rate,
            'times_applied': self.times_applied,
            'created_at': self.created_at.isoformat(),
            'last_applied': self.last_applied.isoformat()
        }


class ErrorNormalizer:
    """
    Error Normalizer - 错误归一化器
    
    Phase 19 Deep Optimization: Normalize errors for pattern matching
    """
    
    @staticmethod
    def normalize_error_message(error_message: str) -> str:
        """
        Normalize error message by removing dynamic values / 归一化错误消息
        
        Phase 19 Deep Optimization: Remove variable names, memory addresses, etc.
        
        Args:
            error_message: Raw error message
            
        Returns:
            Normalized error message pattern
        """
        # Remove memory addresses (0x...)
        normalized = re.sub(r'0x[0-9a-fA-F]+', '0x<ADDR>', error_message)
        
        # Remove file paths (keep only filename)
        normalized = re.sub(r'[A-Za-z]:\\[^:]+\\([^\\]+)', r'\1', normalized)
        normalized = re.sub(r'/[^/]+/([^/]+)', r'\1', normalized)
        
        # Remove line numbers
        normalized = re.sub(r'line \d+', 'line <N>', normalized)
        
        # Remove specific variable names in quotes
        normalized = re.sub(r"'[a-zA-Z_][a-zA-Z0-9_]*'", "'<VAR>'", normalized)
        
        # Remove numeric values
        normalized = re.sub(r'\b\d+\b', '<NUM>', normalized)
        
        return normalized
    
    @staticmethod
    def extract_traceback_chain(tb_str: str) -> List[str]:
        """
        Extract traceback chain from traceback string / 提取回溯链
        
        Args:
            tb_str: Traceback string
            
        Returns:
            List of function calls in traceback
        """
        chain = []
        
        # Extract function names from traceback
        for line in tb_str.split('\n'):
            # Match lines like: "  File "...", line X, in function_name"
            match = re.search(r'in ([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if match:
                chain.append(match.group(1))
        
        return chain
    
    @staticmethod
    def hash_traceback_chain(chain: List[str]) -> str:
        """
        Create abstract hash of traceback chain / 创建回溯链的抽象哈希
        
        Args:
            chain: List of function names in traceback
            
        Returns:
            Hash of the chain
        """
        chain_str = '->'.join(chain)
        return hashlib.md5(chain_str.encode()).hexdigest()[:16]


class ImmuneMemoryDatabase:
    """
    Immune Memory Database - 免疫记忆数据库
    
    Phase 19 Deep Optimization: Persistent storage for error patterns and healing actions
    """
    
    def __init__(self, db_path: str):
        """
        Initialize immune memory database
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Error fingerprints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_fingerprints (
                fingerprint_id TEXT PRIMARY KEY,
                error_type TEXT,
                error_message_pattern TEXT,
                traceback_chain_hash TEXT,
                file_path TEXT,
                function_name TEXT,
                first_seen TEXT,
                last_seen TEXT,
                occurrence_count INTEGER
            )
        ''')
        
        # Healing prescriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS healing_prescriptions (
                prescription_id TEXT PRIMARY KEY,
                fingerprint_id TEXT,
                healing_action TEXT,
                code_patch TEXT,
                success_rate REAL,
                times_applied INTEGER,
                created_at TEXT,
                last_applied TEXT,
                FOREIGN KEY (fingerprint_id) REFERENCES error_fingerprints(fingerprint_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_fingerprint(self, fingerprint: ErrorFingerprint):
        """Store or update error fingerprint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if fingerprint exists
        cursor.execute(
            'SELECT occurrence_count FROM error_fingerprints WHERE fingerprint_id = ?',
            (fingerprint.fingerprint_id,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing fingerprint
            cursor.execute('''
                UPDATE error_fingerprints
                SET last_seen = ?, occurrence_count = ?
                WHERE fingerprint_id = ?
            ''', (fingerprint.last_seen.isoformat(), fingerprint.occurrence_count, fingerprint.fingerprint_id))
        else:
            # Insert new fingerprint
            cursor.execute('''
                INSERT INTO error_fingerprints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fingerprint.fingerprint_id,
                fingerprint.error_type,
                fingerprint.error_message_pattern,
                fingerprint.traceback_chain_hash,
                fingerprint.file_path,
                fingerprint.function_name,
                fingerprint.first_seen.isoformat(),
                fingerprint.last_seen.isoformat(),
                fingerprint.occurrence_count
            ))
        
        conn.commit()
        conn.close()
    
    def find_matching_fingerprint(self, fingerprint_id: str) -> Optional[ErrorFingerprint]:
        """Find matching error fingerprint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM error_fingerprints WHERE fingerprint_id = ?',
            (fingerprint_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return ErrorFingerprint(
                fingerprint_id=result[0],
                error_type=result[1],
                error_message_pattern=result[2],
                traceback_chain_hash=result[3],
                file_path=result[4],
                function_name=result[5],
                first_seen=datetime.fromisoformat(result[6]),
                last_seen=datetime.fromisoformat(result[7]),
                occurrence_count=result[8]
            )
        
        return None
    
    def store_prescription(self, prescription: HealingPrescription):
        """Store or update healing prescription"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if prescription exists
        cursor.execute(
            'SELECT times_applied FROM healing_prescriptions WHERE prescription_id = ?',
            (prescription.prescription_id,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing prescription
            cursor.execute('''
                UPDATE healing_prescriptions
                SET success_rate = ?, times_applied = ?, last_applied = ?
                WHERE prescription_id = ?
            ''', (prescription.success_rate, prescription.times_applied,
                  prescription.last_applied.isoformat(), prescription.prescription_id))
        else:
            # Insert new prescription
            cursor.execute('''
                INSERT INTO healing_prescriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prescription.prescription_id,
                prescription.fingerprint_id,
                prescription.healing_action,
                prescription.code_patch,
                prescription.success_rate,
                prescription.times_applied,
                prescription.created_at.isoformat(),
                prescription.last_applied.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def find_prescriptions_for_fingerprint(self, fingerprint_id: str) -> List[HealingPrescription]:
        """Find all healing prescriptions for an error fingerprint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM healing_prescriptions WHERE fingerprint_id = ? ORDER BY success_rate DESC',
            (fingerprint_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        prescriptions = []
        for result in results:
            prescription = HealingPrescription(
                prescription_id=result[0],
                fingerprint_id=result[1],
                healing_action=result[2],
                code_patch=result[3],
                success_rate=result[4],
                times_applied=result[5],
                created_at=datetime.fromisoformat(result[6]),
                last_applied=datetime.fromisoformat(result[7])
            )
            prescriptions.append(prescription)
        
        return prescriptions


class RCAImmuneSystem:
    """
    RCA Immune System - 根因分析免疫系统
    
    Phase 19: Predictive immunity with pattern learning
    Phase 19 Deep Optimization: Error normalization + immune memory + exponential backoff
    
    Key Responsibilities:
    - Error fingerprint generation
    - Pattern matching and retrieval
    - Healing prescription management
    - Immune fatigue protection
    """
    
    def __init__(self, db_path: str, max_consecutive_failures: int = 3):
        """
        Initialize RCA immune system
        
        Args:
            db_path: Path to immune memory database
            max_consecutive_failures: Max failures before freeze
        """
        self.normalizer = ErrorNormalizer()
        self.memory = ImmuneMemoryDatabase(db_path)
        self.max_consecutive_failures = max_consecutive_failures
        
        # Immune fatigue tracking
        self.failure_history: Dict[str, List[datetime]] = {}  # fingerprint_id -> failure times
        self.freeze_until: Dict[str, datetime] = {}  # fingerprint_id -> freeze end time
    
    async def analyze_error(
        self,
        error: Exception,
        tb_str: str,
        context: Optional[Dict] = None
    ) -> ErrorFingerprint:
        """
        Analyze error and generate fingerprint / 分析错误并生成指纹
        
        Phase 19 Deep Optimization: Root cause normalization
        
        Args:
            error: Exception object
            tb_str: Traceback string
            context: Optional context information
            
        Returns:
            Error fingerprint
        """
        print(f"\n🔬 RCA Immune System - Analyzing Error")
        print(f"   Error Type: {type(error).__name__}")
        print(f"   Error Message: {str(error)[:100]}")
        
        # Normalize error message
        normalized_message = self.normalizer.normalize_error_message(str(error))
        
        # Extract and hash traceback chain
        tb_chain = self.normalizer.extract_traceback_chain(tb_str)
        tb_hash = self.normalizer.hash_traceback_chain(tb_chain)
        
        # Generate fingerprint ID
        fingerprint_data = f"{type(error).__name__}:{normalized_message}:{tb_hash}"
        fingerprint_id = hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
        
        # Check if we've seen this before
        existing = self.memory.find_matching_fingerprint(fingerprint_id)
        
        if existing:
            # Update occurrence count
            existing.occurrence_count += 1
            existing.last_seen = datetime.now()
            fingerprint = existing
            print(f"   🔍 Known error pattern (seen {existing.occurrence_count} times)")
        else:
            # New error pattern
            fingerprint = ErrorFingerprint(
                fingerprint_id=fingerprint_id,
                error_type=type(error).__name__,
                error_message_pattern=normalized_message,
                traceback_chain_hash=tb_hash,
                file_path=context.get('file_path') if context else None,
                function_name=context.get('function_name') if context else None
            )
            print(f"   ✨ New error pattern discovered")
        
        # Store fingerprint
        self.memory.store_fingerprint(fingerprint)
        
        print(f"   Fingerprint ID: {fingerprint_id}")
        print(f"   Traceback Chain: {' -> '.join(tb_chain[:3])}...")
        
        return fingerprint
    
    async def retrieve_healing_prescription(
        self,
        fingerprint: ErrorFingerprint
    ) -> Optional[HealingPrescription]:
        """
        Retrieve healing prescription from immune memory / 从免疫记忆检索治愈处方
        
        Phase 19 Deep Optimization: RAG-style offline self-healing
        
        Args:
            fingerprint: Error fingerprint
            
        Returns:
            Best healing prescription or None
        """
        print(f"\n💊 Retrieving healing prescription...")
        
        # Check if in freeze state
        if fingerprint.fingerprint_id in self.freeze_until:
            freeze_end = self.freeze_until[fingerprint.fingerprint_id]
            if datetime.now() < freeze_end:
                remaining = (freeze_end - datetime.now()).total_seconds()
                print(f"   ❄️ Error in FREEZE state ({remaining:.0f}s remaining)")
                print(f"   User intervention required")
                return None
        
        # Find prescriptions
        prescriptions = self.memory.find_prescriptions_for_fingerprint(fingerprint.fingerprint_id)
        
        if not prescriptions:
            print(f"   ❌ No historical prescription found")
            return None
        
        # Return best prescription (highest success rate)
        best = prescriptions[0]
        print(f"   ✅ Found prescription (success rate: {best.success_rate:.1%})")
        print(f"      Action: {best.healing_action}")
        print(f"      Applied: {best.times_applied} times")
        
        return best
    
    async def record_healing_attempt(
        self,
        fingerprint: ErrorFingerprint,
        healing_action: str,
        code_patch: Optional[str],
        success: bool
    ):
        """
        Record healing attempt result / 记录治愈尝试结果
        
        Phase 19 Deep Optimization: Immune fatigue & exponential backoff
        
        Args:
            fingerprint: Error fingerprint
            healing_action: Type of healing applied
            code_patch: Code changes made
            success: Whether healing succeeded
        """
        print(f"\n📝 Recording healing attempt...")
        
        if success:
            print(f"   ✅ Healing successful")
            
            # Clear failure history
            if fingerprint.fingerprint_id in self.failure_history:
                del self.failure_history[fingerprint.fingerprint_id]
            
            # Store or update prescription
            prescription_id = hashlib.md5(
                f"{fingerprint.fingerprint_id}:{healing_action}".encode()
            ).hexdigest()[:16]
            
            # Check if prescription exists
            prescriptions = self.memory.find_prescriptions_for_fingerprint(fingerprint.fingerprint_id)
            existing = next((p for p in prescriptions if p.prescription_id == prescription_id), None)
            
            if existing:
                # Update success rate
                existing.times_applied += 1
                existing.last_applied = datetime.now()
                prescription = existing
            else:
                # Create new prescription
                prescription = HealingPrescription(
                    prescription_id=prescription_id,
                    fingerprint_id=fingerprint.fingerprint_id,
                    healing_action=healing_action,
                    code_patch=code_patch
                )
            
            self.memory.store_prescription(prescription)
            
        else:
            print(f"   ❌ Healing failed")
            
            # Track failure
            if fingerprint.fingerprint_id not in self.failure_history:
                self.failure_history[fingerprint.fingerprint_id] = []
            
            self.failure_history[fingerprint.fingerprint_id].append(datetime.now())
            
            # Check for immune fatigue
            recent_failures = [
                t for t in self.failure_history[fingerprint.fingerprint_id]
                if (datetime.now() - t).total_seconds() < 3600  # Last hour
            ]
            
            if len(recent_failures) >= self.max_consecutive_failures:
                # Trigger exponential backoff
                backoff_seconds = 2 ** len(recent_failures) * 60  # Exponential backoff
                freeze_until = datetime.now() + timedelta(seconds=backoff_seconds)
                
                self.freeze_until[fingerprint.fingerprint_id] = freeze_until
                
                print(f"   ❄️ IMMUNE FATIGUE - Entering FREEZE state")
                print(f"      Consecutive failures: {len(recent_failures)}")
                print(f"      Freeze duration: {backoff_seconds/60:.1f} minutes")
                print(f"      🚨 USER INTERVENTION REQUIRED 🚨")


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize immune system
        db_path = Path(__file__).parent / "immune_memory.db"
        immune_system = RCAImmuneSystem(str(db_path))
        
        # Simulate error
        try:
            # Trigger an error
            result = 1 / 0
        except Exception as e:
            tb_str = traceback.format_exc()
            
            # Analyze error
            fingerprint = await immune_system.analyze_error(
                e,
                tb_str,
                context={'file_path': 'test.py', 'function_name': 'main'}
            )
            
            # Try to retrieve prescription
            prescription = await immune_system.retrieve_healing_prescription(fingerprint)
            
            if prescription:
                print(f"\n✅ Applying historical prescription...")
                # Apply prescription
                success = True  # Mock success
            else:
                print(f"\n🔧 No prescription found, attempting new healing...")
                success = False  # Mock failure
            
            # Record attempt
            await immune_system.record_healing_attempt(
                fingerprint,
                healing_action="add_zero_check",
                code_patch="if denominator != 0:",
                success=success
            )
    
    asyncio.run(main())
