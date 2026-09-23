from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import FAQ, ChatConversation, ChatMessage, SymptomChecker
import uuid
import json
import re

def get_or_create_conversation(request):
    """Get or create a chat conversation session"""
    session_id = request.session.get('chat_session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = session_id
        conversation = ChatConversation.objects.create(session_id=session_id)
    else:
        conversation, created = ChatConversation.objects.get_or_create(session_id=session_id)
    
    # If user is logged in, update with user info
    if request.user.is_authenticated and not conversation.user:
        conversation.user = request.user
        conversation.user_name = request.user.get_full_name() or request.user.username
        conversation.user_email = request.user.email
        conversation.save()
    
    return conversation

def find_best_faq(message):
    """Find the best matching FAQ for a user message"""
    message_lower = message.lower()
    faqs = FAQ.objects.filter(is_active=True)
    
    best_match = None
    best_score = 0
    
    for faq in faqs:
        score = 0
        # Check keywords
        if faq.keywords:
            keywords = [k.strip().lower() for k in faq.keywords.split(',')]
            for keyword in keywords:
                if keyword in message_lower:
                    score += 3
        
        # Check question
        if any(word in message_lower for word in faq.question.lower().split()):
            score += 2
        
        if score > best_score:
            best_score = score
            best_match = faq
        
        # Increment view count
        faq.view_count += 1
        faq.save()
    
    return best_match if best_score >= 2 else None

def get_greeting_response():
    """Return greeting message"""
    return "👋 Hello! I'm Shree Krishna's virtual assistant. How can I help you today?\n\nI can help you with:\n• Dental & Eye Care services\n• Appointment booking\n• Clinic timings & location\n• Treatment costs\n• Emergency care\n\nJust type your question!"

def get_fallback_response():
    """Return fallback response when no match found"""
    return "I'm not sure about that. Could you please rephrase your question?\n\nYou can also:\n• Call us at +977 9800000000\n• Book an appointment online\n• Visit our clinic\n\nHow else can I help you?"

def process_message(message, conversation):
    """Process user message and generate bot response"""
    message_lower = message.lower()
    
    # Greeting patterns
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'namaste']):
        return "Namaste! 🙏 Welcome to Shree Krishna Dental & Eye Care. How may I assist you today?"
    
    # Appointment related
    if any(word in message_lower for word in ['appointment', 'book', 'schedule']):
        return "📅 To book an appointment:\n\n1. Click on 'Book Appointment' in our menu\n2. Call us at +977 9800000000\n3. Visit our clinic\n\nWould you like me to help you book one right now?"
    
    # Timings
    if any(word in message_lower for word in ['timing', 'hour', 'open', 'close', 'time']):
        return "⏰ Our Clinic Hours:\n\nMonday-Friday: 9:00 AM - 8:00 PM\nSaturday-Sunday: 10:00 AM - 5:00 PM\n\nEmergency: 24/7 available"
    
    # Location
    if any(word in message_lower for word in ['location', 'address', 'where', 'clinic']):
        return "📍 Our Location:\nShree Krishna Dental & Eye Care\nKathmandu, Nepal\n\nGoogle Maps: [Click for directions]\n\nNeed help finding us?"
    
    # Emergency
    if any(word in message_lower for word in ['emergency', 'urgent', 'immediate', 'pain']):
        return "🚨 EMERGENCY SERVICE (24/7)\n\n📞 Call: +977 9800000000\n🏥 Visit our clinic immediately\n\nFor severe pain or accidents, please come to our clinic or call our emergency number right away!"
    
    # Pricing
    if any(word in message_lower for word in ['price', 'cost', 'fee', 'charge', 'payment']):
        return "💰 Our consultation fee starts from ₹500.\n\nFor specific treatments:\n• Dental Checkup: ₹500\n• Eye Checkup: ₹500\n• Root Canal: ₹2000 onwards\n• Cataract Surgery: ₹25,000 onwards\n\nWould you like a detailed price list?"
    
    # Find best FAQ match
    faq_match = find_best_faq(message)
    if faq_match:
        return faq_match.answer
    
    # Default response
    return get_fallback_response()

@csrf_exempt
def send_message(request):
    """Handle AJAX message sending"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Get or create conversation
            conversation = get_or_create_conversation(request)
            
            # Save user message
            ChatMessage.objects.create(
                conversation=conversation,
                sender='user',
                message=user_message
            )
            
            # Generate bot response
            bot_response = process_message(user_message, conversation)
            
            # Save bot response
            ChatMessage.objects.create(
                conversation=conversation,
                sender='bot',
                message=bot_response
            )
            
            return JsonResponse({
                'response': bot_response,
                'conversation_id': conversation.session_id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def chatbot_ui(request):
    """Render the chatbot interface"""
    conversation = get_or_create_conversation(request)
    
    # Get recent messages (last 20)
    messages = conversation.messages.all()[:20]
    
    context = {
        'messages': messages,
        'conversation_id': conversation.session_id,
    }
    return render(request, 'chatbot/chatbot_ui.html', context)

def get_bot_response(request):
    """Alternative endpoint for getting bot response"""
    if request.method == 'GET':
        message = request.GET.get('message', '')
        if message:
            response = process_message(message, get_or_create_conversation(request))
            return JsonResponse({'response': response})
    return JsonResponse({'response': get_fallback_response()})

def symptom_checker(request):
    """Display symptom checker interface"""
    return render(request, 'chatbot/symptom_checker.html')

@csrf_exempt
def check_symptoms(request):
    """Process symptom checking"""
    if request.method == 'POST':
        data = json.loads(request.body)
        symptoms = data.get('symptoms', '').lower()
        
        # Find matching symptoms
        matches = SymptomChecker.objects.filter(is_active=True)
        results = []
        
        for symptom in matches:
            if any(keyword.strip().lower() in symptoms for keyword in symptom.keywords.split(',')):
                results.append({
                    'symptom': symptom.symptom,
                    'possible_conditions': symptom.possible_conditions,
                    'recommendation': symptom.recommendation,
                    'urgency': symptom.urgency_level,
                })
        
        if results:
            return JsonResponse({'results': results})
        else:
            return JsonResponse({
                'results': [{
                    'symptom': 'No direct match found',
                    'possible_conditions': 'Please consult our doctor',
                    'recommendation': 'Schedule a consultation with our specialist',
                    'urgency': 'medium'
                }]
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def clear_session(request):
    """Clear chat session"""
    if 'chat_session_id' in request.session:
        del request.session['chat_session_id']
    return JsonResponse({'status': 'cleared'})