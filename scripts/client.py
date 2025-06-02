# -*- coding: gbk -*-
import os.path

import requests
import json
import time

# 服务器地址
# server_addr = "127.0.0.1:8080"
server_addr = '192.168.7.205:18180'

def train():
    global reference_audio_text, asr_format_audio_url
    # 预处理和转换请求的URL和数据
    preprocess_url = f"http://{server_addr}/v1/preprocess_and_tran"
    preprocess_data = {
        "format": "wav",
        # "reference_audio": "https://digital-public.obs.myhuaweicloud.com/video_split/20240906/df73a3a3a4df46528a219dc6c8a63bc5/df73a3a3a4df46528a219dc6c8a63bc5_denoise.wav",
        # "reference_audio": 'https://cdn.guiji.ai/vpp/vpp/2024/11/28/1179229354404749313.wav',
        # "reference_audio": 'http://192.168.6.131:9000/media/wav/t111.wav',
        # "reference_audio": 'https://digital-public-dev.obs.cn-east-3.myhuaweicloud.com/vpp/vpp/2025/02/17/1208702486668517376/1088912893313037256/1088912893313037256.wav',
        # "reference_audio": 'https://digital-public-dev.obs.cn-east-3.myhuaweicloud.com/vpp/vpp/2025/02/17/1208704896291971072/1088915387820815346/1088915387820815346.wav',
        # "reference_audio": 'http://192.168.6.131:9000/media/tts/short_12s.wav',
        # "reference_audio": 'short_12s.wav',
        "reference_audio": '1122.wav',
        "lang": "zh"
    }

    start_time = time.time()
    # 发起预处理和转换请求
    print(f'发起训练， url:{preprocess_url}, data:{json.dumps(preprocess_data)}')
    preprocess_response = requests.post(preprocess_url, headers={"Content-Type": "application/json"},
                                        data=json.dumps(preprocess_data))
    print(f'训练返回结果：{preprocess_response.text}')
    # 解析响应中的reference_audio_text和asr_format_audio_url
    preprocess_result = preprocess_response.json()
    code = preprocess_result.get("code")
    if code != 0:
        print(f'预处理失败，错误码：{code}')
        exit(1)
    print('>>>>>>训练成功，开始调用tts')
    reference_audio_text = preprocess_result.get("reference_audio_text")
    asr_format_audio_url = preprocess_result.get("asr_format_audio_url")
    print(f"Reference Audio Text: {reference_audio_text}")
    print(f"ASR Format Audio URL: {asr_format_audio_url}")
    print(f'耗时：{time.time()-start_time}')
    return reference_audio_text, asr_format_audio_url


def tts(r_text, r_audio, text, save_path='/code/data/output.wav'):
    start_time = time.time()
    print(f'准备调用tts， r_text:{r_text}, r_audio:{r_audio}, text:{text}, save_path:{save_path}')
    # TTS调用的URL和数据
    invoke_url = f"http://{server_addr}/v1/invoke"
    invoke_data = {
        "speaker": "487180693714239488",
        'text': text,
        "format": "wav",
        "topP": 0.7,
        "max_new_tokens": 1024,
        "chunk_length": 100,
        "repetition_penalty": 1.2,
        "temperature": 0.7,
        "need_asr": False,
        "streaming": False,
        "is_fixed_seed": 1,
        "is_norm": 0,
        "reference_audio": r_audio,
        "reference_text": r_text
    }

    # 发起TTS调用请求
    invoke_response = requests.post(invoke_url, headers={"Content-Type": "application/json"},
                                    data=json.dumps(invoke_data))
    if invoke_response.status_code != 200:
        print(f"TTS调用失败，状态码: {invoke_response.status_code}, {invoke_response.text}")
        return

    # 将返回结果保存为wav文件
    wav_data = invoke_response.content
    with open(save_path, "wb") as f:
        f.write(wav_data)
        print(f'wav保存成功，路径:{os.path.abspath(save_path)}')
    print(f'耗时：{time.time()-start_time}')


def call_1():
    # r_text = '生活并没有如你所愿，这个世界上没有那么多的刚刚好，努力不一定会有回报，但是努力的过程一定会让我们成为更优秀的自己。人生路上的每一步都算数，你付出的每一点都有意义。我们在世界上选择什么样的，成为什么样的人。人生丰富多彩，得靠自己成全。你此刻的付出，决定你未来会成为什么样的人。当你改变不了世界的时候，你可以改变自己。人的人生永远不会辜负你，那些转错的弯，那些走过的路，那些流下的眼泪，那些留下的伤痕，都会成为我们独一无二的自己。'
    # r_audio = '/code/sessions/20241122/b74a734c5a9a4d48a2c614c3e9a99d7e/asr_format.wav'

    r_text = '二零一三年蒋凡将其一手创办的友盟以八千万的美金卖给了阿里。之后又在当年以淘宝无线事业部资深总裁的身份加入了阿里。蒋凡在淘宝天猫的几年里面啊，与淘天的增长啊可以说是完美的重叠。他的三大代表作啊，第一个就牵手淘宝无线转型，推出了千人千面猜你喜欢，打造了淘宝内容的生态啊，推出了淘宝成功转型的互联网移动时代。美团的创始人王欣啊，在二零一九年的时候朋友圈发言。'
    r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241128/b59bbba07d6d44699f86301a2161f873/asr_format.wav'

    r_text = '生活并没有如你所愿，这个世界上没有那么多的刚刚好，努力不一定会有回报，但是努力的过程一定会让我们成为更优秀的自己。人生路上的每一步都算数，你付出的每一点都有意义。我们在世界上选择什么样的，成为什么样的人，人生丰富多彩，得靠自己成全，你此刻的付出，觉得你未来会成为什么样的人，当你改变不了世界的时候，你可以改变自己。人的人生永远不会辜负你，那些转错的弯，那些走过的路，那些流下的眼泪，那些留下的伤痕，都会成为我们独一无二的自己。人生就是一场自己与自己的较量。'
    r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241127/5fbc5158f6eb4b98a2a6cb2b88d8c238/asr_format.wav'

    # 排查卡顿问题
    # r_text = '咱们只需要对着手机说一二三就可以了。一二三一二三一二三四五六七一二三四五六七八九十一二三四五六七八九十，一二三三二一一二三四五六七一二三四五六七八九十一，二三四五六七八九十，一二三三二一一二三四五六七一二三四五六七八九十一，二三四五六七八九十。一二三四五六七八九十一二三四五六七八九十一二三三二一一二三四五六七一二三四五六七八九十。'
    # r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241205/029c2642d05348fb8ecb476860676416/asr_format.wav'

    # 排查卡顿问题2
    # r_text = "咱们只需要对着手机说一二三就可以了。一二三一二三一二三四五六七，一二三四五六七八九十，一二三四五六七八九十，一二三三二一，一二三四五六七，一二三四五六七八九十，一二三四五六七八九十，一二三三二一，一二三四五六七，一二三四五六七八九十，一二三四五六七八九十。一二三四五六七八九十，一二三四五六七八九十，一二三三二一，一二三四五六七，一二三四五六七八九十。"
    # r_audio = "http://192.168.6.131:9000/media/wav/t222.wav"

    text_13 = '你好，我是小助手，很高兴认识你。'
    text_113 = '结硬寨，打呆仗，曾国藩的这句话，你觉得和乔布斯的那句话说的是不是一个理儿啊。当然，刺激也不能时时、天天。但精神上保持着一种必要的饥渴，会让人每天都有盼头。如果不懂我在说什么，可以试试让自己饿几顿。你会发现自己从来没有如此的清醒、如此的渴盼着天亮和下一顿。这就是等待、希望。而人类全部的智慧，就在于这五个字：等待和希望。'
    text_363 = """来越长久，并且永远前进，不会因为任何时 是的'的改变而停止呢？在1991年之前，我父亲阿斯蒂芬一直在找这样的一个啊都是生意。直到有一次他去欧洲旅行，发现欧洲啊是哒大大小小的城市里都有很多罗马大浴池，他就问导游为什么这里会建这么多罗马大浴池，原来是撒的因为在十字军东征时期，战斗结束之后将领希望士兵快速恢复体力，但是士兵们太累了，不想吃也睡不好。后来将领们发现泡澡、沐浴可以让士兵们放松，也吃得下睡得着了，所以就大量建造了浴场，让士兵们休息好了之后再次上战场。果然，泡完澡的士兵个个都英勇无比，这个习惯也逐渐传承下来了。听完这个故事，我父亲突然发现，当代人的生活跟当时罗马士兵很像，压力太大，导致大家吃不好睡不好，所以我父亲决定，要把罗马大浴池搬进千家万户。这就是我们巨晴创立的初衷，让SPA给人健康、给人希望，让大家的生活重新生机勃勃。"""
    text_a = "人家都公布退市了，里面的资金肯定是削尖了脑袋往外逃命啊"
    text_a = "韩美日三国的高级外交官员也在首尔举行了第14次外交次官副部长级协商会议。韩国外交部第一次官金烘均、美国国务院副国务卿库尔特坎贝尔和日本外务省事务次官冈野正敬出席了此次会议。三方就朝鲜半岛及周边地区的安全形势进行了深入讨论"
    text_a = '当地时间4日凌晨4时27分左右，韩国总统尹锡悦宣布接受国会的要求，解除紧急戒严令。这距离他3日22时25分宣布实施“紧急戒严”仅6个多小时。关于此次戒严的理由，尹锡悦主要将矛头对准了在野党。\n\n 一段时间以来，韩国国内关于政治主张的分歧和争端愈演愈烈，牵动韩国社会的广泛关注。'
    text_a = """OK现在大家看到的我，
就是用软件生成出来的，
长相一样，
声音一样，
口型也一模一样，
我只需要给他发个文案，
他就能自动帮我做口播了。"""
    text = text_a
    tts(r_text, r_audio, text, save_path='output1145.wav')


def full_call():
    text = '你好，我是小助手，很高兴认识你。'
    _reference_audio_text, _asr_format_audio_url = train()
    print('准备调用tts')
    tts(_reference_audio_text, _asr_format_audio_url, text, save_path='output1122_wtt.wav')


if __name__ == '__main__':
    # train()
    # call_1()
    full_call()
