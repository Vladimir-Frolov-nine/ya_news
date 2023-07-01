import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.forms import WARNING, BAD_WORDS

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url
):
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    admin_client, form_data, news, new_text_comment, detail_url
):
    assertRedirects(
        admin_client.post(
            detail_url, data=form_data
        ), f'{detail_url}#comments'
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == new_text_comment
    assert comment.news == news


def test_user_cant_use_bad_words(
    author_client, detail_url
):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    assertFormError(
        author_client.post(
            detail_url, data=bad_words_data
        ), form='form', field='text', errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, detail_url, delete_comment_url
):
    assertRedirects(
        author_client.delete(delete_comment_url), detail_url + '#comments'
    )
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_comment_url
):
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client, form_data, comment, new_text_comment,
    comment_url, edit_comment_url
):
    assertRedirects(
        author_client.post(
            edit_comment_url, data=form_data
        ), comment_url + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == new_text_comment


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_data, text_comment, edit_comment_url
):
    response = admin_client.post(edit_comment_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == text_comment
