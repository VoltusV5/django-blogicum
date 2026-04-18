from datetime import datetime

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count

from blog.models import Category, Post, Comments
from blog.forms import ChangeProfileForm, PostForm, CommentForm

User = get_user_model()

PAGINATOR_ELEMENTS_IN_PAGE = 10


def get_paginated_page(request, queryset, in_page=PAGINATOR_ELEMENTS_IN_PAGE):
    """
    Функция пагинации.
    Получает request
    Данные и кол-во элементов на странице
    """
    paginator = Paginator(queryset, in_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_published_posts():
    """Возвращает опубликованные посты"""
    datetime_now = datetime.now()

    post_list = (
        Post.objects.filter(
            pub_date__lt=datetime_now, is_published=True,
            category__is_published=True)
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )

    return post_list


def index(request):
    """Главная страница проекта"""
    template_name = 'blog/index.html'

    page_obj = get_paginated_page(
        request, get_published_posts(),
        PAGINATOR_ELEMENTS_IN_PAGE
    )

    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    """Страница отдельной публикации"""
    template_name = 'blog/detail.html'

    base = Post.objects.annotate(comment_count=Count('comments'))

    if request.user.is_authenticated:
        post = base.filter(pk=post_id, author=request.user).first()
        if post is not None:
            form = CommentForm()
            comments = post.comments.all()
            return render(
                request,
                template_name,
                {'post': post, 'form': form, 'comments': comments},
            )

    post = get_object_or_404(
        get_published_posts(), pk=post_id,
    )

    form = CommentForm()
    comments = post.comments.all()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, template_name, context)


def category_posts(request, category_slug):
    """Страница категории"""
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)

    page_obj = get_paginated_page(
        request,
        get_published_posts().filter(category=category),
        PAGINATOR_ELEMENTS_IN_PAGE
    )

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def profile(request, username):
    """Профиль пользователя"""
    template_name = 'blog/profile.html'

    user_profile = get_object_or_404(User, username=username)

    # Если автор своего поста
    if request.user == user_profile:
        posts = (
            Post.objects
            .filter(author=user_profile)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
    else:
        posts = get_published_posts().filter(author__username=username)

    page_obj = get_paginated_page(request, posts, PAGINATOR_ELEMENTS_IN_PAGE)

    context = {
        'profile': user_profile,
        'page_obj': page_obj,
    }

    return render(request, template_name, context)


@login_required
def edit_profile(request):
    """Изменение профиля пользователя"""
    template_name = 'blog/user.html'

    if request.method == 'POST':
        form = ChangeProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ChangeProfileForm(instance=request.user)

    context = {
        'form': form,
    }

    return render(request, template_name, context)


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
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Создание поста"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, IsAuthorMixin, PostMixin, UpdateView):
    """Редактирование поста"""

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.pk}
        )


class PostDeleteView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """Удаление постов"""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


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
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """Создание комментов"""

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(
        LoginRequiredMixin, IsCommentAuthorMixin, CommentMixin, UpdateView):
    """Редактирование комментов"""


class CommentDeleteView(
        LoginRequiredMixin, IsCommentAuthorMixin, DeleteView):
    """Удаление комментов"""

    model = Comments
    template_name = 'blog/comment.html'
    context_object_name = 'comment'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
