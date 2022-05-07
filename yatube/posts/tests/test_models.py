from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
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

    def test_models_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        model_titles = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title
        }
        for title, expected in model_titles.items():
            with self.subTest(expected=expected):
                self.assertEqual(title, expected)

    def test_models_have_correct_verbose_name(self):
        """Проверяем, что у моделей корректные verbose_name."""
        post_verbose_name = self.post._meta.get_field('text').verbose_name
        group_verbose_name = self.group._meta.get_field('title').verbose_name
        verbose_names = {
            post_verbose_name: 'Текст поста',
            group_verbose_name: 'Название группы'
        }
        for verbose_name, expected in verbose_names.items():
            with self.subTest(expected=expected):
                self.assertEqual(verbose_name, expected)

    def test_models_have_correct_help_texts(self):
        """Проверяем, что у моделей корректные help_text."""
        post_help_text = self.post._meta.get_field('text').help_text
        group_help_text = self.group._meta.get_field('title').help_text
        help_texts = {
            post_help_text: 'Введите текст поста',
            group_help_text: 'Дайте название группе'
        }
        for help_text, expected in help_texts.items():
            with self.subTest(expected=expected):
                self.assertEqual(help_text, expected)
