from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from blog.models import Post, Comments
from blog.forms import CommentForm, PostForm


class IsAuthorMixin:
    """Редактирование и удаление только для автора"""

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    """Миксин для постов"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class IsCommentAuthorMixin:
    """Проверка, что коммент редактирует именно автор"""

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comments, pk=kwargs['comment_id'])
        if (int(kwargs['post_id']) != instance.post_id
                or instance.author != request.user):
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    """Миксин для комментариев"""

    model = Comments
    form_class = CommentForm
    template_name = 'blog/comment.html'
    context_object_name = 'comment'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})
