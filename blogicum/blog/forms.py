from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    
    class Meta():
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows':3})
        }
    
    def clean(self):
        super().clean()
