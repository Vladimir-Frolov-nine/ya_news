import pytest

from django.conf import settings


@pytest.mark.django_db
def test_news_count(
    news_package, client, news_home_url
):
    response = client.get(news_home_url)
    assert len(
        response.context['object_list']
    ) == len(news_package) - 1


@pytest.mark.django_db
def test_new_order(
    client, news_package, news_home_url
):
    assert len(news_package) - 1 == settings.NEWS_COUNT_ON_HOME_PAGE
    response = client.get(news_home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(
    client, detail_url
):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(
    author_client, detail_url
):
    response = author_client.get(detail_url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_comments_order(
    client, news, detail_url, comments_package
):
    response = client.get(detail_url)
    assert 'news' in response.context
    news_instance = response.context['news']
    comment_date = [
        comment.created for comment in news_instance.comment_set.all()
    ]
    assert comment_date == sorted(comment_date, reverse=True)
