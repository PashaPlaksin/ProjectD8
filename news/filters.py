from django_filters import FilterSet,  ModelChoiceFilter, DateFromToRangeFilter, NumberFilter,ModelMultipleChoiceFilter

from django_filters.widgets import RangeWidget


from .models import Category, Post
# создаём фильтр


class PostFilter(FilterSet):
    rating = NumberFilter(label='Rating', lookup_expr='gte')
    dateCreated = DateFromToRangeFilter(label='Date', lookup_expr=(
        'icontains'), widget=RangeWidget(attrs={'type': 'date'}))
    postCategory = ModelMultipleChoiceFilter(queryset=Category.objects.all(), label='Category')
    class Meta:
        model = Post
        fields = ['author', ]


class C(FilterSet):
    category = ModelChoiceFilter(queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = ['category']

