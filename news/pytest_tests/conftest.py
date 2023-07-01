# conftest.py ya_news
import pytest

from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def text_comment():
    return 'Текст комментария.'


@pytest.fixture
def comment(author, news, text_comment):
    comment = Comment.objects.create(
        news=news,
        text=text_comment,
        author=author,
    )
    return comment


@pytest.fixture
def comment_pk_for_args(comment):
    return comment.pk,


@pytest.fixture
def news_pk_for_args(news):
    return news.pk,


@pytest.fixture
def news_package():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_package(news, admin_user):
    now = timezone.now()
    comments = []
    for index in range(2):
        comment = Comment(
            author=admin_user,
            news=news,
            text=f'Текст{index}',
        )
        comment.created = now - timedelta(days=index)
        comments.append(comment)
        return Comment.objects.bulk_create(comments)


@pytest.fixture
def new_text_comment():
    return 'Текст обновленного комментария.'


@pytest.fixture
def form_data(new_text_comment):
    return {
        'text': new_text_comment
    }


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def comment_url(comment):
    return reverse('news:detail', args=(comment.pk,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def news_home_url(comment):
    return reverse('news:home')
