from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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

    def firstPostDict(
            self,
            response,
            post_with_group=None,
    ):
        if not post_with_group:
            first_post = response.context['page_obj'][0]
            first_post_dict = {
                first_post.text: self.post.text,
                first_post.author: self.post.author,
                first_post.id: self.post.id
            }
        else:
            first_post = response.context['page_obj'][0]
            first_post_dict = {
                first_post.text: post_with_group.text,
                first_post.author: post_with_group.author,
                first_post.id: post_with_group.id
            }
        return first_post_dict

    def firstPostDictForIsOnPage(self, response, post_with_group):
        posts_indexes = [0, 1]
        for posts_index in posts_indexes:
            first_post = response.context['page_obj'][posts_index]
            if first_post.group:
                first_post_dict = {
                    first_post.text: post_with_group.text,
                    first_post.author: post_with_group.author,
                    first_post.id: post_with_group.id
                }
        return first_post_dict

    def test_views_uses_correct_templates(self):
        """View-функции используют свои темплейты."""
        templates_views = {
            'posts/index.html': reverse('posts:main_page'),
            'posts/group_list.html': (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                )
            ),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': f'{self.user.username}'}
                )
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}
                )
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_views.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_view_sends_correct_context(self):
        """View-функция index передаёт верный context."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        for actual, expected in self.firstPostDict(response).items():
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_group_page_view_sends_correct_context(self):
        """
        View-функция group_posts передаёт верный context;
        Пост с указанной группой попадает на страницу группы.
        """
        post_with_group = Post.objects.create(
            author=self.user,
            text='Тестовый пост с группой',
            group=self.group
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response.context.get('group'), self.group)

        for actual, expected in self.firstPostDict(
                response, post_with_group
        ).items():
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_profile_page_view_sends_correct_context(self):
        """View-функция profile передаёт верный context."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        second_user = User.objects.create_user(username='second-user')
        Post.objects.create(
            author=second_user,
            text='Пост не от test-user'
        )
        self.assertEqual(
            response.context['author'],
            self.user,
            'В context передаётся неверный author.'
        )
        self.assertEqual(
            response.context['num_of_posts'],
            Post.objects.filter(author=self.user).count(),
            'В context передаётся неверное количество постов автора.'
        )

        for actual, expected in self.firstPostDict(response).items():
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_post_detail_page_view_sends_correct_context(self):
        """View-функция post_detail передаёт верный context."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.context['post'], self.post)

    def test_post_creating_page_view_sends_correct_context(self):
        """View-функция post_create передаёт верный context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_view_sends_correct_context(self):
        """View-функция post_edit передаёт верный context."""
        post_edit_data = {'text': "I hope it'll work"}
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=post_edit_data,
            follow=True
        )
        changed_post = response.context['post']
        self.assertEqual(changed_post.text, "I hope it'll work")

    def test_post_with_group_is_on_main_page(self):
        """Пост с указанной группой попадает на главную страницу."""
        post_with_group = Post.objects.create(
            author=self.user,
            text='Тестовый пост с группой',
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:main_page'))
        for actual, expected in self.firstPostDictForIsOnPage(
            response, post_with_group
        ).items():
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_post_with_group_is_on_profile_page(self):
        """Пост с указанной группой попадает в профиль автора."""
        post_with_group = Post.objects.create(
            author=self.user,
            text='Тестовый пост с группой',
            group=self.group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        for actual, expected in self.firstPostDictForIsOnPage(
            response, post_with_group
        ).items():
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_post_with_group_isnt_on_others_group_page(self):
        """Пост с указанной группой не попадает на страницу другой группы."""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост с группой',
            group=self.group
        )
        Post.objects.create(
            author=self.user,
            text='Тестовый пост с группой, но другой',
            group=self.group_not_like_the_old_one
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group_not_like_the_old_one.slug}'}
            )
        )
        count_of_posts_in_page_obj = len(response.context['page_obj'])
        expected_count_of_posts = Post.objects.filter(group=self.group).count()
        self.assertEqual(count_of_posts_in_page_obj, expected_count_of_posts)

    def test_image_in_context(self):
        """Изображение передается в посте в контексте."""
        temporary_image = SimpleUploadedFile(
            name='image',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/png'
        )
        post_with_image = Post.objects.create(
            author=self.user,
            text='С картинкой!',
            image=temporary_image,
            group=self.group
        )
        reverses = [
            reverse('posts:main_page'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_with_image.id}
            )
        ]
        for rev in reverses:
            response = self.authorized_client.get(rev)
            if rev != reverse(
                'posts:post_detail',
                kwargs={'post_id': post_with_image.id}
            ):
                post = response.context['page_obj'][0]
                image_is = post.image
            else:
                post = response.context['post']
                image_is = post.image
            self.assertTrue(image_is, f'Проблема в {rev}')

    def test_new_comment_in_post_details(self):
        """Комментарий попадает в секцию комментариев."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment, self.comment)

    def test_follow_is_working(self):
        """Авторизованный пользователь может подписаться."""
        new_user = User.objects.create_user(username='new-user')
        self.authorized_client.get(
            reverse(
                'posts:follow',
                kwargs={'username': new_user.username}
            )
        )
        follow = Follow.objects.get(
            user=self.user,
            author=new_user
        )
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, new_user)

    def test_unfollow_is_working(self):
        """Авторизованный пользователь может отписаться."""
        new_user = User.objects.create_user(username='new-user')
        self.authorized_client.get(
            reverse(
                'posts:follow',
                kwargs={'username': new_user.username}
            )
        )
        follow = Follow.objects.get(
            user=self.user,
            author=new_user
        )
        followings_count = Follow.objects.count()
        follow.delete()
        new_followings_count = Follow.objects.count()
        self.assertEqual(followings_count, new_followings_count+1)

    def test_posts_for_followers(self):
        """Подписчики видят в ленте посты автора."""
        new_user = User.objects.create_user(username='new-user')
        self.authorized_client.get(
            reverse(
                'posts:follow',
                kwargs={'username': new_user.username}
            )
        )
        new_users_post = Post.objects.create(
            text='Проверяем подписки',
            author=new_user
        )
        response = self.authorized_client.get(
            reverse('posts:followings')
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post, new_users_post)

    def test_posts_for_not_followers(self):
        """Не подписчики не видят в ленте посты автора."""
        new_user = User.objects.create_user(username='new-user')
        new_users_post = Post.objects.create(
            text='Проверяем подписки',
            author=new_user
        )
        response = self.authorized_client.get(
            reverse('posts:followings')
        )
        nothing = response.context['page_obj']
        self.assertNotEqual(nothing, new_users_post)
