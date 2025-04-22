import requests

def send_wxpusher_message(content, uids, app_token, topicIds, title=None):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "uids": uids,  # 关键修复：字段名从 "uid" 改为 "uids"
        "topicIds": topicIds,
        "summary": title,  # 关键字段：设置标题（显示在消息通知栏）
        "contentType": 1,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
    # 上传图片并获取图片URL
    image_url = upload_image(image_path)
    if not image_url:
        logging.info("图片上传失败，无法发送消息。")
        return

    # 使用HTML格式显示图片
    content = f'<img src="{image_url}" alt="Image">'
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "uids": uids,
        "topicIds": topicIds,
        "summary": title,
        "contentType": 2,  # HTML类型
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

if __name__ == "__main__":
    APP_TOKEN = "AT_PWwDFvgL1pymLhqCtuZfmLoPzKZgPOf1"  # 双色球专用 APP_TOKEN
    USER_UIDS = ["UID_wKraNNh5OPgSq2kP0neChHsNC3Sd"]
    send_wxpusher_message("Blue Balls: [5, 6, 7, 8, 9] \n Red Balls: [29, 23, 5, 10, 17, 7]", USER_UIDS, APP_TOKEN, [39909], "Test")