import os
import json
import requests
from urllib.parse import urlparse, urlunparse
from github import Github
import git
import secrets
import string

from polyglot_piranha import execute_piranha, PiranhaArguments

def generate_random_id_string(length=6):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

def get_flag_substitutions(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier):
    output = []
    flag_json = get_flag_data(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier)

    if flag_json is None:
        print("no flags found")
        return output
    features = flag_json["features"]
    for feature in features:
        identifier = feature["identifier"]
        output.append({"stale_flag_name": identifier, "treated": "true"})

    return output

def get_flag_data(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier):
    url = "https://{}/gateway/cf/admin/features?routingId={}&projectIdentifier={}&accountIdentifier={}&orgIdentifier={}&environmentIdentifier={}&pageSize=50&pageNumber=0&metrics=false&summary=true&status=marked-for-cleanup".format(
        base_url, account_id, project_identifier, account_id, org_identifier, environment_identifier)
    try:
        headers = {"x-api-key": api_key}
        response = requests.get(url, params={}, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print("Error:", e)

    return None

def add_username_and_password_to_remote_url(url, username, password):
    parsed_url = urlparse(url)
    if not parsed_url.username and not parsed_url.password:
        updated_url = parsed_url._replace(netloc=f"{username}:{password}@{parsed_url.netloc}")
        final_url = urlunparse(updated_url)
    elif not parsed_url.password:
        updated_url = parsed_url._replace(netloc=f"{parsed_url.username}:{password}@{parsed_url.netloc.split('@')[-1]}")
        final_url = urlunparse(updated_url)
    elif not parsed_url.username:
        updated_url = parsed_url._replace(netloc=f"{username}:{parsed_url.password}@{parsed_url.netloc.split('@')[-1]}")
        final_url = urlunparse(updated_url)
    else:
        final_url = url
    return final_url

def get_repo_name_from_remote_url(url):
    parsed_url = urlparse(url)
    repo_name = parsed_url.path.rstrip(".git")
    if repo_name.startswith('/'):
        # Remove the leading slash
        repo_name = repo_name[1:]
    return repo_name

api_key = os.environ.get("PLUGIN_API_KEY", "")
if api_key == "":
    raise Exception("No API key")

github_token = os.environ.get("PLUGIN_GITHUB_TOKEN", "")
if github_token == "":
    raise Exception("No Github Token")

github_username = os.environ.get("PLUGIN_GITHUB_USERNAME", "")
if github_username == "":
    raise Exception("No Github Username")

account_id = os.environ.get("PLUGIN_ACCOUNT_ID", "")
if account_id == "":
    raise Exception("No Account ID")

org_identifier = os.environ.get("PLUGIN_ORG_IDENTIFIER", "default")
if org_identifier == "":
    raise Exception("No Organization Identifier")

environment_identifier = os.environ.get("PLUGIN_ENV_IDENTIFIER", "Test")
if environment_identifier == "":
    raise Exception("No Env Identifier")

project_identifier = os.environ.get("PLUGIN_PROJECT_IDENTIFIER", "")
if project_identifier == "":
    raise Exception("No Project Identifier")

new_branch_name = os.environ.get("PLUGIN_BRANCH_NAME", "stale_flag_removal_{}".format(generate_random_id_string()))

base_url = os.environ.get("PLUGIN_BASE_URL", "app.harness.io")

path_to_codebase = os.environ.get("PLUGIN_PATH_TO_CODEBASE", ".")

path_to_configurations = os.environ.get("PLUGIN_PATH_TO_CONFIGURATIONS", ".")

language = os.environ.get("PLUGIN_LANGUAGE", "go")

cleanup_comments = os.environ.get("PLUGIN_CLEANUP_COMMENTS", True)

author = git.Actor(github_username, "{}@users.noreply.github.com".format(github_username))

if __name__ == "__main__":
    repository_dir = "./"
    repo = git.Repo(repository_dir)

    # buffer size can cause commit issues, for some reason
    buffer_size_bytes = 10 * 1024 * 1024  # 10 megabytes
    repo.config_writer().set_value("http", "postBuffer", buffer_size_bytes).release()

    g = Github(github_token)
    user = g.get_user(github_username)

    remote_name = "origin"
    original_branch = repo.active_branch
    new_branch = repo.create_head(new_branch_name, original_branch)
    new_branch.checkout()

    print("Getting list of flags that have been marked for cleanup")
    flag_substitutions = get_flag_substitutions(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier)

    stale_flag_names = []
    for substitution in flag_substitutions:
        flag_name = substitution["stale_flag_name"]
        print("Generating commit to remove {}".format(flag_name))
        piranha_arguments = PiranhaArguments(
            language,
            paths_to_codebase = [path_to_codebase],
            path_to_configurations = path_to_configurations,
            substitutions = substitution,
            dry_run = False,
            cleanup_comments = cleanup_comments
        )
        execute_piranha(piranha_arguments)
        repo.git.add(".")

        stale_flag_names.append(flag_name)
        message = "Removes stale flag and associated code: {}".format(flag_name)
        repo.index.commit(message, author=author)

    repo_name = get_repo_name_from_remote_url(repo.remote(remote_name).url)

    remote_url = add_username_and_password_to_remote_url(repo.remote(remote_name).url, github_username, github_token)
    print("Pushing commits to Github")
    repo.remote(remote_name).set_url(remote_url)
    repo.git.push(remote_name, new_branch_name, force=True)

    github_repo = g.get_repo(repo_name)

    separator = ", "
    flag_names_str = separator.join(stale_flag_names)

    title = "[MAINT] Remove stale flags"
    body = """`
       The following stale flags were removed: {}
    """.format(flag_names_str)
    try:
        print("Creating PR")
        pr = github_repo.create_pull(
            title=title,
            body=body,
            base=original_branch.name,
            head=new_branch_name
        )
        print(f"Pull request created: {pr.html_url}")
    except Exception as e:
        print(f"Error creating pull request: {e}")