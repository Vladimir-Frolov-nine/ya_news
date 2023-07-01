# news/tests/test_content.py
from datetime import datetime, timedelta
# Допишите новый импорт.
from django.utils import timezone

# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
# Импортируем функцию reverse(),
# она понадобится для получения адреса страницы.
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


class TestHomePage(TestCase):
    HOME_URL = reverse('news:home')

#    @classmethod
#    def setUpTestData(cls):
#        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
#            News.objects.create(title=f'Новость {index}', text='Просто текст.')

# bulk_create(), для одновременного создания нескольких объектов.
#    @classmethod
#    def setUpTestData(cls):
#        all_news = []
#        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
#            news = News(title=f'Новость {index}', text='Просто текст.')
#            all_news.append(news)
#        News.objects.bulk_create(all_news)

# list comprehension/ тот же результат
#    @classmethod
#    def setUpTestData(cls):
#        all_news = [
#            News(title=f'Новость {index}', text='Просто текст.')
#            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE +1)
#        ]
#        News.objects.bulk_create(all_news)

# А можно написать выражение,
# создающее объекты новостей внутри bulk_create()
    @classmethod
    def setUpTestData(cls):
        today = datetime.today()
        News.objects.bulk_create(
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE +1)
        )

    def test_news_count(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = len(object_list)
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_new_order(self):
        response = self.client.get(self.HOME_URL)
        # Есть и другой ключ, он состоит из имени модели и окончания _list,
        # в примере с моделью News — response.context['news_list'];
        # под ним хранятся те же объекты, что и в object_list.
        object_list = response.context['news_list']
#        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_dates = [news.date for news in object_list]
        # Проверяем, что исходный список был отсортирован правильно.
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)

class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Тестовая новость', text='Текст, много слов.'
        )
        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        # Запоминаем текущее время:
#        now = datetime.now()
        # Получите текущее время при помощи утилиты timezone.
        now = timezone.now()
        # Создаём комментарии в цикле.
        for index in range(2):
            # Создаём объект и записываем его в переменную.
            comment = Comment.objects.create(
                author=cls.author, news=cls.news, text=f'Текст{index}',
            )
            # Сразу после создания меняем время создания комментария.
            comment.created = now + timedelta(days=index)
            # И сохраняем эти изменения.
            comment.save()

    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        # под ожидаемым именем - названием модели.
        self.assertIn('news', response.context)
        # Получаем объект новости.
        news = response.context['news']
        all_comments = news.comment_set.all()
        # Проверяем, что время создания первого комментария в списке
        # меньше, чем время создания второго.
        self.assertLess(all_comments[0].created, all_comments[1].created)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
