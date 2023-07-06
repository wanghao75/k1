import json
import sys

import requests
import yaml
import os


def get_org_repos(t):
    org = "ci-robot"
    page = 1
    org_repos = []
    uri = "https://gitee.com/api/v5/users/{}/repos".format(org)
    while True:
        parameter = {
            "access_token": t,
            "page": page,
            "per_page": 100
        }

        res = requests.get(url=uri, params=parameter)
        if res.status_code != 200:
            continue

        if len(res.json()) == 0:
            break

        for r in res.json():
            if r.get("full_name").startswith("ci-robot"):
                org_repos.append(r.get("full_name"))
        page += 1

    return org_repos


def get_src_org_repos(t):
    org = "src-op"
    page = 1
    src_org_repos = []
    uri = "https://gitee.com/api/v5/orgs/{}/repos".format(org)
    while True:
        parameter = {
            "access_token": t,
            "page": page,
            "per_page": 100
        }

        res = requests.get(url=uri, params=parameter)
        if res.status_code != 200:
            continue

        if len(res.json()) == 0:
            break

        for r in res.json():
            src_org_repos.append(r.get("full_name"))
        page += 1

    return src_org_repos


def load_and_compare_file(l1, l2):
    print(l1, l2)
    with open("./repositories_branches_map.yaml", "r", encoding="utf-8") as f:
        d = yaml.safe_load(f.read())

    maps = {}
    for i in d.get("mapping"):
        if i not in l1 and i not in l2:
            maps[i] = d.get("mapping").get(i)
        else:
            continue
    return maps


def create_fork_and_complete_config(map_dict, token, github_token):
    workdir = os.popen("pwd").readlines()[0].split("\n")[0]
    os.popen("git clone https://oauth2%s:@github.com/fixproblems/infra-openeuler" % github_token).readlines()
    with open("%s/infra-openeuler/applications/patchwork/secrets.yaml" % workdir, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f.read())

    d = {}
    for k, v in map_dict:
        org, repo = k.split("/")[0], k.split("/")[1]
        uri = "https://gitee.com/api/v5/repos/{}/{}/forks".format(org, repo)
        if k.startswith("src"):
            r = requests.post(url=uri, data={"access_token": token, "organization": "src-op"})
            if r.status_code != 201:
                continue
        else:
            r = requests.post(url=uri, data={"access_token": token,})
            if r.status_code != 201:
                continue
        d[v.get("env").get("host")] = {"path": "secrets/data/openeuler/patchwork", "key": v.get("env").get("host")}
        d[v.get("env").get("pass")] = {"path": "secrets/data/openeuler/patchwork", "key": v.get("env").get("pass")}

    data.get("spec").get("keysMap").update(d)
    with open("%s/infra-openeuler/applications/patchwork/secrets.yaml" % workdir, "w", encoding="utf-8") as ff:
        yaml.safe_dump(data, ff, sort_keys=False)

    os.chdir("%s/infra-openeuler" % workdir)
    os.popen("git add . && git commit -am 'refresh secrets' && git push").readlines()
    os.chdir(workdir)

    # make pr
    uri = "https://api.github.com/repos/opensourceways/infra-openeuler/pulls"
    headers = {
        "Authorization": "token %s" % github_token
    }
    payload = {
        "head": "fixproblems:master",
        "base": "master",
        "title": "refresh config"
    }

    requests.post(url=uri, headers=headers, data=json.dumps(payload))


def main():
    token = sys.argv[1]
    gh_token = sys.argv[2]
    if token == "" or gh_token == "":
        sys.exit(1)

    m = load_and_compare_file(get_org_repos(token), get_src_org_repos(token))
    print(m)
    create_fork_and_complete_config(m, token, gh_token)


if __name__ == '__main__':
    main()
