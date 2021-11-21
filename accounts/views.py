from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user
from django.contrib import messages
from django.conf import settings

from .forms import (LoginForm, UserRegistrationForm, 
                    UpdateUserForm, UpdateProfileForm)
from .models import Profile

CustomUser = get_user_model()


class LoginFormView(View):
    template_name = 'accounts/login.html',
        
    def get(self, request, *args, **kwargs):
        login_form = LoginForm()
        return render(request, self.template_name, {'form': login_form})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            return self.form_valid(login_form)
        return self.form_invalid(login_form)

    def form_invalid(self, login_form):
        return render(self.request, self.template_name, {'form': login_form})

    def form_valid(self, login_form):
        data = login_form.cleaned_data
        user_record = CustomUser.objects.get_user_by_email(email=data['email'])
        if user_record:
            user = authenticate(self.request, username=user_record, password=data['password'])
            if user:
                login(self.request, user)
                messages.success(self.request, 'You have logged in successfully')
                return redirect(settings.LOGIN_REDIRECT_URL)
        messages.error(self.request, 'Incorrect email / password')
        return render(self.request, self.template_name, {'form': login_form})


class UserRegistrationView(View):
    template_name = 'accounts/register.html'
    successful_template_name = 'accounts/register_done.html'

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            return self.form_valid(user_form)
        return self.form_invalid(user_form)

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        return render(request, self.template_name, {'user_form': user_form})

    def form_invalid(self, user_form):
        return render(self.request, self.template_name, {'user_form': user_form})

    def form_valid(self, user_form):
        data = user_form.cleaned_data

        email = data['email']
        password = data['password']
        password2 = data['password2']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, 'User with given email alredy exists')
            return render(self.request, self.template_name, {'user_form': user_form})
        
        # Create new user object
        new_user = CustomUser.objects.create_user(
            first_name=data['first_name'],
            last_name = data['last_name'],
            email=data['email'],
            username=email,
            password=password)
        Profile.objects.create(user=new_user)
        return render(self.request, self.successful_template_name, {'new_user': new_user})


class ProfileUpdateView(View):
    template_name = 'accounts/profile.html'
    
    
    def get(self, request, *args, **kwargs):
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
        return render(request, self.template_name, context={'user_form': user_form,
                                                            'profile_form': profile_form})
    
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        user = user_record = CustomUser.objects.get_user_by_email(email=email)
        if not user or user.id == request.user.id:
            user_form = UpdateUserForm(instance=request.user, data=request.POST)
            profile_form = UpdateProfileForm(instance=request.user.profile, data=request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                return self.form_valid(user_form, profile_form)
        return self.form_invalid()
                       
    def form_valid(self, user_form, profile_form):
        email = user_form.cleaned_data['email']
        user = user_form.save(commit=False)
        profile = profile_form.save(commit=False)
        user.username = email
        user.save()
        profile.user = user
        profile.save()
        
        messages.success(self.request, 'Profile was updated successfully') 
        return redirect('profile_url')
    
    def form_invalid(self):
        messages.error(self.request, 'User with given email alredy exists') 
        return redirect('profile_url')
        