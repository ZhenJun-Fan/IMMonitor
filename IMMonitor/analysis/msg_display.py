# !/usr/bin/python3.6
# coding:utf-8
"""
-------------------------------------------------
  Author:        fan_zj
  Date：         2019-3-8
-------------------------------------------------
"""
from IMMonitor.db.common import db
from IMMonitor.analysis.model import DetectResults
from IMMonitor.wx.model import WxGroupMessage, WxGroupMember


def account_msg_out_line(msg_id_list):
    """
    计算某个成员的违规消息数量
    :param msg_id_list: 成员所有消息的id列表
    :return: num: 违规消息数目
    """
    num = 0
    # 获得检测结果数据库中所有消息id列表
    temp_msg_id_list = db.session.query(DetectResults.msg_id).all()
    for msg_id in msg_id_list:
        if msg_id in temp_msg_id_list:
            num += 1
    return num


def get_username_msg_id(group_name, user_name):
    """
    获得某个成员所有消息的id列表
    :param groupname: 成员所对应的群名称
    :param username: 成员名称/昵称
    :return: msg_id_list: 所有消息的id列表
    """
    msg_id_list = db.session.query(WxGroupMessage.MsgId).filter_by(GroupNickName=group_name, FromUserName=user_name).all()
    return msg_id_list


def user_name_msg_out_line_display(group_name, top_No=20):
    """
    统计并显示群所有成员的违规消息
    :param groupname: 群名称
    :return:
    """
    user_msg_out_line_num = {}
    # 获得群所有成员昵称
    user_nmae_list = db.session.query(WxGroupMember.NickName).all()
    for user_name in user_nmae_list:
        temp_num = account_msg_out_line(user_name)
        user_msg_out_line_num['user_name'] = temp_num




