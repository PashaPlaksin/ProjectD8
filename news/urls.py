from django.urls import path
from django.conf.urls import url
from .views import NewsList, PostAuthor,PostView, PostSearch, PostCreateView, PostDeleteView, PostUpdateView ,  PostTag, PostType, subscribe_to_category, unsubscribe_from_category,ProfileView#, send_emails

# нужно добавлять кэширование напрямую в urls.py (в котором хранятся именно сами представления, а не основной urls.py из папки с settings.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page


app_name = 'news'
urlpatterns = [
    # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно, почему
    path('',NewsList.as_view(), name='news'),  # т. к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    path('<int:pk>', PostView.as_view()),
    path('post/<int:pk>', PostView.as_view(), name='post_view'),
    path('search/', PostSearch.as_view(), name='search'),
    path('search/<int:pk>', PostView.as_view()),

    path('add/', PostCreateView.as_view(), name='post_add'),  # Ссылка на создание товара

    path('<int:pk>/edit', PostUpdateView.as_view(), name='post_edit'),
    path('<int:pk>/delete', PostDeleteView.as_view(), name='post_delete'),
    # url(r'^post_author$', post_author),
    path('author/<int:pk>', cache_page(60*5)(PostAuthor.as_view()), name='author_name'),
    path('type/<str:name>', cache_page(60*5)(PostType.as_view()), name='post_type'),
    path('tag/<int:pk>',cache_page(60*5)(PostTag.as_view()), name='post_tag'),

    path('subscribe/<int:pk>', subscribe_to_category, name='sub_cat'),
    path('unsubscribe/<int:pk>', unsubscribe_from_category, name='unsub_cat'),
    path('profile/', ProfileView.as_view(), name='profile'),

]