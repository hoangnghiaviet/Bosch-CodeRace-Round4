import os
import openpyxl
from io import BytesIO
import pandas as pd
from github import Github
from github.GithubException import UnknownObjectException, GithubException
from dotenv import load_dotenv

repository_name = None
repository = None
branch = None
branch_name = None

def Config():
    global repository_name, repository , branch_name , branch
    load_dotenv(dotenv_path="/opt/airflow/dags/src/secret.env")

    # Authenticate with the GitHub API using a personal access token
    access_token = os.getenv("TOKEN")
    g = Github(access_token)

    # Get the repository
    repository_name = os.getenv("REPOSITORY_NAME")

    # for example "hoangteo0103/CODERACE"
    repository = g.get_repo(repository_name)

    # Get the branch
    branch_name = os.getenv("BRANCH_NAME")
    try:
        branch = repository.get_branch(branch_name)
        print("Branch already exists:", branch_name)
    except GithubException:
        # Check if any branch exists
        branches = repository.get_branches()
        if branches.totalCount > 0:
            # Use the first existing branch as a base for the new branch
            base_branch = branches[0]
        else:
            # Create a dummy file to initialize the repository if it's empty
            repository.create_file(
                "README.md", "Initial commit", "This is the initial commit.", branch=branch_name
            )
            # Use the created branch as a base for the new branch
            base_branch = repository.get_branch(branch_name)

        # Create a new branch based on the chosen base branch
        ref = repository.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
        branch = repository.get_branch(branch_name)

def push_file_xlsx(file_path , local_file_path):
    # Overwrite the file if it exists
    try:
        contents = repository.get_contents(file_path, ref=branch.commit.sha)
        # If the file already existed, we delete it
        repository.delete_file(contents.path, 'File overwritten', contents.sha, branch=branch_name)
    except UnknownObjectException:
        pass

    # Read the content from a local XLSX file
    workbook = openpyxl.load_workbook(local_file_path)
    worksheet = workbook.active

    # Convert the worksheet content to bytes
    file_content = BytesIO()
    workbook.save(file_content)
    file_content.seek(0)
    new_file_content = file_content.read()
    file_content.close()
    workbook.close()

    repository.create_file(file_path, 'File added', new_file_content, branch=branch_name)

def push_file(file_path , local_file_path):
    # Overwrite the file if it exists
    try:
        contents = repository.get_contents(file_path, ref=branch.commit.sha)
        # If the file already existed, we delete it
        repository.delete_file(contents.path, 'File overwritten', contents.sha, branch=branch_name)
    except UnknownObjectException:
        pass

    # Read the content from a local file
    with open(local_file_path, 'r') as file:
        new_file_content = file.read()
    # Create the new file
    repository.create_file(file_path, 'File added', new_file_content, branch=branch_name)
def update_index_rst(new_rst_file, rst_caption):
    index_file_path = "docs/index.rst"

    # Get the content of the index.rst file from the repository
    contents = repository.get_contents(index_file_path, ref=branch.commit.sha)
    lines = contents.decoded_content.decode().splitlines()

    # Modify the rst_caption to include the :caption: prefix
    rst_caption = ":caption: " + rst_caption

    # Store the lines of content before the toctree section
    new_content = []

    # Dictionary to store the toctree caption and associated requirements
    toctree_dict = {}

    # Extract the lines before the toctree section
    for i, line in enumerate(lines):
        if line.startswith(".. toctree"):
            break
        new_content.append(line + '\n')

    # Extract the toctree captions and requirements
    for i, line in enumerate(lines):
        if line.startswith(".. toctree"):
            requirement_file_index = i + 4
            while (
                    requirement_file_index < len(lines)
                    and lines[requirement_file_index].startswith('   ')
            ):
                caption = lines[i + 2].strip()
                requirement = lines[requirement_file_index].strip()
                if caption not in toctree_dict:
                    toctree_dict[caption] = []
                toctree_dict[caption].append(requirement)
                requirement_file_index += 1

    # Update the dictionary with the new requirement
    for caption, requirements in toctree_dict.items():
        if new_rst_file in requirements:
            requirements.remove(new_rst_file)

    # Add the new requirement to the dictionary
    if rst_caption in toctree_dict:
        toctree_dict[rst_caption].append(new_rst_file)
    else:
        toctree_dict[rst_caption] = [new_rst_file]

    # Rebuild the updated content
    updated_content = "".join(new_content)

    # Iterate over the toctree captions and requirements
    for index, (caption, requirements) in enumerate(toctree_dict.items()):
        if len(requirements) == 0:
            continue

        # Add the toctree directive and caption to the updated content
        if index != 0:
            updated_content += "\n"
        updated_content += ".. toctree::\n"
        updated_content += "   :maxdepth: 1\n"
        updated_content += f"   {caption}\n\n"

        # Add the requirements to the updated content
        for requirement in requirements:
            updated_content += f"   {requirement}\n"

    # Add the Indices and tables section
    updated_content += """
Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
    """

    # Delete the existing index.rst file in the repository
    repository.delete_file(contents.path, 'File overwritten', contents.sha, branch=branch_name)

    # Create the updated index.rst file in the repository
    repository.create_file(index_file_path, 'File added', updated_content, branch=branch_name)

Config()

#Update config.xlsx and conf.py for building html


def updateIndexRST():
    # Create conf.py in repo
    configSphinxLocalPath = '/opt/airflow/dags/src/conf.py'
    configSphinxPath = 'docs/conf.py'
    push_file(configSphinxPath, configSphinxLocalPath)
    configUserLocalPath = '/opt/airflow/dags/input/config.xlsx'
    configUserPath = 'docs/config.xlsx'
    # Create config.xlsx in repo
    push_file_xlsx(configUserPath , configUserLocalPath)

    # Read from the user config file 'config.xlsx' to choose the location and caption of the new uploaded RST
    config_info = pd.read_excel(configUserLocalPath, "UploadFileRST")
    requirement_file_path = ''
    for index, row in config_info.iterrows():
        requirement_file_path = row["File Destination"]
        requirement_file_caption = row["Requirement Caption"]

    update_index_rst(requirement_file_path.replace('docs' ,'.'), requirement_file_caption)





