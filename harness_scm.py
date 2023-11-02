import requests


class HarnessSCM:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://app.harness.io/gateway/code/api/v1"  # Replace this with your API base URL

    def get_repo(self, repo_id, account_id, project_id, **kwargs):
        print("Repo", repo_id)
        repo_id = repo_id.split("/")[-1]
        print(repo_id)
        org_id = kwargs.get("org_id", "default")
        endpoint = f"{self.base_url}/repos/{account_id}/{org_id}/{project_id}/{repo_id}/+/?routingId={account_id}"
        headers = {
            'x-api-key': self.token
        }
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return Repo(self.token, response.json())
        else:
            print(response.request)
            print(endpoint)
            raise Exception(f"Failed to retrieve repository: {response.status_code}")


class Repo:
    def __init__(self, token, data, **kwargs):
        self.token = token
        self.data = data
        self.base_url = kwargs.get("base_url", "https://app.harness.io/gateway/code/api/v1")

    def create_pull(self, **kwargs):

        endpoint = f"{self.base_url}/repos/{self.data['path']}/+/pullreq"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.token
        }

        data = {
            "target_branch": kwargs.get("base", "main"),
            "source_branch": kwargs.get("head", "main"),
            "title": kwargs.get("title", "test"),
            "description": kwargs.get("body", "test"),
            "is_draft": False
        }

        response = requests.post(endpoint, headers=headers, json=data)

        if response.status_code == 201:
            print("Pull request created successfully!")
            return response.json()
        else:
            raise Exception(f"Failed to create pull request: {response.status_code}")


# Example usage
# token = ""
# reponame = "flag_cleanup"
# g = HarnessSCM(token)
# repo = g.get_repo("flag_cleanup", "6_vVHzo9Qeu9fXvj-AcbCQ", "Feature_Flags_Demo")
# repo.create_pull(
#                 title="my second PR",
#                 body="hi!",
#                 base="main",
#                 head="stale_flag_removal_QUBS8Q"
#             )
