import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(
    client, name, args
):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args')),
    )
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_availability_for_comment_edit_and_delete(
    name, args, parametrized_client, expected_status
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args')),
    ),
)
def test_redirect_for_anonymous_client(
    client, name, args
):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    assertRedirects(
        client.get(url), f'{login_url}?next={url}'
    )