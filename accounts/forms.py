from django import forms
from django.core.validators import validate_email
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from .models import Profile


class LoginForm(forms.Form):
    email = forms.CharField(required=True, validators=[validate_email], widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))


class UserRegistrationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': ('The two password fields didn’t match.'),}
    
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    email = forms.CharField(required=True, validators=[validate_email], widget=forms.EmailInput(attrs={
        'class': 'form-control'}))

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',)
        return password2
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        try:
            validate_password(password, user=self.instance)
        except ValidationError as errors:
            raise ValidationError(errors)
        return password
        
    
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'password')
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'required': True}),
            'password': forms.PasswordInput(
                attrs={'class': 'form-control'})}
        

class UpdateUserForm(forms.ModelForm):
    
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'fprm-control'}),
            'last_name': forms.TextInput(attrs={'class': 'from-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
        

class UpdateProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('phone_number', 'address', 'postal_code', 'city', 'country')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'control-form'}),
            'country': forms.TextInput(attrs={'class': 'form-control'})
        }