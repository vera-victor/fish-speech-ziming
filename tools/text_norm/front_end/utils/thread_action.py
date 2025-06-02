from threading import Thread

from service.modules.log.log_helper import app_logger


class GraphemeProsodyThread(Thread):
    def __init__(self, prosody_predict, line, i):
        super().__init__()
        self.prosody_predict = prosody_predict
        self.line = line
        self.i = i
        self.result = None
        # self.start()  # 因为作为一个工具，线程必须永远“在线”，所以不如让它在创建完成后直接运行，省得我们手动再去start它
        # self.join()

    def run(self):
        app_logger.debug("韵律预测 [输入]： %s" % self.line)
        grapheme_list, prosody_list = self.prosody_predict.call(self.line)
        app_logger.debug("拼音预测 [输出] grapheme_list: {}".format(grapheme_list))
        app_logger.debug("韵律预测 [输出] prosody_list: {}".format(prosody_list))
        self.result = grapheme_list, prosody_list, self.i

    def get_result(self):
        return self.result
