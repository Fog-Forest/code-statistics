#!/usr/bin/python3
# coding=utf8
# @Author: Mario
# @Date  : 2021/01/01
# @Desc  : GitLab 按时间查看各用户代码提交量官方API版(钉钉推送版)

import datetime
import json

import requests
from dateutil.parser import parse

# 需修改如下四条信息
gitlab_url = ""  # GitLab 地址
private_token = ""  # GitLab Access Tokens（管理员权限）
report_path = "/data/"  # 生成的报告文件存放目录
dingding_token = ""  # 钉钉机器人token

info_master = []
info_other = []
statistics = {}

# 需要去除的统计的 Git 用户名
exclude_names = ["Administrator",]

headers = {
    'Connection': 'close',
}


# UTC时间转时间戳
def utc_time(time):
    dt = parse(time)
    return int(dt.timestamp())


# 根据日期获取星期
def get_week_num(date):
    week = datetime.datetime.strptime(date, "%Y-%m-%d").weekday() + 1
    if week == 1:
        return "周一"
    elif week == 2:
        return "周二"
    elif week == 3:
        return "周三"
    elif week == 4:
        return "周四"
    elif week == 5:
        return "周五"
    elif week == 6:
        return "周六"
    else:
        return "周日"


# 获取 GitLab 上的所有项目
def gitlab_projects(project_kind):
    project_ids = []
    page = 1
    while True:
        url = gitlab_url + "api/v4/projects/?private_token=" + private_token + "&page=" + str(page) + "&per_page=20"
        while True:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                break
            except Exception as e:
                print(e)
                continue
        projects = json.loads(res.text)
        if len(projects) == 0:
            break
        else:
            for project in projects:
                if project["namespace"]["kind"] != project_kind or project["archived"]:  # 统计哪种类型未归档的仓库 user、group
                    continue
                else:
                    # print(project["namespace"]["name"] + " ID:" + str(project["id"]) + " 描述：" + project["description"])
                    project_ids.append(project["id"])
            page += 1
    print("共获取到 " + str(len(project_ids)) + " 个有效项目")
    return project_ids


# 获取 GitLab 上的项目 id 中的分支
def project_branches(project_id):
    branch_names = []
    page = 1
    while True:
        url = gitlab_url + "api/v4/projects/" + str(
            project_id) + "/repository/branches?private_token=" + private_token + "&page=" + str(page) + "&per_page=20"
        while True:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                break
            except Exception as e:
                print(e)
                continue
        branches = json.loads(res.text)
        if len(branches) == 0:
            break
        else:
            for branch in branches:
                branch_names.append(branch["name"])
            page += 1
    return branch_names


# 获取 GitLab 上的项目分支中的 commits，当 title 或 message 首单词为 Merge 时，表示合并操作，剔除此代码量
def project_commits(project_id, branch, start_time, end_time):
    commit_ids = []
    page = 1
    while True:
        url = gitlab_url + "api/v4/projects/" + str(
            project_id) + "/repository/commits?ref_name=" + branch + "&private_token=" + private_token + "&page=" + str(
            page) + "&per_page=20"
        while True:
            try:
                res = requests.get(url, headers=headers, timeout=10)
                break
            except Exception as e:
                print(e)
                continue
        commits = json.loads(res.text)
        if len(commits) == 0:
            break
        else:
            for commit in commits:
                if "Merge" in commit["title"] or "Merge" in commit["message"] or "合并" in commit["title"] or "合并" in \
                        commit["message"]:  # 不统计合并操作
                    continue
                elif utc_time(commit["authored_date"]) < utc_time(start_time) or utc_time(
                        commit["authored_date"]) > utc_time(end_time):  # 不满足时间区间
                    continue
                else:
                    commit_ids.append(commit["id"])
            page += 1
    return commit_ids


# 根据 commits 的 id 获取代码量，type: 1 为主分支，2为其他分支
def commit_code(project_id, commit_id, branch_type):
    global info_master, info_other
    url = gitlab_url + "api/v4/projects/" + str(
        project_id) + "/repository/commits/" + commit_id + "?private_token=" + private_token
    while True:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            break
        except Exception as e:
            print(e)
            continue
    data = json.loads(res.text)
    obj = {"name": data["author_name"], "additions": data["stats"]["additions"],
           "deletions": data["stats"]["deletions"], "total": data["stats"]["total"]}  # Git工具用户名,新增代码数,删除代码数,总计代码数
    if data["author_name"] not in exclude_names:  # 去除不需要统计的Git用户名
        if branch_type == 1:
            info_master.append(obj)
        elif branch_type == 2:
            info_other.append(obj)
        # else:
        # do some things


# GitLab 数据查询
def gitlab_info(start_time, end_time, project_kind):
    for project_id in gitlab_projects(project_kind):  # 遍历所有项目ID
        for branch_name in project_branches(project_id):  # 遍历每个项目中的分支
            if branch_name == "master" and project_kind != "user":  # 主分支（个人仓直接统计全部）
                for commit_id in project_commits(project_id, branch_name, start_time, end_time):  # 遍历每个分支中的 commit id
                    commit_code(project_id, commit_id, 1)  # 获取代码提交量
            else:  # 其他分支
                for commit_id in project_commits(project_id, branch_name, start_time, end_time):
                    commit_code(project_id, commit_id, 2)  # 获取代码提交量


#  统计数据处理
def gitlab_statistics_data(branch_type):
    global statistics
    statistics.clear()

    name = []  # Git工具用户名
    additions = []  # 新增代码数
    deletions = []  # 删除代码数
    total = []  # 总计代码数
    times = []  # 提交次数

    if branch_type == 1:
        info = info_master
    elif branch_type == 2:
        info = info_other
    # else
    # do some things

    for i in info:
        for key, value in i.items():
            if key == "name":
                name.append(value)
            if key == "additions":
                additions.append(value)
            if key == "deletions":
                deletions.append(value)
            if key == "total":
                total.append(value)
            times.append(1)  # 提交次数
    array = list(zip(name, additions, deletions, total, times))
    # print(array)

    # 去重累加
    for j in array:
        name = j[0]
        additions = j[1]
        deletions = j[2]
        total = j[3]
        times = j[4]
        if name in statistics.keys():
            statistics[name][0] += additions
            statistics[name][1] += deletions
            statistics[name][2] += total
            statistics[name][3] += times
        else:
            statistics.update({name: [additions, deletions, total, times]})
        # else:
        # do some things
    return statistics


# 代码统计内容列表处理
def gitlab_statistics_content(file_name):
    for i in statistics.keys():
        content_save("<tr><td>" + str(i) + "</td><td>" + str(statistics[i][0]) + "</td><td>" + str(
            statistics[i][1]) + "</td><td>" + str(statistics[i][2]) + "</td><td>" + str(
            statistics[i][3]) + "</td></tr>", "a", file_name)


# 保存数据到文件
def content_save(data, mode, file_name):
    file = open(report_path + "/" + file_name, mode, encoding='utf-8')
    file.write(data)
    file.close()


# 钉钉通知
def dingding(url, imgurl, mes):
    content = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": "GitLab代码提交量统计[]",
            "text": "![](" + imgurl + ")GitLab代码提交量统计" + mes,
            "hideAvatar": "0",
            "btnOrientation": "0",
            "singleTitle": "点击查看详情",
            "singleURL": url
        }
    }
    json_headers = {'Content-Type': 'application/json;charset=utf-8'}
    result = requests.post("https://oapi.dingtalk.com/robot/send?access_token=" + dingding_token, json.dumps(content),
                           headers=json_headers).text
    print(result)
