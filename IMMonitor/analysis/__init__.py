from IMMonitor import app
from flask import Blueprint, jsonify
from IMMonitor.analysis import msg_detect
from IMMonitor.analysis.model import MsgDetectResult

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
