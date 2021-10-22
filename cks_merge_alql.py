#作者仓库:https://github.com/spiritLHL/qinglong_auto_tools
#觉得不错麻烦点个star谢谢


'''
cron: 1
new Env('二叉树合并ck');
'''

#在脚本管理里修改这个文件的配置，然后保存，然后禁用 二叉树合并ck 这个任务，有需要再点运行

# 主青龙，合并结果存储的容器，事先需要在容器里创建应用，给所有权限，然后重启容器，应用设置才会生效，
# 本脚本不含转ck功能，只合并ck，默认合并的环境变量名为JD_COOKIE，其他变量名自己按照下面注释改

merge_id = ""
merge_secret = ""
merge_url = ""


# 被合并ck的分容器，事先需要在分容器里创建应用，给所有权限，然后重启容器，应用设置才会生效
# 按照格式有几个写几个，没有的空的删除
client_ids=['','','','']
client_secrets=['','','','']
urllist = ["http://xxxx:xxxx/","","",'']

import requests
import time
import json
import re

requests.packages.urllib3.disable_warnings()


def gettimestamp():
    return str(int(time.time() * 1000))

def gettoken(self,url_token):
    r = requests.get(url_token).text
    res = json.loads(r)["data"]["token"]
    self.headers.update({"Authorization": "Bearer "+res})

def login(self, baseurl, cilent_id_temp, cilent_secret_temp):
    url_token = baseurl+'open/auth/token?client_id='+cilent_id_temp+'&client_secret='+cilent_secret_temp
    gettoken(self, url_token)

def getitem(self, baseurl, key , typ):
    url = baseurl + typ + "/envs?searchValue=%s&t=%s" % (key, gettimestamp())
    r = self.get(url)
    item = json.loads(r.text)["data"]
    return item


def getckitem(self, baseurl, key, typ):
    url = baseurl + typ + "/envs?searchValue=JD_COOKIE&t=%s" % gettimestamp()  # 获取ck的变量名为JD_COOKIE
    r = self.get(url)
    for i in json.loads(r.text)["data"]:
        if key in i["value"]:
            return i
    return []

def update(self, baseurl, typ, text, qlid):
    url = baseurl + typ + "/envs?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    data = {
        "name": "JD_COOKIE", # 更新ck的变量名为JD_COOKIE
        "value": text,
        "_id": qlid
    }
    r = self.put(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def insert(self, baseurl, typ, text):
    url = baseurl + typ + "/envs?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    data = []
    data_json = {
        "value": text,
        "name": "JD_COOKIE" # 插入ck的变量名为JD_COOKIE
    }
    data.append(data_json)
    r = self.post(url, json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False

if __name__ == '__main__':
    s = requests.session()
    login(s, merge_url, merge_id, merge_secret)
    c_list = []

    count = 0
    for i in urllist:
        a = requests.session()
        login(a, urllist[count], client_ids[count], client_secrets[count])
        cks = getitem(a, urllist[count], "JD_COOKIE", "open") # 获取ck的变量名为JD_COOKIE
        for i in cks:
            tp = i['value']
            ptpin = re.findall(r"pt_pin=(.*?);", tp)[0]
            ptpin = "pt_pin=" + ptpin + ';'
            ptkey = re.findall(r"pt_key=(.*?);", tp)[0]
            ptkey = "pt_key=" + ptkey + ';'
            c = ptkey + ptpin
            c_list.append(c)
        count += 1
        print("分容器{}的所有ck获取完毕\n".format(count))

    print("合并ck中\n")
    result_list = list(set(c_list))
    co = 0
    for k in c_list:
        co += 1
        ptpin = re.findall(r"pt_pin=(.*?);", k)[0]
        ptpin = "pt_pin=" + ptpin
        item = getckitem(s, merge_url, ptpin, "open")
        if item != []:
            qlid = item["_id"]
            if update(s, merge_url, "open", k, qlid):
                print("第%s个JD_COOKIE更新成功,pin为%s" % (co, ptpin[7:]))
            else:
                print("第%s个JD_COOKIE更新失败,pin为%s" % (co, ptpin[7:]))
        else:
            if insert(s, merge_url, "open", k):
                print("第%s个JD_COOKIE添加成功,pin为%s" % (co, ptpin[7:]))
            else:
                print("第%s个JD_COOKIE添加失败,pin为%s" % (co, ptpin[7:]))


    print("")

    print("合并ck完毕")


