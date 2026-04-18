from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model

from .models import Post, Comments


User = get_user_model()


class ChangeProfileForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'is_published']

        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 10})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text',]
