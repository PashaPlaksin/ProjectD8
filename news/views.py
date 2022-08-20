from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.shortcuts import redirect
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.urls import resolve
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from django.utils.timezone import datetime
# импортируем недавно написанный фильтр
from .filters import C, PostFilter
from .forms import PostForm  # импортируем нашу форму
from .models import Post, Author, Category, CatSub
from django.http import HttpResponse


from django.core.cache import cache # импортируем наш кэш


class NewsList(ListView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-dateCreated')
    paginate_by = 10  # поставим постраничный вывод в один элемент
    # добавляем форм класс, чтобы получать доступ к форме через метод POST
    form_class = PostForm


    # (привет, полиморфизм, мы скучали!!!)
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        return context


class PostView(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs): # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}', None) # кэш очень похож на словарь, и метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.
 
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset) 
            # obj = super().get_object(queryset=kwargs['queryset']) 
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        
        return obj

# дженерик для получения деталей о товаре
class PostSearch(ListView):
    template_name = 'news/search.html'
    context_object_name = 'posts'
    queryset = Post.objects.all()

    # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса 
    # (привет, полиморфизм, мы скучали!!!)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        # context['categories'] = Category.objects.all()
        context['form'] = PostForm

        return context


def page_name(r):
    req = resolve(r.path_info).kwargs['name']
    # print(req)
    return req


class PostAuthor(ListView):
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        queryset = Post.objects.filter(author=Author.objects.get(id=self.id))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['name'] = Author.objects.get(authorUsername=User.objects.get(id=self.id))

        return context


class PostType(ListView):
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.name = resolve(self.request.path_info).kwargs['name']
        queryset = Post.objects.filter(categoryType=self.name)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['name'] = self.name

        return context


class PostTag(ListView):
    model = Post
    template_name = 'news/subcat/filtered.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        queryset = Post.objects.filter(postCategory=Category.objects.get(id=self.id))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        context['name'] = Category.objects.get(id=self.id)

        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'news/crud/post_create.html'
    form_class = PostForm
    success_url = '/news/'
    permission_required = ('news.add_post')
    error_message = 'You cannot post more than 3 posts a day'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = Author.objects.get(authorUsername=self.request.user)
        postAuthor = self.object.author
        posts = Post.objects.all()
        count_todays_posts = 0 
        for post in posts:
            if post.author == postAuthor:
                time_delta = datetime.now().date() - post.dateCreated.date()
                if time_delta.total_seconds() < 86400:
                    count_todays_posts +=1

        if count_todays_posts < 3:
            self.object.save()
        
            cat = Category.objects.get(pk=self.request.POST['postCategory'])
            self.object.postCategory.add(cat)

            validated = super().form_valid(form)

        else: 
            messages.error(self.request,  'You cannot post more than 3 posts a day.')
            validated = super().form_invalid(form)

        return validated

# дженерик для редактирования объекта
class PostUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'news/crud/post_create.html'
    form_class = PostForm
    success_url = '/news/'

    permission_required = ('news.change_post')

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        post = Post.objects.get(pk=id)
        post.isUpdated = True
        return post


# дженерик для удаления товара
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'news/crud/post_delete.html'
    success_url = '/news/'
    permission_required = ('news.delete_post')

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class ProfileView(ListView):
    model = CatSub
    template_name = 'news/profile.html'
    context_object_name = 'categories'


# Подписка пользователя в категорию новостей
@login_required
def subscribe_to_category(request, pk):
    user = request.user
    cat = Category.objects.get(id=pk)

    if not cat.subscribers.filter(id=user.id).exists():     
        cat.subscribers.add(user)
        html = render_to_string(
            'news/subcat/subsribed.html',
            {'categories': cat, 'user': user}, # передаем в шаблон какие захотим переменные, в данном случае я просто передал категорию для вывода ее в письме
        )  
        category = f'{cat}'
        email = user.email
        msg = EmailMultiAlternatives(
            subject=f'{category} category subscription',
            from_email='newsportal@yandex.ru',
            to=[email, ],
        ) 

        msg.attach_alternative(html, 'text/html')
        try:
            msg.send()
        except Exception as e:
            print(e)
        return redirect('/news/profile/')
        

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def unsubscribe_from_category(request, pk):
    user = request.user
    cat = Category.objects.get(id=pk)

    if cat.subscribers.filter(id=user.id).exists():     
        cat.subscribers.remove(user)        
    return redirect('/news/profile/')

