from django import forms

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='Текст')
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Группа'
    )

    class Meta:
        model = Post
        fields = ('text', 'image', 'group')


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='Текст')

    class Meta:
        model = Comment
        fields = ('text',)
