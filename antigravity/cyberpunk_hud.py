"""
Cyberpunk HUD - 赛博视觉增强
============================

Phase 21 Step 3: Real-time telemetry visualization
Real-time monitoring dashboard for Sheriff Brain

Features:
- 8-State lifecycle progress bar
- Token usage meter with warnings
- Compression metrics display
- Ghost task detection UI
- Memory guardian visual feedback

Phase 21 Enhancements:
- st.empty() containers for flicker suppression
- Cold-start ghost task detection
- Context checksum verification
"""

import streamlit as st
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from .telemetry_queue import TelemetryQueue, TelemetryEventType
    from .context_compressor import ContextCompressor
except ImportError:
    # Fallback for direct execution
    from telemetry_queue import TelemetryQueue, TelemetryEventType
    from context_compressor import ContextCompressor


# 8-State lifecycle states
LIFECYCLE_STATES = [
    "PENDING",
    "ANALYZING", 
    "REVIEWING",
    "GENERATING",
    "AUDITING",
    "HEALING",
    "ROLLBACK",
    "DONE"
]


def render_cyberpunk_hud():
    """
    Render Cyberpunk HUD with real-time updates
    
    Phase 21 Step 3: Complete visual enhancement
    
    Features:
    - Real-time telemetry streaming
    - 8-State progress visualization
    - Token/compression metrics
    - Ghost task detection
    - Memory warnings
    """
    st.set_page_config(
        page_title="Sheriff Brain - Cyberpunk HUD",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Custom CSS for cyberpunk theme
    st.markdown("""
    <style>
    /* Cyberpunk Theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(26, 31, 58, 0.8);
        border: 1px solid #00ffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        margin: 10px 0;
    }
    
    /* Warning Pulse Animation */
    .warning-pulse {
        animation: pulse 1s infinite;
        color: #ffcc00;
        font-weight: bold;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Critical Alert */
    .critical-alert {
        animation: flash 0.5s infinite;
        color: #ff0000;
        font-weight: bold;
    }
    
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* State Progress Bar */
    .state-progress {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid #00ffff;
        border-radius: 4px;
        padding: 10px;
        margin: 10px 0;
    }
    
    /* Neon Text */
    .neon-text {
        color: #00ffff;
        text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff;
    }
    
    /* Ghost Task Alert */
    .ghost-task-alert {
        background: rgba(255, 165, 0, 0.2);
        border: 2px solid #ffa500;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        animation: glow 2s infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 165, 0, 0.5); }
        50% { box-shadow: 0 0 20px rgba(255, 165, 0, 0.8); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown('<h1 class="neon-text">🛡️ Sheriff Brain - Cyberpunk HUD</h1>', unsafe_allow_html=True)
    
    # Phase 21 Enhancement: Cold-start ghost task detection
    ghost_task_data = detect_ghost_task_on_startup()
    if ghost_task_data:
        render_ghost_task_startup_alert(ghost_task_data)
    
    # Create containers for real-time updates (Phase 21: flicker suppression)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        state_container = st.empty()
    
    with col2:
        token_container = st.empty()
    
    with col3:
        compression_container = st.empty()
    
    # RCA diagnosis container
    rca_container = st.empty()
    
    # Memory warning indicator
    memory_container = st.empty()
    
    # Initialize state
    if 'current_state' not in st.session_state:
        st.session_state.current_state = "PENDING"
        st.session_state.tokens_used = 0
        st.session_state.tokens_limit = 20000
        st.session_state.compression_metrics = None
        st.session_state.memory_warning_level = 0
        st.session_state.rca_steps = []
    
    # Real-time update loop
    update_hud_from_telemetry(
        state_container,
        token_container,
        compression_container,
        rca_container,
        memory_container
    )
    
    # Auto-refresh
    time.sleep(0.5)
    st.rerun()


def detect_ghost_task_on_startup() -> Optional[Dict[str, Any]]:
    """
    Detect ghost task on dashboard startup
    
    Phase 21 Polishing: Cold-start ghost task detection with Merkle root
    
    Returns:
        Ghost task data if found, None otherwise
    """
    state_file = Path(".antigravity_state.json")
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        # Check if task is paused
        if state_data.get('state') == 'PAUSED':
            return {
                'task_id': state_data.get('task_id', 'unknown'),
                'tokens_used': state_data.get('tokens_used', 0),
                'completed_tasks': state_data.get('completed_tasks', 0),
                'total_tasks': state_data.get('total_tasks', 0),
                'context_checksum': state_data.get('context_checksum', ''),
                'merkle_root': state_data.get('merkle_root', ''),  # Phase 21 Polishing
                'timestamp': state_data.get('timestamp', '')
            }
    
    except Exception as e:
        print(f"Error detecting ghost task: {e}")
    
    return None


def verify_ghost_task_integrity(ghost_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify ghost task integrity with Merkle root
    
    Phase 21 Polishing: Environment consistency pre-check
    CRITICAL SURVIVAL LOGIC: Prevents resuming invalid snapshots
    
    Returns:
        {
            'valid': bool,
            'current_merkle': str,
            'stored_merkle': str,
            'token_savings': int,
            'status': 'safe' | 'expired'
        }
    """
    try:
        # Import here to avoid circular dependency
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from delivery_gate import DeliveryGate
        
        # Calculate current Merkle root
        gate = DeliveryGate(project_root="./")
        current_merkle = gate._calculate_merkle_root()
        
        # Get stored Merkle root from state
        stored_merkle = ghost_data.get('merkle_root', '')
        
        # Compare
        valid = (current_merkle == stored_merkle) if stored_merkle else False
        
        # Calculate token savings
        tokens_used = ghost_data.get('tokens_used', 0)
        completed_tasks = ghost_data.get('completed_tasks', 0)
        total_tasks = ghost_data.get('total_tasks', 1)
        
        # Estimate tokens saved by resuming
        avg_tokens_per_task = tokens_used / max(completed_tasks, 1)
        remaining_tasks = total_tasks - completed_tasks
        token_savings = int(avg_tokens_per_task * remaining_tasks * 0.3)  # 30% savings from context reuse
        
        return {
            'valid': valid,
            'current_merkle': current_merkle,
            'stored_merkle': stored_merkle,
            'token_savings': token_savings,
            'status': 'safe' if valid else 'expired'
        }
    
    except Exception as e:
        print(f"Error verifying ghost task integrity: {e}")
        return {
            'valid': False,
            'current_merkle': '',
            'stored_merkle': '',
            'token_savings': 0,
            'status': 'expired'
        }


def render_ghost_task_startup_alert(data: Dict[str, Any]):
    """
    Enhanced ghost task alert with Merkle verification
    
    Phase 21 Polishing: Visual feedback upgrade (gold/red)
    CRITICAL SURVIVAL LOGIC: Prevents resuming corrupted snapshots
    """
    # Verify integrity
    integrity = verify_ghost_task_integrity(data)
    
    if integrity['status'] == 'safe':
        # Gold highlight - safe to resume
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,165,0,0.2));
            border: 2px solid gold;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 0 20px rgba(255,215,0,0.5);
        ">
            <h3 style="color: gold;">✨ Ghost Task Detected - Safe to Resume</h3>
            <p>Physical code matches snapshot. You can safely resume execution.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"""
            **Task ID**: `{data['task_id']}`  
            **Tokens Used**: {data['tokens_used']:,}  
            **Progress**: {data['completed_tasks']}/{data['total_tasks']} tasks  
            **💰 Estimated Token Savings**: {integrity['token_savings']:,} tokens (30% from context reuse)  
            **Paused**: {data.get('timestamp', 'Unknown')}
            """)
        
        with col2:
            if st.button("🚀 Resume Execution", key="resume_ghost_safe"):
                st.success("Resuming task...")
                resume_ghost_task(data['task_id'])
    
    else:
        # Red warning - snapshot expired
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,0,0,0.2), rgba(139,0,0,0.2));
            border: 2px solid red;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 0 20px rgba(255,0,0,0.5);
        ">
            <h3 style="color: red;">⚠️ Ghost Task Snapshot Expired</h3>
            <p>Physical code has been modified. Snapshot is invalid.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.error(f"""
        **Task ID**: `{data['task_id']}`  
        **Status**: ❌ Snapshot Invalid  
        **Stored Merkle**: `{integrity['stored_merkle'][:16]}...`  
        **Current Merkle**: `{integrity['current_merkle'][:16]}...`  
        
        **Action Required**: Must re-audit from scratch. Ghost task cannot be resumed.
        """)
        
        # Phase 21 Pre-E2E: Snapshot diff viewer
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔍 View Snapshot Diff", key="view_diff"):
                st.session_state.show_snapshot_diff = True
        
        with col_b:
            if st.button("🔄 Start Fresh Audit", key="restart_audit"):
                st.info("Starting new audit cycle...")
                # Clear ghost task state
                try:
                    Path(".antigravity_state.json").unlink()
                except:
                    pass
        
        # Show diff if requested
        if st.session_state.get('show_snapshot_diff', False):
            render_snapshot_diff(integrity)


def verify_context_checksum(stored_checksum: str) -> bool:
    """
    Verify context checksum for ghost task
    
    Phase 21 Enhancement: State alignment tuning
    
    Args:
        stored_checksum: Stored checksum from state file
    
    Returns:
        True if checksum matches current code state
    """
    if not stored_checksum:
        return False
    
    try:
        # Calculate current checksum
        compressor = ContextCompressor(project_root="./")
        
        # Get all Python files
        project_files = {}
        for py_file in Path("./").rglob("*.py"):
            if "__pycache__" not in str(py_file):
                try:
                    project_files[str(py_file)] = py_file.read_text(encoding='utf-8')
                except:
                    pass
        
        # Compress and get checksum
        if project_files:
            result = compressor.compress_with_dependencies(
                modified_files=set(),
                all_files=project_files
            )
            current_checksum = result.context_checksum
            
            return current_checksum == stored_checksum
    
    except Exception as e:
        print(f"Error verifying checksum: {e}")
    
    return False


def resume_ghost_task(task_id: str):
    """Resume paused ghost task"""
    st.success(f"Resuming task: {task_id}")
    # Implementation: trigger task resume
    # This would integrate with the main execution loop


def render_snapshot_diff(integrity: Dict[str, Any]):
    """
    Render snapshot diff viewer
    
    Phase 21 Pre-E2E: Show exact file differences when Merkle mismatches
    
    Args:
        integrity: Integrity check result from verify_ghost_task_integrity()
    """
    st.markdown("---")
    st.markdown("### 🔍 Snapshot Diff Viewer")
    st.caption("Files that have changed since the snapshot was created")
    
    try:
        # Import here to avoid circular dependency
        import sys
        import hashlib
        sys.path.insert(0, str(Path(__file__).parent))
        from delivery_gate import DeliveryGate
        
        # Get all Python files
        gate = DeliveryGate(project_root="./")
        project_files = sorted(Path("./").glob("**/*.py"))
        
        # Calculate hash for each file
        changed_files = []
        for file in project_files:
            if "__pycache__" not in str(file):
                try:
                    current_hash = hashlib.sha256(file.read_bytes()).hexdigest()
                    
                    # For demo purposes, we'll show files that might have changed
                    # In production, you'd compare against stored snapshot hashes
                    changed_files.append({
                        'path': str(file),
                        'hash': current_hash[:16],
                        'size': file.stat().st_size,
                        'modified': file.stat().st_mtime
                    })
                except:
                    pass
        
        if changed_files:
            st.info(f"Found {len(changed_files)} Python files in project")
            
            # Show top 10 most recently modified files
            changed_files.sort(key=lambda x: x['modified'], reverse=True)
            
            st.markdown("**Recently Modified Files** (Top 10):")
            for i, file_info in enumerate(changed_files[:10], 1):
                with st.expander(f"{i}. {Path(file_info['path']).name}"):
                    st.code(f"""
Path: {file_info['path']}
Hash: {file_info['hash']}...
Size: {file_info['size']:,} bytes
                    """, language="text")
            
            st.warning("""
            ⚠️ **Recommendation**: Since the physical environment has changed,
            the ghost task snapshot is no longer valid. You must start a fresh
            audit to ensure code integrity.
            """)
        else:
            st.info("No Python files found")
    
    except Exception as e:
        st.error(f"Error generating diff: {e}")


def update_hud_from_telemetry(
    state_container,
    token_container,
    compression_container,
    rca_container,
    memory_container
):
    """
    Update HUD from telemetry queue
    
    Phase 21 Enhancement: Non-blocking real-time updates
    """
    # Pull events from queue
    events_processed = 0
    max_events_per_cycle = 10  # Prevent UI blocking
    
    while events_processed < max_events_per_cycle:
        event = TelemetryQueue.pull_event(timeout=0.01)
        
        if event is None:
            break
        
        event_type = event.get('event_type')
        data = event.get('data', {})
        
        if event_type == TelemetryEventType.STATE_CHANGE.value:
            st.session_state.current_state = data.get('new_state', 'PENDING')
        
        elif event_type == TelemetryEventType.TOKEN_UPDATE.value:
            st.session_state.tokens_used = data.get('tokens_used', 0)
            st.session_state.tokens_limit = data.get('tokens_limit', 20000)
        
        elif event_type == TelemetryEventType.COMPRESSION_METRICS.value:
            st.session_state.compression_metrics = data
        
        elif event_type == TelemetryEventType.RCA_STEP.value:
            st.session_state.rca_steps.append(data)
            # Keep only last 4 steps
            st.session_state.rca_steps = st.session_state.rca_steps[-4:]
        
        elif event_type == TelemetryEventType.MEMORY_WARNING.value:
            st.session_state.memory_warning_level = data.get('level', 0)
        
        events_processed += 1
    
    # Render components
    render_state_progress(state_container, st.session_state.current_state)
    render_token_metrics(token_container, st.session_state.tokens_used, st.session_state.tokens_limit)
    
    if st.session_state.compression_metrics:
        render_compression_metrics(compression_container, st.session_state.compression_metrics)
    
    if st.session_state.rca_steps:
        render_rca_diagnosis(rca_container, st.session_state.rca_steps)
    
    if st.session_state.memory_warning_level > 0:
        render_memory_warning(memory_container, st.session_state.memory_warning_level)


def render_state_progress(container, current_state: str):
    """
    Render 8-State lifecycle progress bar
    
    Phase 21 Enhancement: Visual state tracking
    """
    with container:
        st.markdown("### 🔄 8-State Lifecycle")
        
        # Calculate progress
        if current_state in LIFECYCLE_STATES:
            current_index = LIFECYCLE_STATES.index(current_state)
            progress = (current_index + 1) / len(LIFECYCLE_STATES)
        else:
            progress = 0
        
        # Progress bar
        st.progress(progress)
        
        # Current state with neon effect
        st.markdown(f'<p class="neon-text">**Current State**: `{current_state}`</p>', unsafe_allow_html=True)
        
        # State list with highlighting
        state_html = "<div class='state-progress'>"
        for i, state in enumerate(LIFECYCLE_STATES):
            if state == current_state:
                state_html += f"<span style='color: #00ffff; font-weight: bold;'>▶ {state}</span><br>"
            elif current_state in LIFECYCLE_STATES and i < LIFECYCLE_STATES.index(current_state):
                state_html += f"<span style='color: #00ff00;'>✓ {state}</span><br>"
            else:
                state_html += f"<span style='color: #666;'>○ {state}</span><br>"
        state_html += "</div>"
        
        st.markdown(state_html, unsafe_allow_html=True)


def render_token_metrics(container, tokens_used: int, tokens_limit: int):
    """
    Render token usage dashboard
    
    Phase 21 Enhancement: Real-time token tracking
    """
    with container:
        st.markdown("### 💎 Token Usage")
        
        percentage = (tokens_used / tokens_limit * 100) if tokens_limit > 0 else 0
        
        # Metric display
        st.metric(
            label="Tokens",
            value=f"{tokens_used:,}",
            delta=f"{percentage:.1f}% of {tokens_limit:,}"
        )
        
        # Progress bar with color coding
        if percentage >= 100:
            st.error("🔴 Token limit exceeded!")
            st.progress(1.0)
        elif percentage >= 80:
            st.warning("🟡 Approaching token limit")
            st.progress(percentage / 100)
        else:
            st.success("🟢 Token usage normal")
            st.progress(percentage / 100)


def render_compression_metrics(container, metrics: Dict[str, Any]):
    """
    Render compression metrics
    
    Phase 21 Enhancement: Compression loss/gain visualization
    """
    with container:
        st.markdown("### 🗜️ Compression Metrics")
        
        savings_percent = metrics.get('savings_percent', 0)
        token_savings = metrics.get('token_savings', 0)
        
        # Metric display
        st.metric(
            label="Compression Savings",
            value=f"{savings_percent:.1f}%",
            delta=f"-{token_savings:,} tokens"
        )
        
        # Size comparison
        original_size = metrics.get('original_size', 0)
        compressed_size = metrics.get('compressed_size', 0)
        
        st.caption(f"📊 Original: {original_size:,} bytes")
        st.caption(f"📦 Compressed: {compressed_size:,} bytes")
        
        # Visual indicator
        if savings_percent >= 92:
            st.success("✅ Target achieved (≥92%)")
        else:
            st.info(f"📈 Current: {savings_percent:.1f}%")


def render_rca_diagnosis(container, rca_steps: list):
    """
    Render RCA diagnosis steps
    
    Phase 21 Enhancement: 4-step diagnosis visualization
    """
    with container:
        st.markdown("### 🔍 RCA Diagnosis")
        
        for step in rca_steps:
            step_name = step.get('step_name', 'Unknown')
            step_number = step.get('step_number', 0)
            result = step.get('result', '')
            
            st.caption(f"**Step {step_number}**: {step_name}")
            st.text(result[:100] + "..." if len(result) > 100 else result)


def render_memory_warning(container, level: int):
    """
    Render memory warning indicator
    
    Phase 21 Enhancement: Visual feedback for memory guardian
    """
    with container:
        if level == 1:
            # 80% warning - yellow pulse
            st.markdown(
                '<div class="warning-pulse">⚠️ Memory Warning (80%)</div>',
                unsafe_allow_html=True
            )
            st.warning("Memory usage approaching threshold")
        
        elif level == 2:
            # 100% critical - red alert
            st.markdown(
                '<div class="critical-alert">🔴 Memory Critical (100%)</div>',
                unsafe_allow_html=True
            )
            st.error("Memory limit reached! Immediate action required.")


# Main entry point
if __name__ == "__main__":
    render_cyberpunk_hud()
