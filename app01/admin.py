from django.contrib import admin
from app01.models import MedicalKnowledge, DiagnosisRecord


@admin.register(MedicalKnowledge)
class MedicalKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['disease', 'symptoms', 'created_at']
    search_fields = ['disease', 'symptoms']
    list_per_page = 20


@admin.register(DiagnosisRecord)
class DiagnosisRecordAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_input', 'created_at']
    list_per_page = 30
    readonly_fields = ['session_id', 'user_input', 'ai_response', 'created_at']
