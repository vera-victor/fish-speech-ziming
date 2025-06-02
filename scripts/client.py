# -*- coding: gbk -*-
import os.path

import requests
import json
import time

# ��������ַ
# server_addr = "127.0.0.1:8080"
server_addr = '192.168.7.205:18180'

def train():
    global reference_audio_text, asr_format_audio_url
    # Ԥ�����ת�������URL������
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
    # ����Ԥ�����ת������
    print(f'����ѵ���� url:{preprocess_url}, data:{json.dumps(preprocess_data)}')
    preprocess_response = requests.post(preprocess_url, headers={"Content-Type": "application/json"},
                                        data=json.dumps(preprocess_data))
    print(f'ѵ�����ؽ����{preprocess_response.text}')
    # ������Ӧ�е�reference_audio_text��asr_format_audio_url
    preprocess_result = preprocess_response.json()
    code = preprocess_result.get("code")
    if code != 0:
        print(f'Ԥ����ʧ�ܣ������룺{code}')
        exit(1)
    print('>>>>>>ѵ���ɹ�����ʼ����tts')
    reference_audio_text = preprocess_result.get("reference_audio_text")
    asr_format_audio_url = preprocess_result.get("asr_format_audio_url")
    print(f"Reference Audio Text: {reference_audio_text}")
    print(f"ASR Format Audio URL: {asr_format_audio_url}")
    print(f'��ʱ��{time.time()-start_time}')
    return reference_audio_text, asr_format_audio_url


def tts(r_text, r_audio, text, save_path='/code/data/output.wav'):
    start_time = time.time()
    print(f'׼������tts�� r_text:{r_text}, r_audio:{r_audio}, text:{text}, save_path:{save_path}')
    # TTS���õ�URL������
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

    # ����TTS��������
    invoke_response = requests.post(invoke_url, headers={"Content-Type": "application/json"},
                                    data=json.dumps(invoke_data))
    if invoke_response.status_code != 200:
        print(f"TTS����ʧ�ܣ�״̬��: {invoke_response.status_code}, {invoke_response.text}")
        return

    # �����ؽ������Ϊwav�ļ�
    wav_data = invoke_response.content
    with open(save_path, "wb") as f:
        f.write(wav_data)
        print(f'wav����ɹ���·��:{os.path.abspath(save_path)}')
    print(f'��ʱ��{time.time()-start_time}')


def call_1():
    # r_text = '���û��������Ը�����������û����ô��ĸոպã�Ŭ����һ�����лر�������Ŭ���Ĺ���һ���������ǳ�Ϊ��������Լ�������·�ϵ�ÿһ�����������㸶����ÿһ�㶼�����塣������������ѡ��ʲô���ģ���Ϊʲô�����ˡ������ḻ��ʣ��ÿ��Լ���ȫ����˿̵ĸ�����������δ�����Ϊʲô�����ˡ�����ı䲻�������ʱ������Ըı��Լ����˵�������Զ���Ṽ���㣬��Щת����䣬��Щ�߹���·����Щ���µ����ᣬ��Щ���µ��˺ۣ������Ϊ���Ƕ�һ�޶����Լ���'
    # r_audio = '/code/sessions/20241122/b74a734c5a9a4d48a2c614c3e9a99d7e/asr_format.wav'

    r_text = '����һ���꽯������һ�ִ���������԰�ǧ������������˰��֮�����ڵ������Ա�������ҵ�������ܲõ���ݼ����˰���������Ա���è�ļ������氡�������������������˵���������ص����������������������һ����ǣ���Ա�����ת�ͣ��Ƴ���ǧ��ǧ�����ϲ�����������Ա����ݵ���̬�����Ƴ����Ա��ɹ�ת�͵Ļ������ƶ�ʱ�������ŵĴ�ʼ�����������ڶ���һ�����ʱ������Ȧ���ԡ�'
    r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241128/b59bbba07d6d44699f86301a2161f873/asr_format.wav'

    r_text = '���û��������Ը�����������û����ô��ĸոպã�Ŭ����һ�����лر�������Ŭ���Ĺ���һ���������ǳ�Ϊ��������Լ�������·�ϵ�ÿһ�����������㸶����ÿһ�㶼�����塣������������ѡ��ʲô���ģ���Ϊʲô�����ˣ������ḻ��ʣ��ÿ��Լ���ȫ����˿̵ĸ�����������δ�����Ϊʲô�����ˣ�����ı䲻�������ʱ������Ըı��Լ����˵�������Զ���Ṽ���㣬��Щת����䣬��Щ�߹���·����Щ���µ����ᣬ��Щ���µ��˺ۣ������Ϊ���Ƕ�һ�޶����Լ�����������һ���Լ����Լ��Ľ�����'
    r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241127/5fbc5158f6eb4b98a2a6cb2b88d8c238/asr_format.wav'

    # �Ų鿨������
    # r_text = '����ֻ��Ҫ�����ֻ�˵һ�����Ϳ����ˡ�һ����һ����һ������������һ�����������߰˾�ʮһ�����������߰˾�ʮ��һ��������һһ������������һ�����������߰˾�ʮһ�������������߰˾�ʮ��һ��������һһ������������һ�����������߰˾�ʮһ�������������߰˾�ʮ��һ�����������߰˾�ʮһ�����������߰˾�ʮһ��������һһ������������һ�����������߰˾�ʮ��'
    # r_audio = 'https://digital-public-dev.obs.myhuaweicloud.com/vcm_server/20241205/029c2642d05348fb8ecb476860676416/asr_format.wav'

    # �Ų鿨������2
    # r_text = "����ֻ��Ҫ�����ֻ�˵һ�����Ϳ����ˡ�һ����һ����һ�����������ߣ�һ�����������߰˾�ʮ��һ�����������߰˾�ʮ��һ��������һ��һ�����������ߣ�һ�����������߰˾�ʮ��һ�����������߰˾�ʮ��һ��������һ��һ�����������ߣ�һ�����������߰˾�ʮ��һ�����������߰˾�ʮ��һ�����������߰˾�ʮ��һ�����������߰˾�ʮ��һ��������һ��һ�����������ߣ�һ�����������߰˾�ʮ��"
    # r_audio = "http://192.168.6.131:9000/media/wav/t222.wav"

    text_13 = '��ã�����С���֣��ܸ�����ʶ�㡣'
    text_113 = '��Ӳկ������̣�����������仰������ú��ǲ�˹���Ǿ仰˵���ǲ���һ�����������Ȼ���̼�Ҳ����ʱʱ�����졣�������ϱ�����һ�ֱ�Ҫ�ļ��ʣ�������ÿ�춼����ͷ�������������˵ʲô�������������Լ������١���ᷢ���Լ�����û����˵����ѡ���˵Ŀ�������������һ�١�����ǵȴ���ϣ����������ȫ�����ǻۣ�������������֣��ȴ���ϣ����'
    text_363 = """��Խ���ã�������Զǰ����������Ϊ�κ�ʱ �ǵ�'�ĸı��ֹͣ�أ���1991��֮ǰ���Ҹ��װ�˹�ٷ�һֱ����������һ�����������⡣ֱ����һ����ȥŷ�����У�����ŷ�ް����մ��СС�ĳ����ﶼ�кܶ������ԡ�أ������ʵ���Ϊʲô����Ὠ��ô�������ԡ�أ�ԭ����������Ϊ��ʮ�־�����ʱ�ڣ�ս������֮����ϣ��ʿ�����ٻָ�����������ʿ����̫���ˣ������Ҳ˯���á����������Ƿ������衢��ԡ������ʿ���Ƿ��ɣ�Ҳ�Ե���˯�����ˣ����Ծʹ���������ԡ������ʿ������Ϣ����֮���ٴ���ս������Ȼ���������ʿ��������Ӣ���ޱȣ����ϰ��Ҳ�𽥴��������ˡ�����������£��Ҹ���ͻȻ���֣������˵��������ʱ����ʿ������ѹ��̫�󣬵��´�ҳԲ���˯���ã������Ҹ��׾�����Ҫ�������ԡ�ذ��ǧ���򻧡���������Ǿ��紴���ĳ��ԣ���SPA���˽���������ϣ�����ô�ҵ�������������������"""
    text_a = "�˼Ҷ����������ˣ�������ʽ�϶����������Դ�����������"
    text_a = "�����������ĸ߼��⽻��ԱҲ���׶������˵�14���⽻�ιٸ�������Э�̻��顣�����⽻����һ�ιٽ�������������Ժ�����������ؿ��������ձ�����ʡ����ιٸ�Ұ������ϯ�˴˴λ��顣�����ͳ��ʰ뵺���ܱߵ����İ�ȫ���ƽ�������������"
    text_a = '����ʱ��4���賿4ʱ27�����ң�������ͳ�������������ܹ����Ҫ�󣬽������������������3��22ʱ25������ʵʩ���������ϡ���6����Сʱ�����ڴ˴ν��ϵ����ɣ���������Ҫ��ìͷ��׼����Ұ����\n\n һ��ʱ���������������ڹ����������ŵķ���������������ң�ǣ���������Ĺ㷺��ע��'
    text_a = """OK���ڴ�ҿ������ң�
������������ɳ����ģ�
����һ����
����һ����
����Ҳһģһ����
��ֻ��Ҫ���������İ���
�������Զ��������ڲ��ˡ�"""
    text = text_a
    tts(r_text, r_audio, text, save_path='output1145.wav')


def full_call():
    text = '��ã�����С���֣��ܸ�����ʶ�㡣'
    _reference_audio_text, _asr_format_audio_url = train()
    print('׼������tts')
    tts(_reference_audio_text, _asr_format_audio_url, text, save_path='output1122_wtt.wav')


if __name__ == '__main__':
    # train()
    # call_1()
    full_call()
