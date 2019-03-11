import re

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from IMMonitor import app, ret_val
from IMMonitor.db.common import db
from IMMonitor.analysis.model import MsgDetectResult
from IMMonitor.analysis import msg_detect
from IMMonitor.analysis.model import MsgDetectResult
from IMMonitor.wx.model import WxGroupMessage


ACCESS_TOKEN = '24.5066b60e5aa6af8577c4aadaec727cd8.2592000.1546587768.282335-15056684'
DETECT_URL_IMG = 'https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/user_defined'
DETECT_URL_TEXT = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam'

bp_analysis = Blueprint('bp_analysis', __name__)


# @app.route('/analysis/text_dectect')
# def text_dectect():
#     text = '明天去天安门闹事'
#     detect_result = msg_detect.detect_text(text)
#     detect_result = msg_detect.unify_detect_result(msg_type='Text', msg_id='123456', result=detect_result)
#     MsgDetectResult.batch_insert(detect_result)
#
#     return jsonify({
#         'ok': 'ok'
#     })


# 2.识别每个群违规信息关键词，绘制词云图
@app.route('/analysis/msg_keywords')
def msg_keywords():
    """
    识别并统计每个群违规信息关键词
    :return:
    """
    args = request.args
    label = args.get('label')
    group_id = args.get('group_id')

    if not all([label, group_id]):
        return jsonify(ret_val.gen(ret_val.CODE_PARAMS_ERR, extra_msg='需要传入label和group_id参数'))
    # 数据库交互，取出每条违规消息敏感词列表
    keywords = db.session.query(MsgDetectResult.result_info, WxGroupMessage)\
        .filter(and_(WxGroupMessage.group_id == group_id, MsgDetectResult.msg_id == WxGroupMessage.MsgId)).all()
    keywords_list = []
    for keyword in keywords:
        keywords_list += keyword[0].split(',')
    keywords_dict = {}
    # 桶排序统计每条违规消息敏感词频数
    for key_word in keywords_list:
        if not keywords_dict.get(key_word):
            keywords_dict[key_word] = 1
        else:
            keywords_dict[key_word] = keywords_dict[key_word] + 1

    return jsonify(ret_val.gen(ret_val.CODE_SUCCESS, data=keywords_dict))


# 3.每个群成员发送违规消息量统计
@app.route('/analysis/member_danger')
def member_danger():
    """
    统计指定群成员发送违规消息量
    :return:
    """
    args = request.args
    label = args.get('label')
    group_id = args.get('group_id')

    if not all([label, group_id]):
        return jsonify(ret_val.gen(ret_val.CODE_PARAMS_ERR, extra_msg='需要传入label和group_id参数'))
    # 数据库交互，取出发出每条违规消息的成员名列表
    danger_list = db.session.query(MsgDetectResult, WxGroupMessage.FromUserNickName)\
        .filter(and_(WxGroupMessage.group_id == group_id, MsgDetectResult.msg_id == WxGroupMessage.MsgId)).all()
    member_list = {}
    # 桶排序实现群成员违规消息统计
    for danger in danger_list:
        UserNickName = danger[1]
        if not member_list.get(UserNickName):
            member_list[UserNickName] = 1
        else:
            member_list[UserNickName] = member_list[UserNickName] + 1

    return jsonify(ret_val.gen(ret_val.CODE_SUCCESS, data=member_list))


# 4. 统计单个群消息总数，每种违规消息（比如暴恐，色情，政治敏感等）数量
@app.route('/analysis/group_danger')
def group_danger():
    args = request.args
    label = args.get('label')
    group_id = args.get('group_id')
    if not all([label, group_id]):
        return jsonify(ret_val.gen(ret_val.CODE_PARAMS_ERR, extra_msg='需要传入label和group_id参数'))

    danger_list = db.session.query(WxGroupMessage, MsgDetectResult)\
        .filter(and_(WxGroupMessage.group_id == group_id,
                     WxGroupMessage.MsgId == MsgDetectResult.msg_id)).all()

    label_dict = {'1': 0, '2': 0, '3': 0, '4': 0, '8': 0, '21': 0, '22': 0, '23': 0, '24': 0, '25': 0}
    # img_type = {'1': '色情', '2': '性感', '3': '暴恐', '4': '恶心', '8': '政治人物'}
    # text_label = {'21': '暴恐违禁', '22': '文本色情', '23': '政治敏感', '24': '恶意推广', '25': '低俗辱骂'}
    # 违禁信息类别融合
    # '色情性感':  # 1 + 2 + 22
    # '暴恐违禁':  # 3 + 21
    # '政治敏感':  # 8 + 23
    # '低俗辱骂':  # 25
    # '恶心反感':  # 4 +24
    group_danger_dict = {'色情性感': 0, '暴恐违禁': 0, '政治敏感': 0, '低俗辱骂': 0, '恶心反感': 0}
    for danger in danger_list:
        label_dict[str(danger[1].result_label)] += 1
    group_danger_dict['色情性感'] = label_dict['1'] + label_dict['2'] + label_dict['22']
    group_danger_dict['暴恐违禁'] = label_dict['3'] + label_dict['21']
    group_danger_dict['政治敏感'] = label_dict['8'] + label_dict['23']
    group_danger_dict['低俗辱骂'] = label_dict['25']
    group_danger_dict['恶心反感'] = label_dict['4'] + label_dict['24']

    return jsonify(ret_val.gen(ret_val.CODE_SUCCESS, data=group_danger_dict))


# 5.单个群每天各时段违规消息占比变化趋势图
@app.route('/analysis/datetime_danger')
def datetime_danger():
    """
    单个群每天各时段违规消息数量
    :return: 每天违规消息数量和每天中各小时的违规消息数量
    """
    args = request.args
    label = args.get('label')
    group_id = args.get('group_id')

    if not all([label, group_id]):
        return jsonify(ret_val.gen(ret_val.CODE_PARAMS_ERR, extra_msg='需要传入label和group_id参数'))

    # 数据库交互，取出发出每条违规消息的成员名列表
    date_time_list = db.session.query(MsgDetectResult, WxGroupMessage.date_created)\
        .filter(and_(WxGroupMessage.group_id == group_id, MsgDetectResult.msg_id == WxGroupMessage.MsgId)).all()

    danger_dict = {"day": 0, "hour": 0}
    danger_day_dict = {}
    danger_hour_dict = {}
    # 桶排序实现群成员违规消息统计
    for time in date_time_list:
        # time[1]: 2019-03-09 11:14:47.574616
        # 统计每一天的违规消息数量
        date_temp = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", str(time[1]))
        day = date_temp.group(0)
        if not danger_day_dict.get(day):
            danger_day_dict[day] = 1
        else:
            danger_day_dict[day] += 1
        # 统计每天中各小时的违规消息数量
        hour_temp = re.search(r"(\d{1,2}:\d{1,2})", str(time[1]))
        hour = hour_temp.group(1).split(":")[0]
        if not danger_hour_dict.get(hour):
            danger_hour_dict[hour] = 1
        else:
            danger_hour_dict[hour] += 1

    danger_dict['day'] = danger_day_dict
    danger_dict['hour'] = danger_hour_dict
    return jsonify(ret_val.gen(ret_val.CODE_SUCCESS, data=danger_dict))

