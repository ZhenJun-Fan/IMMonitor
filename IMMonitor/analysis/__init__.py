from IMMonitor import app, ret_val
from flask import Blueprint, jsonify, request
from IMMonitor.analysis import msg_detect
from IMMonitor.analysis.model import MsgDetectResult


from flask import Blueprint, jsonify
from sqlalchemy import and_

from IMMonitor import app
from IMMonitor.db.common import db
from IMMonitor.analysis.model import MsgDetectResult
from IMMonitor.wx.model import WxGroupMessage


ACCESS_TOKEN = '24.5066b60e5aa6af8577c4aadaec727cd8.2592000.1546587768.282335-15056684'
DETECT_URL_IMG = 'https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/user_defined'
DETECT_URL_TEXT = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam'


bp_analysis = Blueprint('bp_analysis', __name__)


@app.route('/analysis/text_dectect')
def text_dectect():
    text = '明天去天安门闹事'
    detect_result = msg_detect.detect_text(text)
    detect_result = msg_detect.unify_detect_result(msg_type='Text', msg_id='123456', result=detect_result)
    MsgDetectResult.batch_insert(detect_result)
    return jsonify({
        'ok': 'ok'
    })


# @app.route('/analysis/group_danger')
# def group_danger():
#     danger_list = db.session.query(WxGroupMessage, MsgDetectResult)\
#         .filter(and_(MsgDetectResult.result_label == 13,
#                      WxGroupMessage.MsgId == MsgDetectResult.msg_id)).all()
#     for danger in danger_list:
#         print(danger[0].GroupNickName,
#               danger[0].FromUserNickName,
#               danger[0].Content,
#               danger[1].result_info,
#               danger[1].result_label)
#     return jsonify({'ok': 'ok'})


# 4. 统计单个群消息总数，每种违规消息（比如暴恐，色情，政治敏感等）数量，计算各种违规消息占比，以雷达图展示
@app.route('/analysis/group_danger')
def group_danger():
    args = request.args
    label = args.get('label')
    group_id = args.get('group_id')
    if not all([label,group_id]):
        return jsonify(ret_val.gen(ret_val.CODE_PARAMS_ERR, extra_msg='需要传入label和group_username参数'))

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

