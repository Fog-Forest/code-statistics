import time

from code_statistics import *

imgurl = "https://ae01.alicdn.com/kf/U56b2fb24ff7b4e5fa05c5acf7d3d0318r.jpg"
file_name = "day.html"

if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  [日]")
    time1 = time.strftime("%Y-%m-%d 00:00:00")  # 开始时间
    time2 = time.strftime("%Y-%m-%d 23:59:59")  # 结束时间

    # header1
    content_save(
        "<!DOCTYPE html><html><head><title>GitLab代码提交量统计</title><meta charset=\"utf-8\"/><link href=\"https://cdn.jsdelivr.net/gh/Fog-Forest/cdn@2.1.6.2/markdown/markdown.css\" rel=\"stylesheet\" type=\"text/css\" /></head><body><h3>GitLab代码提交量统计(单位：行)  【日报】</h3><br><h5><font color=red>注：统计将会剔除所有合并操作</font></h5><h5>上次更新时间：" + time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()) + "</h5><br><blockquote><p>群组仓库</p></blockquote><ul><li><p><strong>master</strong></p><table><thead><tr><th>Git用户名</th><th>新增代码数</th><th>删除代码数</th><th>总计代码数</th><th>提交次数</th></tr></thead><tbody>",
        "w", file_name)

    gitlab_info(time1, time2, "group")  # 群组仓库统计
    gitlab_statistics_data(1)  # master
    gitlab_statistics_content(file_name)
    content_save(
        "</tbody></table></li><li><p><strong>dev</strong></p><table><thead><tr><th>Git用户名</th><th>新增代码数</th><th>删除代码数</th><th>总计代码数</th><th>提交次数</th></tr></thead><tbody>",
        "a", file_name)

    gitlab_statistics_data(2)  # dev
    gitlab_statistics_content(file_name)

    # 准备第二次统计前需要清空
    print("\n******************* switch *******************\n")
    info_master.clear()
    info_other.clear()

    # header2
    content_save(
        "</tbody></table></li></ul><blockquote><p>个人仓库</p></blockquote><ul><li><p><strong>all</strong></p><table><thead><tr><th>Git用户名</th><th>新增代码数</th><th>删除代码数</th><th>总计代码数</th><th>提交次数</th></tr></thead><tbody></tbody>",
        "a", file_name)

    gitlab_info(time1, time2, "user")  # 个人仓库统计
    gitlab_statistics_data(2)  # 个人仓直接统计全部分支
    gitlab_statistics_content(file_name)
    # footer
    content_save("</tbody></table></li></ul></body></html>", "a", file_name)

    dingding("http://localhost/" + file_name, imgurl, "[日报]")  # 不需要推送可以注释掉
    print("http://localhost/" + file_name)
