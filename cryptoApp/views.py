
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import CustomUserCreationForm
from .models import Message
from .crypto_utils import generate_key, encrypt_message, decrypt_message
from .twilio_utils import send_sms  
import random
import string
import os
import logging
from django.http import HttpResponseRedirect


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'messages/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('send_message')
    else:
        form = AuthenticationForm()
    return render(request, 'messages/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def send_message(request):
    if request.method == 'POST':
        message_text = request.POST['message']
        phone_number = request.POST['phone_number']

        otp = ''.join(random.choices(string.digits, k=6))

        salt = os.urandom(16)
        otp1 = os.urandom(32)
        key = generate_key(otp, salt)
        nonce, encrypted_message = encrypt_message(message_text, otp1)

        message = Message.objects.create(
            user=request.user,
            encrypted_message=encrypted_message,
            nonce=nonce,
            salt=salt,
            otp=otp1,
            recipient_phone_number=phone_number,
        )

        otp2 = otp1.hex()
        sms_message = f"Key: {otp2}"
        send_sms(phone_number, sms_message)

        return render(request, 'messages/message_with_home_button.html', {'message': "Message sent successfully!"})
    return render(request, 'messages/send_message.html')

@login_required
def receive_message(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')

        try:
            otp1 = bytes.fromhex(otp)
            message_record = Message.objects.get(otp=otp1)
            salt = bytes(message_record.salt)
            decrypted_message = decrypt_message(
                message_record.encrypted_message,
                otp1,
                message_record.nonce
            )

            # sms_message = f"Decrypted Message: {decrypted_message}\nOTP: {otp}\nMessage ID: {message_record.id}"
            # send_sms(message_record.recipient_phone_number, sms_message)

            return render(request, 'messages/message_with_home_button.html', {
                'message': f"Decrypted message sent successfully! Message: {decrypted_message}",
                'decrypted_message': decrypted_message,
            })
        except Message.DoesNotExist:
            return render(request, 'messages/message_with_home_button.html', {
                'message': "Message not found or you do not have permission to view it."
            })
        except Exception as e:
            return render(request, 'messages/message_with_home_button.html', {
                'message': f"Failed to decrypt message: {e}"
            })
    else:
        return render(request, 'messages/receive_message.html')

def index(request):
    return render(request, 'messages/Home.html')

def Home(request):
    return render(request, 'messages/Home.html')

def contact(request):
    return render(request, 'messages/contact.html')

def about(request):
    return render(request, 'messages/about.html')

def service(request):
    return render(request, 'messages/service.html')
