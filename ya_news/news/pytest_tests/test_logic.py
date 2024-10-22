from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENTS = '#comments'


def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        news, author, author_client,
        form_data, detail_url,
):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}{COMMENTS}')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        errors=WARNING,
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, detail_url, delete_url,
):
    news_url = detail_url
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{news_url}{COMMENTS}')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(admin_client, delete_url):
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        comment, author_client, edit_url, detail_url, new_form_data,
):
    news_url = detail_url
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, f'{news_url}{COMMENTS}')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        comment, admin_client, edit_url, new_form_data,
):
    response = admin_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
