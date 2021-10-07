# GitLab 开发者代码提交量统计
统计 GitLab 所有开发者代码提交情况，按删除、新增、总计、次数四个维度展示，支持日、月、周三种时间范围，自动将统计结果推送钉钉群


### 使用说明
1. 安装需要的支持库
`pip install -r requirements.txt`

2. 修改 `code_statistics.py` 文件 L13-L24 内容以及 `day.py、month.py、week.py` 三个文件的倒数第二行内容，最后运行即可，这三个文件分别对应 日、月、周三个统计时间范围，需要统计哪个时间就运行哪个脚本


### 自动运行
Linux 设置 crontab 定时任务即可

```bash
50 20 * * 1-6  bash run.sh day.py
00 21 * * 7    bash run.sh week.py
30 10 2 1-12 * bash run.sh month.py
```


### 已知问题
1. 统计人数超过 25 人，Excel模板排版会有问题，因为数据直接由Excel处理的，所以需要拖下表格让他支持更多行
