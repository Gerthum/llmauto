"""
GitHub PR Creation Functions

Required installation:
pip install PyGithub python-dotenv

Setup:
1. Copy .env.example to .env
2. Fill in your GitHub token and repo details
3. Load environment variables in your main app with: load_dotenv()

Usage examples:

1. Basic usage with all parameters:
   pr_url = create_github_pr_with_code(
       code="print('Hello, World!')",
       filename="hello.py",
       repo_name="username/myrepo",
       pr_title="Add hello world script",
       pr_description="This PR adds a simple hello world script",
       branch_name="feature/hello-world",
       commit_message="Add hello world script",
       github_token="your_github_token"
   )

2. Quick usage (requires .env to be loaded in main app):
   pr_url = create_quick_pr(
       code="def add(a, b): return a + b",
       filename="utils.py",
       description="Add utility function"
   )
"""

import os
import base64
from github import Github  # pip install PyGithub
from typing import Optional


def configure_target_repo(repo_name: str, default_branch: str = "main", github_token: Optional[str] = None):
    """
    Configure the target repository for PR creation.
    
    Args:
        repo_name (str): Repository name in format 'owner/repo'
        default_branch (str): Default branch to target for PRs
        github_token (str, optional): GitHub token to use
    """
    os.environ['GITHUB_REPO'] = repo_name
    os.environ['DEFAULT_BRANCH'] = default_branch
    if github_token:
        os.environ['GITHUB_TOKEN'] = github_token
    print(f"✓ Configured target repository: {repo_name} (branch: {default_branch})")


def create_github_pr_with_code(
    code: str,
    filename: str,
    repo_name: str,
    pr_title: str,
    pr_description: str,
    branch_name: str,
    commit_message: str,
    github_token: Optional[str] = None,
    target_branch: Optional[str] = None
) -> str:
    """
    Creates a GitHub Pull Request with the provided code.
    
    Args:
        code (str): The code content to be added to the file
        filename (str): Name of the file to create/update (e.g., 'src/new_feature.py')
        repo_name (str): Repository name in format 'owner/repo' (e.g., 'username/myproject')
        pr_title (str): Title for the pull request
        pr_description (str): Description for the pull request
        branch_name (str): Name of the new branch to create for the PR
        commit_message (str): Commit message for the code changes
        github_token (str, optional): GitHub personal access token. If None, will use GITHUB_TOKEN env var
        target_branch (str): Target branch for the PR (default: 'main')
    
    Returns:
        str: URL of the created pull request
        
    Raises:
        Exception: If GitHub operations fail
    """
    try:
        # Get GitHub token from parameter or environment variable
        token = github_token or os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GitHub token is required. Provide it as parameter or set GITHUB_TOKEN environment variable")
        
        # Get target branch from parameter or environment variable
        if target_branch is None:
            target_branch = os.getenv('DEFAULT_BRANCH', 'main')
        
        # Initialize GitHub client
        g = Github(token)
        
        # Get the repository
        try:
            repo = g.get_repo(repo_name)
            print(f"✓ Connected to repository: {repo_name}")
        except Exception as e:
            raise Exception(f"Repository '{repo_name}' not found or access denied. Error: {str(e)}")
        
        # Get the default branch reference
        try:
            source_branch = repo.get_branch(target_branch)
            print(f"✓ Found target branch: {target_branch}")
        except Exception as e:
            # List available branches for debugging
            branches = [branch.name for branch in repo.get_branches()]
            raise Exception(f"Branch '{target_branch}' not found. Available branches: {', '.join(branches[:5])}. Error: {str(e)}")
        
        # Create a new branch
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=source_branch.commit.sha
        )
        
        # Check if file exists
        try:
            existing_file = repo.get_contents(filename, ref=branch_name)
            # Update existing file
            repo.update_file(
                path=filename,
                message=commit_message,
                content=code,
                sha=existing_file.sha,
                branch=branch_name
            )
        except:
            # Create new file
            repo.create_file(
                path=filename,
                message=commit_message,
                content=code,
                branch=branch_name
            )
        
        # Create pull request
        pr = repo.create_pull(
            title=pr_title,
            body=pr_description,
            head=branch_name,
            base=target_branch
        )
        
        return pr.html_url
        
    except Exception as e:
        raise Exception(f"Failed to create GitHub PR: {str(e)}")


def create_quick_pr(code: str, filename: str, description: str = "Auto-generated code") -> str:
    """
    Simplified function to create a PR with minimal parameters.
    Uses environment variables for configuration.
    
    Args:
        code (str): The code content
        filename (str): Name of the file to create
        description (str): Brief description of the changes
    
    Returns:
        str: URL of the created pull request
    """
    import datetime
    
    # Generate automatic names
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"feature/auto_generated_{timestamp}"
    pr_title = f"Add {filename}"
    commit_message = f"Add auto-generated {filename}"
    
    # Get repo name from environment or current directory
    repo_name = os.getenv('GITHUB_REPO')
    if not repo_name:
        # Try to extract from git remote (if available)
        try:
            import subprocess
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from git URL
                if 'github.com' in url:
                    if url.startswith('git@'):
                        repo_name = url.split(':')[1].replace('.git', '')
                    else:
                        repo_name = '/'.join(url.split('/')[-2:]).replace('.git', '')
        except:
            pass
    
    if not repo_name:
        raise ValueError("Repository name not found. Set GITHUB_REPO environment variable or run from a git repository")
    
    return create_github_pr_with_code(
        code=code,
        filename=filename,
        repo_name=repo_name,
        pr_title=pr_title,
        pr_description=description,
        branch_name=branch_name,
        commit_message=commit_message
    )