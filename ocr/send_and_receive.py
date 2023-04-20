import copy
import base64
from ocr.utils import *
import requests
import json
from urllib import parse


def prepare_request_data(request_data, f_data):
    new_request_data = copy.deepcopy(request_data)

    new_request_data['header']['status'] = 3
    new_request_data['payload']["image"]["image"] = base64.b64encode(f_data).decode()
    new_request_data['payload']["image"]['status'] = 3

    return new_request_data



def execute(request_url, request_data, method, app_id, api_key, api_secret, f_data):
    # 获取请求url
    auth_request_url = build_auth_request_url(request_url, method, api_key, api_secret)

    url = parse.urlparse(request_url)
    headers = {'content-type': "application/json", 'host': url.hostname, 'app_id': app_id}
    # 准备待发送的数据
    new_request_data = prepare_request_data(request_data, f_data)
    response = requests.post(auth_request_url, data=json.dumps(new_request_data), headers=headers)
    return response

# 处理响应数据
def deal_response(response):
    temp_result = json.loads(response.content.decode())
    finalResult = base64.b64decode(temp_result['payload']['ocr_output_text']['text']).decode()
    finalResult = finalResult.replace(" ", "").replace("\n", "").replace("\t", "").strip()
    return finalResult
    # extract_invoice(finalResult)
    
