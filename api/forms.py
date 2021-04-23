from django import forms
from .models import Post
from django.core.exceptions import ValidationError

# form for the creation of a new post
class PostModelForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['content']
        widgets ={"content": forms.Textarea(attrs={"rows": "5"})}
        labels = {"content": "Message"}

    # validation method to avoid posts that contain the word "hack"
    def clean_content(self):
        data = self.cleaned_data.get("content")
        if "hack" in data:
            raise ValidationError("Your content is violating our rules!")
        return data