from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Comment, Group, Post

User = get_user_model()


class ProjectUtilsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_not_like_the_old_one = Group.objects.create(
            title='Тестовая группа, но не как старая',
            slug='slug-not-like-the-old-one',
            description='Описание реально имеет значение?'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст тестовый',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_main_page_cache(self):
        post_for_this_test = Post.objects.create(
            text='Ну текст как текст..',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:main_page'))
        response_content_first = response.content
        post_for_this_test.delete()
        response = self.authorized_client.get(reverse('posts:main_page'))
        response_content_second = response.content
        self.assertEqual(response_content_first, response_content_second)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:main_page'))
        response_content_third = response.content
        self.assertNotEqual(response_content_third, response_content_first)
