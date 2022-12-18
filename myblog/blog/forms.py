from django import forms
from .models import Comment, Post
from taggit.models import Tag


class EmailPostForm(forms.Form):
    name = forms.CharField(
        max_length=25,
        label='Name',
        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Your name..'}))
    email = forms.EmailField(
        label='From',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    to = forms.EmailField(
        label='To',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    comments = forms.CharField(
        required=False,
        label='',
        max_length=2000,
        widget=forms.Textarea(attrs={'placeholder': 'Additional message content..'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

    name = forms.CharField(
        label='Name',
        max_length=25,
        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Your name..'}))
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'mail@mail.com'}))
    body = forms.CharField(
        label='',
        max_length=2000,
        widget=forms.Textarea(attrs={'placeholder': 'comment content..'}))


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = self.get_dynamic_choice()

    class Meta:
        model = Post
        fields = ('title', 'body', 'tags')

    @staticmethod
    def get_dynamic_choice():
        TAGS = [(tag.name, tag.name) for tag in list(Tag.objects.all())]
        return TAGS

    title = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Title..'}))
    body = forms.CharField(
        label='',
        max_length=2000,
        widget=forms.Textarea(attrs={'placeholder': 'Content..'}))
    tags = forms.MultipleChoiceField(
        label='Tags',
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)

    name = forms.CharField(
        label='Tag name',
        max_length=30,
        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Book'}))


class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Django..'}))
