from django import forms

from .models import Post, Comment, User


class PostForm(forms.ModelForm):

    class Meta():
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)


class EditProfileForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)
