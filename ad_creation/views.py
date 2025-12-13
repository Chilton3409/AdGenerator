# views.py
from django.http import HttpResponse
from .services import AdvertisingAssistantService
from .models import Advertisement
import logging
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm, SetPasswordForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from djstripe import models
from django.urls import reverse_lazy
from django_otp.decorators import otp_required
from two_factor.views import OTPRequiredMixin
from two_factor.views import SetupView
from .forms import RegisterForm
from two_factor.views import OTPRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from .forms import CustomPasswordResetForm
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from djstripe.models import Session
from djstripe.models import WebhookEndpoint
from djstripe.models import WebhookEventTrigger
import stripe
from stripe import Product
from dotenv import load_dotenv
load_dotenv()
import os
from django.http import JsonResponse
import json
from django.http import JsonResponse

def home(request):
    return render(request, 'ad_creation/home.html')

def register_view(request):
    try:

        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('home')
        else:
            form = RegisterForm()
        return render(request, 'ad_creation/register.html', {'form': form})
    except Exception as e:
        logging.exception(msg=e)
        return render(request, 'ad_creation/error.html', {'error': e})

def register_and_setup_2fa(request):
    if request.method == 'POST':

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('two_factor:setup')
    else:
        form = RegisterForm()
    return render(request, 'ad_creation/register.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    # These attributes are read by the base PasswordResetView logic.
    # The email backend settings are picked up automatically from settings.py

    # Optional: Customize the email template used for the body
    # email_template_name = 'ad_creation/password_reset_email.html'

    # Optional: Customize the subject line (must be a string or function)
    # subject_template_name = 'ad_creation/password_reset_subject.txt'

    # Optional: Set the from email address explicitly if needed, otherwise it uses settings.DEFAULT_FROM_EMAIL
    # from_email = settings.DEFAULT_FROM_EMAIL

    success_url = reverse_lazy('ad_creation/password_reset_done')
    
    
# After verifying the user's identity, you can allow them to reset their password
@otp_required
@login_required
def reset_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('password_reset_complete')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'ad_creation/reset_password.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'ad_creation/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'ad_creation/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'ad_creation/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'ad_creation/password_reset_complete.html'

def login_view(request):
    try:

        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
        else:
            form = LoginForm()
        return render(request, 'two_factor/core/login.html', {'form': form})
    except Exception as e:
        logging.exception(msg=e)
        return render(request, 'ad_creation/error.html', {'error': e})


def logout_view(request):
    try:

        logout(request)
        return redirect('home')
    except Exception as e:
        logging.exception(msg=e)
        return render(request, 'ad_creation/error.html', {'error': e})

@login_required
def create_checkout_session(request):
    try:
        # Fetch the Price object from dj-stripe models or Stripe API
        # You can use a lookup_key instead of the price ID
        # Here, we assume the price ID corresponds to an object in dj-stripe
        secret_key = os.environ.get('SECRET_KEY')
        stripe.api_key = secret_key



        # Use the standard Stripe API to create the Checkout Session

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1SNJgX3Pqaw5Vwb5zovI1Av9',
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://gallbegalled.pythonanywhere.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://gallbegalled.pythonanywhere.com/cancel?session_id={CHECKOUT_SESSION_ID}'
        )
        return redirect(session.url)
    except Exception as e:
        logging.exception(msg=e)

        return render(request, 'ad_creation/error.html', {'error': e})
    except Exception as e:
        logging.exception("Failed to create Stripe Checkout session: %s", e)
        return render(request, 'ad_creation/error.html', {'error': e})


def success_view(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return render(request, 'ad_creation/error.html', {'error': 'Missing session ID'})
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription_id = session.subscription
        customer_id = session.customer
        request.user.stripe_customer_id = customer_id
        request.user.stripe_subscription_id = subscription_id
        request.user.subscription_status = 'active'
        request.user.save()
        return render(request, 'ad_creation/success.html')
    except Exception as e:
        return render(request, 'ad_creation/error.html', {'error': str(e)})
def cancel_view(request):

    try:

        return render(request, 'ad_creation/cancel.html')
    except Exception as e:
        return render(request, 'ad_creation/error.html', {'error': str(e)})
@login_required
def cancel_subscription(request):
    try:
        # Ensure your Stripe secret key is set correctly from environment variables
        stripe.api_key = os.environ.get('SECRET_KEY') # Make sure this environment variable name is correct

        subscription_id = request.user.stripe_subscription_id
        
        if not subscription_id:
            message = "You do not have an active subscription to cancel."
            return render(request, 'ad_creation/cancel_subscription.html', {'message': message})

        # --- Stripe API Call ---
        # Cancels the subscription immediately and stops all future billing.
        # The 'deleted' object returned by Stripe confirms the cancellation.
        deleted_subscription = stripe.Subscription.delete(subscription_id)

        # --- Local Database Update ---
        # Update your local User model fields to reflect the cancellation
        request.user.subscription_status = 'cancelled'
        # Optional: Clear the subscription ID since it is no longer valid
        request.user.stripe_subscription_id = None 
        request.user.save()

        message = f"Your subscription ({subscription_id}) has been immediately cancelled."
        return render(request, 'ad_creation/cancel_subscription.html', {'message': message})

    except stripe.error.StripeError as e:
        # Handle specific Stripe API errors (e.g., subscription not found)
        logging.exception("Stripe API Error during subscription cancellation: %s", e)
        return render(request, 'ad_creation/error.html', {'error': str(e)})
        
    except Exception as e:
        # Handle general errors
        logging.exception("An unexpected error occurred during cancellation: %s", e)
        return render(request, 'ad_creation/error.html', {'error': str(e)})

@login_required
def generate_advertisement(request):
    # Ensure SECRET_KEY is accessed correctly (best practice is settings.STRIPE_SECRET_KEY)
    stripe.api_key = os.environ.get('SECRET_KEY')

    if request.user.subscription_status != 'active':
        # Redirect to subscription page if not active
        return redirect('subscribe')

    if request.method == 'POST':

        # Check if the request is a JSON request (from our fetch code)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            filename = data.get('filename', '')
            return JsonResponse({
        'status': 'success',
        'message': 'Advertisement generation initiated successfully.',
        'filename': filename
    })


        else:

            prompt = request.POST.get('prompt')
        # We can also get the filename if you want to use it in the view:
            filename = request.POST.get('filename')

            service = AdvertisingAssistantService()
            advertisement_content = service.generate_advertisement(prompt)

            try:
                # Note: This still requires your 'Advertisement' model to have the 'user' field (see previous fix).
                advertisement = Advertisement.objects.create(
                    content=advertisement_content,
                    prompt=prompt,
                    created_by=request.user,
                    filename = filename
                )
                # Render the template with the result
                return render(request, 'ad_creation/create_ad.html', {'advertisement': advertisement})
            except Exception as e:
                logging.exception(msg=e)
                return render(request, 'ad_creation/error.html', {'error': str(e)})
    else:
        # For GET requests, just render the blank form
        return render(request, 'ad_creation/create_ad.html')

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Advertisement
    fields = ['prompt']
    template_name = 'ad_creation/create_ad.html'

    def get_queryset(self):
        return Advertisement.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        try:

            advertisement = form.save(commit=False)
            service = AdvertisingAssistantService()
            advertisement.content = service.generate_advertisement(advertisement.prompt)
            advertisement.save()
            return redirect('ad_detail', pk=advertisement.pk)

        except Exception as e:
            logging.exception(msg=e)
            return render(self.request, 'ad_creation/error.html', {'error': e})
class AdListView(LoginRequiredMixin,ListView):
    model = Advertisement
    template_name = 'ad_creation/ad_list.html'
    def get_queryset(self):
        return Advertisement.objects.filter(created_by=self.request.user).order_by('-created_at')


class AdDetailView(LoginRequiredMixin,DetailView):
    model = Advertisement
    template_name = 'ad_creation/ad_detail.html'

    def get_queryset(self):
        try:

            return Advertisement.objects.filter(created_by=self.request.user)
        except Exception as e:
            logging.exception(msg=e)
            return render(self.request, 'ad_creation/error.html', {'error': e})
class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Advertisement
    success_url = reverse_lazy('dashboard')
    def get_queryset(self):
        try:

            return Advertisement.objects.filter(created_by=self.request.user)
        except Exception as e:
            logging.exception(msg=e)
            return []
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'ad_creation/dashboard.html'
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        try:

            context['advertisements'] = Advertisement.objects.filter(created_by=self.request.user)
            return context
        except Exception as e:
            logging.exception(msg=e)
            logging.error(f"Error fetching advertisements: {e}")
            context['advertisements'] = []
            return context
