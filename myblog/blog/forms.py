from django import forms
from .models import (
    Comment,
    Post,
)
from taggit.models import Tag


class EmailPostForm(forms.Form):
    """Share a post via email form."""
    name = forms.CharField(
        max_length=25,
        label='Name',
        widget=forms.TextInput(
            attrs={'type': 'search', 'placeholder': 'Your name..'}))
    email = forms.EmailField(
        label='From',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    to = forms.EmailField(
        label='To',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    comments = forms.CharField(
        required=False,
        max_length=2000,
        label='',
        widget=forms.Textarea(
            attrs={'placeholder': 'Additional message content..'}))


class CommentForm(forms.ModelForm):
    """Create a new comment form."""
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

    name = forms.CharField(
        max_length=25,
        label='Name',
        widget=forms.TextInput(
            attrs={'type': 'search', 'placeholder': 'Your name..'}))
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    body = forms.CharField(
        max_length=2000,
        label='',
        widget=forms.Textarea(attrs={'placeholder': 'comment content..'}))


class PostForm(forms.ModelForm):
    """Create a new post form."""
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = self.get_dynamic_choice()

    class Meta:
        model = Post
        fields = ('title', 'body', 'tags')

    @staticmethod
    def get_dynamic_choice():
        tag_choices = [(tag.name, tag.name) for tag in list(Tag.objects.all())]
        return tag_choices

    title = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(
            attrs={'type': 'search', 'placeholder': 'Title..'}))
    body = forms.CharField(
        max_length=2000,
        label='',
        widget=forms.Textarea(attrs={'placeholder': 'Content..'}))
    tags = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Tags',
        widget=forms.CheckboxSelectMultiple)


class TagForm(forms.ModelForm):
    """Create a new tag form."""
    class Meta:
        model = Tag
        fields = ('name',)

    name = forms.CharField(
        max_length=30,
        label='Tag name',
        widget=forms.TextInput(
            attrs={'type': 'search', 'placeholder': 'Book'}))


class SearchForm(forms.Form):
    """Search for posts form."""
    query = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={'type': 'search', 'placeholder': 'Django..'}))
