from libs.yuntongxun.sms import CCP
from celery_tasks.main import app
import logging
logger = logging.getLogger('django')
@app.task(name='send_sms_code',bind=True,default_retry_delay=10)
def send_sms_code(self,mobile,sms_code,):
    try:
        result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
        if result != 0:
            logger.error('发送失败,%s'%result)
            raise Exception('发送失败')
    except Exception as e:
        self.retry(exc=e,max_retries=3)