from django.contrib import admin
from .models import FAQ, ChatConversation, ChatMessage, SymptomChecker

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['sender', 'message', 'created_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'view_count', 'helpful_count', 'order']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer', 'keywords']
    list_editable = ['is_active', 'order']

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'user_name', 'user_email', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['session_id', 'user_name', 'user_email']
    list_editable = ['is_resolved']
    inlines = [ChatMessageInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'message_preview', 'created_at']
    list_filter = ['sender', 'is_read', 'created_at']
    search_fields = ['message']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(SymptomChecker)
class SymptomCheckerAdmin(admin.ModelAdmin):
    list_display = ['symptom', 'urgency_level', 'is_active']
    list_filter = ['urgency_level', 'is_active']
    search_fields = ['symptom', 'possible_conditions', 'recommendation', 'keywords']
    list_editable = ['is_active']