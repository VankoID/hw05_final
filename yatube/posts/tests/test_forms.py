import shutil
import tempfile

from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user_2 = User.objects.create_user(username='user_2')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост о создании поста',
            group=cls.test_group,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)

        self.author_client = Client()
        self.author_client.force_login(PostFormTests.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post_for_guest_client(self):
        """Тестирование создания поста гостем"""
        post_guest_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст_1',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f"{reverse('users:login')}?next=/create/"
        )
        self.assertEqual(Post.objects.count(), post_guest_count)

    def test_create_post_for_author_client(self):
        """Тестирование создания поста авторизованным пользователем"""
        post_count = Post.objects.all().count()
        form_data = {
            'text': 'Тестовый текст для автора поста',
            'group': PostFormTests.test_group.id,
            'image': self.uploaded
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': PostFormTests.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_post_id = Post.objects.latest('pub_date')
        self.assertEqual(last_post_id.group, self.test_group)
        self.assertEqual(last_post_id.text, form_data['text'])
        self.assertEqual(last_post_id.author, self.user)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.test_group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_for_authorized_client_without_group(self):
        """
        Тестирование создания поста авторизованным пользователем
        без выбора группы
        """
        form_data = {
            'text': 'Тестовый текст_2',
            'group': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user_2.username}))
        last_post_id = Post.objects.latest('pub_date')
        self.assertFalse(last_post_id.group, self.test_group)
        self.assertEqual(last_post_id.text, form_data['text'])
        self.assertEqual(last_post_id.author, self.user_2)

    def test_edit_post_for_author(self):
        """ Проверка редактирования поста"""
        form_data = {
            'text': 'Тестовый пост_3',
            'group': self.test_group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        post_edit_id = Post.objects.get(id=self.post.id)
        self.assertEqual(post_edit_id.group.id, form_data['group'])
        self.assertEqual(post_edit_id.text, form_data['text'])
        self.assertEqual(post_edit_id.author, self.user)
        self.assertEqual(post_edit_id.pub_date, self.post.pub_date)

    def test_edit_post_for_guest(self):
        """ Проверка редактирования поста для гостя"""
        form_data = {
            'text': 'При редактировании гостем этот пост должен отличаться',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f"{reverse(('users:login'))}?next="
            f"{reverse('posts:post_edit', kwargs={'post_id': self.post.id})}"
        )
        post_edit_guest = Post.objects.get(id=self.post.id)
        self.assertEqual(post_edit_guest.text, self.post.text)

    def test_edit_post_for_autorized_client_but_non_author(self):
        """ Проверка редактирования поста для авторизованного, но не автора"""
        form_data = {
            'text': 'Текст_4',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        post_edit_auth = Post.objects.get(id=self.post.id)
        self.assertEqual(post_edit_auth.text, self.post.text)

    def test_edit_post_for_author_with_group_editing(self):
        """ Проверка редактирования поста с изменением группы"""
        form_data = {
            'text': 'Тестовый пост_5',
            'group': self.test_group_2.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        change = Post.objects.get(id=self.post.id)
        self.assertEqual(change.group, self.test_group_2)
        self.assertEqual(change.text, form_data['text'])
        self.assertEqual(change.author, self.user)
        self.assertTrue(change.pub_date, self.post.pub_date)


class CommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый текст комментария',
            author=cls.user,
            post=cls.post
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_comment_created_authorized_user(self):
        """Тестирование создания комментария авторизованным пользователем"""
        comment_count = Comment.objects.all().count()
        form_data = {
            'text': 'Тестовый комментарий для авторизованного юзера',
        }
        response = self.auth_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.all().count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            author=self.user,
            post=self.post
        ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_for_non_auth_user(self):
        """Тестирование создания комментария не авторизованным пользователем"""
        form_data = {
            'text': 'Текст комментария_1',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f"{reverse('users:login')}?next="
            f"{reverse('posts:add_comment', kwargs={'post_id': self.post.id})}"
        )
