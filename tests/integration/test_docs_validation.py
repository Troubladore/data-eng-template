"""Integration tests for documentation validation and accuracy.

These tests ensure that documentation stays in sync with the actual template
structure and that all documented files/directories have human-accessible
explanations somewhere in the repo.
"""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Set, List
import pytest


class TestDirectoryStructureAccuracy:
    """Test that docs/directory_structure.md reflects actual template structure."""
    
    def test_directory_structure_is_current(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that directory_structure.md matches actual generated project structure."""
        # Generate a project to get the actual structure
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Template generation failed: {result.stderr}"
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Generate actual directory tree and extract all paths
        actual_tree = self._generate_directory_tree(project_dir)
        
        # Read documented directory structure
        docs_structure_file = project_dir / "docs" / "directory_structure.md"
        assert docs_structure_file.exists(), "docs/directory_structure.md must exist"
        
        documented_tree = docs_structure_file.read_text()
        
        # Parse documented structure to extract files/directories
        documented_items = self._parse_documented_structure(documented_tree)
        
        # Get all actual paths in the project (including nested)
        actual_all_paths = self._get_all_project_paths(project_dir)
        
        # Check that documented items exist somewhere in actual structure
        missing_from_actual = set()
        for item in documented_items:
            item_name = item.rstrip('/')  # Remove trailing slash for comparison
            
            # Check if this item exists as a file or directory name anywhere in project
            if not any(path.name == item_name or path.name == item for path in actual_all_paths):
                missing_from_actual.add(item)
        
        # Allow some flexibility for template variables and generated files  
        ignore_patterns = {
            '.git', '.DS_Store', '__pycache__', '*.pyc', '.pytest_cache',
            'outputs/', 'logs/', '.env', 'uv.lock'  # Generated at runtime
        }
        
        # Filter out ignored and template variable items
        missing_from_actual = {
            item for item in missing_from_actual 
            if not any(self._matches_pattern(item, pattern) for pattern in ignore_patterns)
            and '{{' not in item  # Skip template variables
        }
        
        assert not missing_from_actual, f"Documented items not found in actual structure: {missing_from_actual}"
    
    def _generate_directory_tree(self, project_dir: Path) -> str:
        """Generate a directory tree representation."""
        result = subprocess.run(
            ['tree', '-a', '-I', '.git|__pycache__|*.pyc|.pytest_cache'], 
            cwd=project_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            # Fallback: use find if tree is not available
            result = subprocess.run(
                ['find', '.', '-type', 'f', '-o', '-type', 'd'],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
        
        return result.stdout
    
    def _get_all_project_paths(self, project_dir: Path) -> List[Path]:
        """Get all file and directory paths in the project."""
        paths = []
        for item in project_dir.rglob('*'):
            # Skip git and cache directories
            if any(skip in str(item) for skip in ['.git/', '__pycache__/', '.pytest_cache/']):
                continue
            paths.append(item)
        return paths
    
    def _parse_documented_structure(self, documented_tree: str) -> Set[str]:
        """Parse directory structure from documentation."""
        items = set()
        
        # Find the code block with the tree structure
        in_tree_block = False
        
        for line in documented_tree.split('\n'):
            # Start parsing when we enter the code block
            if line.strip() == '```' and not in_tree_block:
                in_tree_block = True
                continue
            elif line.strip() == '```' and in_tree_block:
                in_tree_block = False
                continue
            
            # Skip lines outside the tree structure code block
            if not in_tree_block:
                continue
                
            # Skip empty lines
            if not line.strip():
                continue
                
            # Extract file/directory names from tree structure lines
            # Tree patterns: ├── file.py, │   └── subdir/, etc.
            # Remove tree decoration and extract the actual filename/dirname
            match = re.search(r'[├└│─\s]*([a-zA-Z0-9_\-\.{}]+(?:/)?)(?:\s+#.*)?$', line)
            if match:
                item = match.group(1).strip()
                # Skip the root directory marker and comments
                if item and item not in {'.', '..'}:
                    items.add(item)
        
        return items
    
    def _extract_tree_items(self, tree_output: str) -> Set[str]:
        """Extract file/directory names from tree output."""
        items = set()
        
        for line in tree_output.split('\n'):
            line = line.strip()
            
            # Skip empty lines and directory count lines
            if not line or line.endswith(' directories,') or line.endswith(' files'):
                continue
                
            # For find output (fallback case)
            if line.startswith('./'):
                path = line[2:]  # Remove './'
                if '/' not in path:  # Top-level items only
                    items.add(path)
                continue
                    
            # For tree output - extract filename/dirname from tree structure
            # Tree patterns: ├── file.py, │   └── subdir/, etc.
            match = re.search(r'[├└│─\s]*([a-zA-Z0-9_\-\.{}]+(?:/)?)$', line)
            if match:
                item = match.group(1).strip()
                if item and item not in {'.', '..'}:
                    items.add(item)
        
        return items
    
    def _matches_pattern(self, item: str, pattern: str) -> bool:
        """Check if item matches ignore pattern."""
        if '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(item, pattern)
        return pattern in item


class TestDocumentationCompleteness:
    """Test that all directories and important files have human-accessible documentation."""
    
    def test_all_directories_have_documentation(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that every directory has some form of documentation."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Find all directories
        directories = []
        for item in project_dir.rglob('*'):
            if item.is_dir() and not self._should_skip_dir(item):
                rel_path = item.relative_to(project_dir)
                directories.append(rel_path)
        
        # Check that each directory has documentation
        undocumented_dirs = []
        
        for dir_path in directories:
            full_dir_path = project_dir / dir_path
            
            # Check for various forms of documentation
            has_docs = (
                # Direct README in the directory
                (full_dir_path / "README.md").exists() or
                # CLAUDE.md guidance file
                (full_dir_path / "CLAUDE.md").exists() or
                # Documented in main docs/
                self._is_documented_in_main_docs(project_dir, str(dir_path)) or
                # Parent directory has README that covers it
                self._parent_has_covering_readme(full_dir_path)
            )
            
            if not has_docs:
                undocumented_dirs.append(str(dir_path))
        
        assert not undocumented_dirs, f"Directories without documentation: {undocumented_dirs}"
    
    def test_important_files_have_documentation(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that important configuration files have documentation."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Important files that should be documented
        important_files = [
            "pyproject.toml",
            "Makefile", 
            ".devcontainer/devcontainer.json",
            ".devcontainer/compose.yaml",
            "conf/config.yaml",
            "dbt/dbt_project.yml"
        ]
        
        undocumented_files = []
        
        for file_path in important_files:
            full_file_path = project_dir / file_path
            
            if not full_file_path.exists():
                continue  # Skip if file doesn't exist
            
            # Check if file is documented somewhere
            is_documented = (
                # Documented in main docs
                self._is_documented_in_main_docs(project_dir, file_path) or
                # Has inline comments explaining purpose
                self._has_inline_documentation(full_file_path) or
                # Covered by directory-level documentation
                self._parent_has_covering_readme(full_file_path.parent)
            )
            
            if not is_documented:
                undocumented_files.append(file_path)
        
        assert not undocumented_files, f"Important files without documentation: {undocumented_files}"
    
    def _should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped in documentation checks."""
        skip_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'outputs', 'logs',
            '.vscode', '.idea', 'node_modules', 'target'
        }
        
        return any(pattern in str(dir_path) for pattern in skip_patterns)
    
    def _is_documented_in_main_docs(self, project_dir: Path, item_path: str) -> bool:
        """Check if item is documented in main docs/ directory."""
        docs_dir = project_dir / "docs"
        
        if not docs_dir.exists():
            return False
        
        # Search for mentions in all markdown files in docs/
        for doc_file in docs_dir.rglob("*.md"):
            try:
                content = doc_file.read_text()
                if item_path in content or Path(item_path).name in content:
                    return True
            except UnicodeDecodeError:
                continue  # Skip binary files
        
        return False
    
    def _parent_has_covering_readme(self, directory: Path) -> bool:
        """Check if parent directory has README that covers this directory."""
        readme_path = directory / "README.md"
        if not readme_path.exists():
            return False
            
        try:
            content = readme_path.read_text()
            # Simple heuristic: README has substantial content (> 100 chars)
            return len(content.strip()) > 100
        except UnicodeDecodeError:
            return False
    
    def _has_inline_documentation(self, file_path: Path) -> bool:
        """Check if file has meaningful inline comments or docstrings."""
        if not file_path.exists():
            return False
            
        try:
            content = file_path.read_text()
            
            # Count comment lines (rough heuristic)
            comment_patterns = ['#', '//', '/*', '"""', "'''", '<!--']
            comment_lines = 0
            
            for line in content.split('\n'):
                line = line.strip()
                if any(line.startswith(pattern) for pattern in comment_patterns):
                    comment_lines += 1
            
            # Consider documented if >10% of lines are comments
            total_lines = len(content.split('\n'))
            return total_lines > 0 and (comment_lines / total_lines) > 0.1
            
        except UnicodeDecodeError:
            return False


class TestDocumentationQuality:
    """Test documentation quality and consistency."""
    
    def test_markdown_files_have_proper_structure(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that Markdown files follow consistent structure."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        
        # Find all Markdown files
        markdown_files = list(project_dir.rglob("*.md"))
        
        assert len(markdown_files) > 0, "Should have Markdown documentation files"
        
        issues = []
        
        for md_file in markdown_files:
            try:
                content = md_file.read_text()
                
                # Check for basic structure
                if not content.strip():
                    issues.append(f"{md_file.name}: Empty file")
                    continue
                
                # Should have at least one heading
                if not re.search(r'^#', content, re.MULTILINE):
                    issues.append(f"{md_file.name}: No headings found")
                
                # Should not have broken relative links (basic check)
                relative_links = re.findall(r'\[.*?\]\(([^)]+)\)', content)
                for link in relative_links:
                    if link.startswith('./') or link.startswith('../'):
                        # Check if linked file exists
                        linked_file = md_file.parent / link
                        if not linked_file.exists():
                            issues.append(f"{md_file.name}: Broken link to {link}")
                            
            except UnicodeDecodeError:
                issues.append(f"{md_file.name}: Not a valid text file")
        
        assert not issues, f"Documentation quality issues: {issues}"
    
    def test_docs_directory_has_index(self, template_dir: Path, temp_dir: Path, default_cookiecutter_config: Dict[str, Any]):
        """Test that docs directory has proper index/navigation."""
        # Generate project
        cmd = [
            'cookiecutter', str(template_dir),
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in default_cookiecutter_config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        
        project_dir = temp_dir / default_cookiecutter_config["repo_slug"]
        docs_dir = project_dir / "docs"
        
        if not docs_dir.exists():
            # If no docs dir, main README should be comprehensive
            main_readme = project_dir / "README.md"
            assert main_readme.exists(), "Must have either docs/ directory or comprehensive README.md"
            return
        
        # Should have index.md or README.md
        has_index = (docs_dir / "index.md").exists() or (docs_dir / "README.md").exists()
        assert has_index, "docs/ directory should have index.md or README.md"