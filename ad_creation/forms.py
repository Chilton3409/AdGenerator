from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.tokens import default_token_generator

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email')
    
class CustomPasswordResetForm(PasswordResetForm):
    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt', email_template_name='registration/password_reset_email.html', use_https=False, token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None, extra_email_context=None):
        # Get the user
        user = self.get_user(self.cleaned_data["email"])
        # Check if the user has a TOTP device
        try:
            device = user.totpdevice_set.get()
        except TOTPDevice.DoesNotExist:
            device = None
        if device:
            # Generate a token and send a two-factor authentication code
            token = default_token_generator.make_token(user)
            device.generate_challenge()
            # Send the password reset email with a link to verify the 2FA code
            subject = "Password Reset Request"
            body = render_to_string('registration/password_reset_email_2fa.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
            })
            send_mail(subject, body, from_email, [user.email])
            return "Email sent with 2FA instructions"
        else:
            # If the user doesn't have 2FA set up, proceed with the normal password reset process
            return super().save(domain_override, subject_template_name, email_template_name, use_https, token_generator, from_email, request, html_email_template_name, extra_email_context)
