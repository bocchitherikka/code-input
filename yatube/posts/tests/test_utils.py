from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
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
