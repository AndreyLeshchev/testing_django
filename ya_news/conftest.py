from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
    )


@pytest.fixture
def news_list():
    today = datetime.today()
    news = News.objects.bulk_create(
        News(
            title=f'Новость {index}', text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news


@pytest.fixture
def comment_list(news, author):
    comments = []
    today = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = today - timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}


@pytest.fixture
def new_form_data():
    return {'text': NEW_COMMENT_TEXT}


@pytest.fixture
def id_comment_for_args(comment):
    return comment.id,


@pytest.fixture
def id_news_for_args(news):
    return news.id,


@pytest.fixture
def detail_url(id_news_for_args):
    return reverse('news:detail', args=id_news_for_args)


@pytest.fixture
def delete_url(id_comment_for_args):
    return reverse('news:delete', args=id_comment_for_args)


@pytest.fixture
def edit_url(id_comment_for_args):
    return reverse('news:edit', args=id_comment_for_args)
