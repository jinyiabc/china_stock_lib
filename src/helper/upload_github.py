import argparse
from importlib import resources
import os
from github import Github
import config

with resources.path('helper', 'mysql.cfg') as p:
    resource_path = str(p)
cfg = config.Config(resource_path)

def upload_github(file_path):

    g = Github(cfg['github_token'])
    repo = g.get_repo("jinyiabc/china_stock_data")
    all_files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    with open(file_path, 'rb') as file:
        content = file.read()
        # file.seek(0)
        # content = pickle.load(file)

    # Upload to github
    git_prefix = 'module-03/'
    head, tail = os.path.split(file_path)
    git_file = git_prefix + tail
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
        print(git_file + ' UPDATED')
    else:
        repo.create_file(git_file, "committing files", content, branch="main")
        print(git_file + ' CREATED')


def upload_github_script(args=None):
    res = parse_args(args)
    file_path = res.file_path
    g = Github(cfg['github_token'])
    repo = g.get_repo("jinyiabc/china_stock_data")
    all_files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    with open(file_path, 'rb') as file:
        content = file.read()
        # file.seek(0)
        # content = pickle.load(file)

    # Upload to github
    git_prefix = 'module-03/'
    head, tail = os.path.split(file_path)
    git_file = git_prefix + tail
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
        print(git_file + ' UPDATED')
    else:
        repo.create_file(git_file, "committing files", content, branch="main")
        print(git_file + ' CREATED')

def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Upload CSV file to github.')

    parser.add_argument('-f',
                        '--file_path',
                        # action='store_true',
                        dest='file_path',
                        required=True,
                        help='file path')


    return parser.parse_args(args)

# python upload_github.py --file_path="./300144-2.csv"
# python upload_github.py --file_path=./300144-2.csv
# python upload_github.py --file_path=D:\work\china_stock_lib\helper\src\helper\300144-2.csv