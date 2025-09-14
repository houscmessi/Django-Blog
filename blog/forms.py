
from django import forms
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    tags_text = forms.CharField(label="标签（逗号分隔）", required=False, help_text="例如：Django, 算法")
    class Meta:
        model = Post
        fields = ["title","body_md","status","tags_text"]

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username","password1","password2")
