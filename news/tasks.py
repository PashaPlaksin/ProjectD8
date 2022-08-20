from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post
from datetime import  timedelta, date

#  файле tasks.py импортируем декоратор из библиотеки:
from celery import shared_task



def get_subscribers(category):
    user_emails = []
    for user in category.subscribers.all():
        user_emails.append(user.email)
    return user_emails

def send_emails(post_object, *args, **kwargs):

    # print(kwargs['template'])
    html = render_to_string(
        kwargs['template'],
        {'category_object': kwargs['category_object'], 'post_object': post_object}, # передаем в шаблон любые переменные
    )
    # print(f'category: {category}')
    msg = EmailMultiAlternatives(
            subject=kwargs['email_subject'],
            from_email='email@yandex.ru',
            to=kwargs['user_emails'] # отправляем всем из списка
        )
    msg.attach_alternative(html, 'text/html')
    msg.send()

@shared_task 
def new_post_subscription(instance):
    # latest_post = Post.objects.all().order_by('-dateCreated')[0]
    template = 'news/subcat/newpost.html'
    latest_post = instance

    if not latest_post.isUpdated:
        for category in latest_post.postCategory.all():
            email_subject = f'New post in category: "{category}"'
            user_emails = get_subscribers(category)
            send_emails(
              latest_post, 
              category_object=category,
              email_subject=email_subject, 
              template=template, 
              user_emails=user_emails)

@shared_task
def notify_subscribers_weekly():

    week = timedelta(days=7)
    posts = Post.objects.all()
    past_week_posts =[]
    template = 'news/subcat/weekly_digest.html'
    email_subject = 'Weekly digest for subscribed categories'

    for post in posts:
      time_delta = date.today() - post.dateCreated.date()
      if(time_delta < week):
        past_week_posts.append(post)
    # past_week_posts = posts.filter(dateCreated__range=[str(today), str(week)])


    past_week_categories = set()
    for post in past_week_posts:
        # past_week_categories.add(post.postCategory.all())

        for category in post.postCategory.all():
          past_week_categories.add(category)
          # print(post.postCategory.all().filter(catsub=category))
    
    # print(past_week_categories)

    user_emails = set()
    for category in past_week_categories:
        get_user_emails = (set(get_subscribers(category)))
        user_emails.update(get_user_emails)

    for user_email in user_emails:
      post_object = []
      category_set = set()

      for post in past_week_posts:
        subscription = post.postCategory.all().values('subscribers').filter(subscribers__email=user_email)

        if subscription.exists():
          # print(subscription)
          post_object.append(post)
          category_set.update(post.postCategory.filter(subscribers__email=user_email))
      print(user_email)
      # print(post_object)
      category_object = list(category_set)
      print(category_object)
          # print(set(post.postCategory.all()))

      send_emails(
        post_object, 
        category_object=category_object,
        email_subject=email_subject, 
        template=template, 
        user_emails=[user_email,])

