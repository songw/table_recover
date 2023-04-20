APPId = "5bda64f4"
APIKey = "9f4e4a0273f46abc042c61c64fd615da"
APISecret = "0fa03e012fa1d4364845913af7ef325c"

# 请求数据
request_data = {
	"header":{
		"app_id":"123456",
		"uid":"39769795890",
		"did":"SR082321940000200",
		"imei":"8664020318693660",
		"imsi":"4600264952729100",
		"mac":"6c:92:bf:65:c6:14",
		"net_type":"wifi",
		"net_isp":"CMCC",
		"status":3,
		"res_id":""
	},
	"parameter":{
		"ocr":{
			"language":"doc",
			"table_option":"1",
			"element_option":"1",
			"char_option":"0",
			"ocr_output_text":{
				"encoding":"utf8",
				"compress":"raw",
				"format":"json"
			}
		}
	},
	"payload":{
		"image":{
			"encoding":"jpeg",
			"image":"",
			"status":3
		}
	}
}

# 请求地址
# request_url = "https://cn-huadong-1.xf-yun.com/v1/private/s5893ced9"
#request_url = "http://cn-huadong-1.xf-yun.com/v1/private/s001fe20b"
request_url = "http://cn-huadong-1.xf-yun.com/v1/private/sfe419816"
