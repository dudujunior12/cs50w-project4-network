from django import forms

class CreatePost(forms.Form):
    post_text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Post', 'class': 'form-control', 'rows': '5'}), label='')