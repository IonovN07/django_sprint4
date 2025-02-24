from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta():
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 3})
        }

    def clean(self):
        super().clean()


class CommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)
