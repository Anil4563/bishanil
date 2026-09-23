from django.db import models
from django.utils import timezone

class FAQ(models.Model):
    """
    Frequently Asked Questions for the chatbot
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('dental', 'Dental Care'),
        ('eye', 'Eye Care'),
        ('appointment', 'Appointments'),
        ('payment', 'Payments'),
        ('insurance', 'Insurance'),
        ('emergency', 'Emergency'),
    ]
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma separated keywords for matching")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'view_count']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question[:100]


class ChatConversation(models.Model):
    """
    Stores chat conversations with users
    """
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=200, blank=True)
    user_email = models.EmailField(blank=True)
    user_phone = models.CharField(max_length=20, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.session_id} - {self.created_at}"


class ChatMessage(models.Model):
    """
    Individual messages in a chat conversation
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('admin', 'Admin'),
    ]
    
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"


class SymptomChecker(models.Model):
    """
    Symptoms and possible conditions for symptom checker
    """
    symptom = models.CharField(max_length=200)
    possible_conditions = models.TextField()
    recommendation = models.TextField()
    urgency_level = models.CharField(max_length=50, choices=[
        ('low', 'Low - Can wait for regular appointment'),
        ('medium', 'Medium - Schedule within a week'),
        ('high', 'High - See doctor within 24-48 hours'),
        ('emergency', 'Emergency - Seek immediate care'),
    ], default='low')
    keywords = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.symptom