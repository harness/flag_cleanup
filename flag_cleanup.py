import os
import requests
from urllib.parse import urlparse, urlunparse
from github import Github
from harness_scm import HarnessSCM, Repo
from piranha_classes import PolyglotPiranha, JavascriptPiranha
import git
import secrets
import string

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
    if "features" in flag_json:
        features = flag_json["features"]
        for feature in features:
            identifier = feature["identifier"]
            output.append({"stale_flag_name": identifier, "treated": "true"})

    return output

def get_flag_data(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier):
    url = "https://{}/gateway/cf/admin/features?routingId={}&projectIdentifier={}&accountIdentifier={}&orgIdentifier={}&environmentIdentifier={}&pageSize=50&pageNumber=0&metrics=false&summary=true&status=marked-for-cleanup".format(
        base_url, account_id, project_identifier, account_id, org_identifier, environment_identifier)
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(url, params={}, headers=headers)
    except Exception as e:
        print(f"Error getting flag data: {e}")
        return {}

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

    return None

def get_env(api_key, base_url, account_id, org_identifier, project_identifier):
    env = "Test"
    url = f"https://{base_url}/gateway/cf/admin/environments?accountIdentifier={account_id}&orgIdentifier={org_identifier}&projectIdentifier={project_identifier}"
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(url, params={}, headers=headers)
    except Exception as e:
        print(f"Error getting environment: {e}")
        return env

    if response.status_code == 200:
        if "data" in response.json():
            data = response.json()["data"]
            if "environments" in data and len(data["environments"]) > 0:
                envDetails = data["environments"][0]
                if "identifier" in envDetails:
                    env = envDetails["identifier"]
    else:
        response.raise_for_status()

    return env

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
git_token = os.environ.get("PLUGIN_GIT_TOKEN", "")
if github_token == "" and git_token == "":
    raise Exception("No Git Token")
elif github_token == "" and git_token != "":
    github_token = git_token  # TODO this is me being lazy

github_username = os.environ.get("PLUGIN_GITHUB_USERNAME", "")
git_username = os.environ.get("PLUGIN_GIT_USERNAME", "")
if github_username == "" and git_username == "":
    raise Exception("No Git Username")
elif github_username == "" and git_username != "":
    github_username = git_username  # TODO this is me being lazy

account_id = os.environ.get("PLUGIN_ACCOUNT_ID", "")
if account_id == "":
    raise Exception("No Account ID")

org_identifier = os.environ.get("PLUGIN_ORG_IDENTIFIER", "default")
if org_identifier == "":
    raise Exception("No Organization Identifier")

project_identifier = os.environ.get("PLUGIN_PROJECT_IDENTIFIER", "")
if project_identifier == "":
    raise Exception("No Project Identifier")

new_branch_name = os.environ.get("PLUGIN_BRANCH_NAME", "stale_flag_removal_{}".format(generate_random_id_string()))

base_url = os.environ.get("PLUGIN_BASE_URL", "app.harness.io")

path_to_codebase = os.environ.get("PLUGIN_PATH_TO_CODEBASE", ".")

path_to_configurations = os.environ.get("PLUGIN_PATH_TO_CONFIGURATIONS", "./rules.toml")

language = os.environ.get("PLUGIN_LANGUAGE", "go")

cleanup_comments = os.environ.get("PLUGIN_CLEANUP_COMMENTS", True)

author = git.Actor(github_username, "{}@users.noreply.github.com".format(github_username))

if __name__ == "__main__":
    repository_dir = "./"
    repo = git.Repo(repository_dir)

    # buffer size can cause commit issues, for some reason
    buffer_size_bytes = 10 * 1024 * 1024  # 10 megabytes
    repo.config_writer().set_value("http", "postBuffer", buffer_size_bytes).release()

    if git_username == "":
        g = Github(github_token)
        user = g.get_user(github_username)  # Why is this never used?
        gitness = False
    else:  # TODO assume use of Harness SCM for now
        g = HarnessSCM(api_key)
        # repo = g.get_repo("reponame", account_id, project_identifier)
        # repo.create_pull("stale_flag_removal_QUBS8Q", "main", "my first PR", "hello world")
        gitness = True

    remote_name = "origin"
    original_branch = repo.active_branch
    new_branch = repo.create_head(new_branch_name, original_branch)
    new_branch.checkout()

    print("Getting environment details")
    environment_identifier = get_env(api_key, base_url, account_id, org_identifier, project_identifier)

    print("Getting list of flags that have been marked for cleanup")
    flag_substitutions = get_flag_substitutions(api_key, base_url, account_id, org_identifier, project_identifier, environment_identifier)

    if language.lower() == "javascript" or language.lower() == "js":
        p = JavascriptPiranha(language, path_to_codebase, path_to_configurations)
    else:
        p = PolyglotPiranha(language, path_to_codebase, path_to_configurations)

    commit_count = 0
    stale_flag_names = []
    for substitution in flag_substitutions:
        flag_name = substitution["stale_flag_name"]
        print("Generating commit to remove flag {}".format(flag_name))
        p.cleanupFlag(substitution, cleanup_comments)
        diff = repo.head.commit.diff(None)
        if len(diff) > 0:
            print("Committing changes made for flag {}".format(flag_name))
            repo.git.add(".")
            stale_flag_names.append(flag_name)
            message = "Removes stale flag and associated code: {}".format(flag_name)
            repo.index.commit(message, author=author)
            commit_count += 1
        else:
            print("No changes made for flag {}".format(flag_name))

    if commit_count > 0:
        repo_name = get_repo_name_from_remote_url(repo.remote(remote_name).url)

        remote_url = add_username_and_password_to_remote_url(repo.remote(remote_name).url, github_username, github_token)
        print(f"Pushing {commit_count} commits to Github")
        repo.remote(remote_name).set_url(remote_url)
        repo.git.push(remote_name, new_branch_name, force=True)

        if gitness:
            github_repo = g.get_repo(repo_name, account_id, project_identifier)
        else:
            github_repo = g.get_repo(repo_name)

        separator = ", "
        flag_names_str = separator.join(stale_flag_names)

        title = "[MAINT] Remove stale flags"
        body = """`
           The following stale flags were removed: {}
        """.format(flag_names_str)
        try:
            print("Creating Pull Request")
            pr = github_repo.create_pull(
                title=title,
                body=body,
                base=original_branch.name,
                head=new_branch_name
            )
            print(f"Pull request created: {pr.html_url}")
        except Exception as e:
            print(f"Error creating pull request: {e}")
    else:
        raise Exception("Nothing to commit, so no Pull Request")