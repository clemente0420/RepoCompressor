import argparse
import os
import subprocess
import chardet
import shutil


def is_text_file(file_path):
    # Check if the file is a text file by checking its MIME type
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith("text")

def download_repo(repo_url):
    # Remove the destination directory if it exists
    repo_name = os.path.basename(repo_url).replace(".git", "")
    if os.path.exists(repo_name):
        shutil.rmtree(repo_name)

    # Use the `git clone` command to download the repository to the local machine
    subprocess.run(["git", "clone", repo_url, repo_name])

    # Return the path to the local repository
    return os.path.abspath(repo_name)

def merge_files_in_repo(repo_path):
    # Get the list of text files in the repository (exclude files in .git directory)
    contents = []
    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            file_path = os.path.join(root, file)
            if not is_text_file(file_path):
                continue
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            contents.append((file_path, content))

    # Merge all files into a single string
    merged_contents = ""
    for file_path, content in contents:
        merged_contents += f"\n\n// File: {file_path}\n\n{content}"

    # Save the merged contents to a file
    base_path = os.path.basename(repo_path)
    merge_file_path = f"{base_path}.merge"
    with open(merge_file_path, "w") as f:
        f.write(merged_contents)

    # Validate the merged file
    validate_merged_file(merge_file_path)

def validate_merged_file(merge_file_path):
    # Generate a check file containing the contents of all text files
    check_file_path = f"{merge_file_path}.check"
    os.system(f"cat $(find . -type f -not -path './.git/*' -and -not -path '*.merge*') > {check_file_path}")

    # Get the line counts of the check file and the merged file
    with open(check_file_path, "r", encoding="utf-8", errors="ignore") as f:
        check_lines = len(f.readlines())
    with open(merge_file_path, "r", encoding="utf-8", errors="ignore") as f:
        merge_lines = len(f.readlines())

    # Compare the line counts of the check file and the merged file
    if merge_lines < check_lines:
        raise Exception(f"Merged file has {merge_lines} lines, expected at least {check_lines} lines")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_url", help="GitHub repository URL")
    args = parser.parse_args()

    # Download the repository to the local machine
    repo_path = download_repo(args.repo_url)

    # Merge all text files in the repository
    merge_files_in_repo(repo_path)
