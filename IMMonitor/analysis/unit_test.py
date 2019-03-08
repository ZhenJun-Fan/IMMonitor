# !/usr/bin/python3.6
# coding:utf-8
"""
-------------------------------------------------
  Author:        fan_zj
  Date：         2019-3-8
-------------------------------------------------
"""

# import os
# import sys
from IMMonitor.analysis import msg_detect, msg_display, model


# 单元测试代码

# BASE_DIR = os.path.dirname(__file__)
# sys.path.append(BASE_DIR)
result = msg_detect.detect_text('我们明天拿枪去天安门杀人，我草你妈')
result_unify = msg_detect.unify_detect_result('Text', '1111', result)
print(result)
print(result_unify)

