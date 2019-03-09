# !/usr/bin/python3.6
# coding:utf-8
"""
-------------------------------------------------
  Author:        fan_zj
  Date：         2019-3-8
-------------------------------------------------
"""

from IMMonitor.db.common import db
from IMMonitor.analysis.model import MsgDetectResult
from IMMonitor.wx.model import WxGroupMessage, WxGroupMember


# 2.识别每个群敏感信息关键词，绘制词云图


# 3.每个群成员发送违规消息量统计
def account_msg_out_line(msg_id_list):
    """
    计算某个成员的违规消息数量
    :param      msg_id_list:    成员所有消息的id列表
    :return:    num:            违规消息数目
    """
    num = 0
    # 获得检测结果数据库中所有消息id列表
    temp_msg_id_list = db.session.query(MsgDetectResult.msg_id).all()
    for msg_id in msg_id_list:
        if msg_id in temp_msg_id_list:
            num += 1
    return num


def get_user_name_msg_id(group_name, user_name):
    """
    获得某个成员所有消息的id列表
    :param      group_name:      某个成员所对应的群名称
    :param      user_name:       某个成员名称/昵称
    :return:    msg_id_list:     某个成员所有消息的id列表
    """
    msg_id_list = db.session.query(WxGroupMessage.MsgId).filter_by(GroupNickName=group_name, FromUserName=user_name).all()
    return msg_id_list


def user_name_msg_out_line_num(group_name):
    """
    统计并显示群所有成员的违规消息
    :param      group_name:                                   群名称
    :return:    [{'name': user_name, 'count': num}, ...]      返回给前端的数据列表
    """
    user_msg_out_line_num_list = []
    user_msg_out_line_num_dict = {}
    # 获得群所有成员昵称
    user_name_list = db.session.query(WxGroupMember.NickName).filter_by(group_name=group_name).all()
    for user_name in user_name_list:
        user_msg_out_line_num_dict['name'] = user_name
        user_msg_out_line_num_dict['count'] = account_msg_out_line(user_name)
        user_msg_out_line_num_list.append(user_msg_out_line_num_dict)
    # return user_msg_out_line_num_list
    return jsonify(ret_val.gen(ret_val.CODE_SUCCESS, data=group_danger_dict))

