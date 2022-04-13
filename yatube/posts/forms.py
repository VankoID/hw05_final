from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
    #   help_texts = {
    #       'text': 'Поле для ввода текста поста',
    #       'group': 'Выберите соответствующую группу',
    #   }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
