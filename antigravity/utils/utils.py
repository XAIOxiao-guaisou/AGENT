import os
import subprocess
import fnmatch

def get_git_diff(repo_path, file_path=None):
    """
    Get the git diff for the repository or a specific file.
    """
    try:
        cmd = ["git", "diff", "HEAD"]
        if file_path:
            cmd.append(file_path)
            
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting git diff: {e}"
    except Exception as e:
        return f"Unexpected error getting git diff: {e}"

def get_tree_structure(root_dir, exclude_patterns=None):
    """
    recursively generate a directory tree structure, excluding specified patterns.
    """
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', 'node_modules', '*.pyc', 'venv', '.env', '.idea', '.vscode']

    tree_str = ""
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not any(fnmatch.fnmatch(f, p) for p in exclude_patterns):
                tree_str += f"{subindent}{f}\n"
    return tree_str

def get_related_test(file_path):
    """
    Map a source file to its corresponding test file.
    Heuristic: src/module/file.py -> tests/module/test_file.py
               src/file.py -> tests/test_file.py
    """
    # Normalize path separators
    file_path = file_path.replace('\\', '/')
    
    parts = file_path.split('/')
    if parts[0] == 'src':
        parts[0] = 'tests'
    elif parts[0] != 'tests':
        parts.insert(0, 'tests')
        
    filename = parts[-1]
    if not filename.startswith('test_'):
        parts[-1] = f"test_{filename}"
        
    return '/'.join(parts)
    
