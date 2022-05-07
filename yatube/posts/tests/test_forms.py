import shutil
import tempfile

from ..forms import PostForm
from ..models import Group, Post, User

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from http import HTTPStatus

TEMP_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_ROOT)
class PostFormTests(TestCase):
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
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаёт пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        created_post = Post.objects.order_by('-pub_date').first()
        self.assertRedirects(response, '/profile/test-user/')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма со страницы редактирования изменяет пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Появился новый пост'
        )
        changed_post = response.context['post']
        changed_text = changed_post.text
        changed_post_author = changed_post.author
        changed_post_group = changed_post.group
        self.assertEqual(changed_text, form_data['text'])
        self.assertEqual(changed_post_author, self.user)
        self.assertEqual(changed_post_group, self.group)
