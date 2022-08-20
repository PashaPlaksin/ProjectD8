from django import template
import re
register = template.Library()  # если мы не зарегистрируем наши фильтры, то Django никогда не узнает, где именно их искать и фильтры потеряются


@register.filter(name='multiply')  # регистрируем наш фильтр под именем multiply, чтоб django понимал, что это именно фильтр, а не простая функция
def multiply(value, arg):  # первый аргумент здесь это то значение, к которому надо применить фильтр, второй аргумент — это аргумент фильтра, т. е. примерно следующее будет в шаблоне value|multiply:arg
    return str(value) * arg  # возвращаемое функцией значение — это то значение, которое подставится к нам в шаблон


@register.filter(name='multiply_str')  
def multiply_str(value, arg):
    if isinstance(value, str) and isinstance(arg, int):  # проверяем, что value — это точно строка, а arg — точно число, чтобы не возникло курьёзов
        return str(value) * arg
    else:
        raise ValueError(f'Нельзя умножить {type(value)} на {type(arg)}')  #  в случае, если кто-то неправильно воспользовался нашим тегом, выводим ошибку

@register.filter(name='censor')  
def censor(value):
    stopwords = []
    text = value
    words = re.sub(r'[^\w\s]','',value).lower().split()

    with open('static/txt/obscene.txt', 'r') as f:
      stopwords = f.read().replace(',', '').split()

    for word in words:
      if word in stopwords:
        text = re.sub(rf'\b{word}\b', '***', text, flags=re.IGNORECASE)

    return text