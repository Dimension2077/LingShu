from django.db import models


class MedicalKnowledge(models.Model):
    """医疗知识库"""
    disease = models.CharField(max_length=200, verbose_name='疾病名称')
    symptoms = models.TextField(verbose_name='典型症状', help_text='多个症状用逗号分隔')
    description = models.TextField(verbose_name='疾病描述', blank=True)
    treatment = models.TextField(verbose_name='治疗建议', blank=True)
    prevention = models.TextField(verbose_name='预防措施', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '医疗知识'
        verbose_name_plural = '医疗知识库'

    def __str__(self):
        return self.disease


class DiagnosisRecord(models.Model):
    """问诊记录"""
    session_id = models.CharField(max_length=100, verbose_name='会话ID')
    user_input = models.TextField(verbose_name='用户输入')
    ai_response = models.TextField(verbose_name='AI回答')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '问诊记录'
        verbose_name_plural = '问诊记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.session_id} - {self.created_at}"
