from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user)

    def test_urls_uses_correct_template_for_guests(self):
        """URL-адрес cуществует для гостя"""
        templates_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.post.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_create_for_redirect_guest_user(self):
        """Неавторизованный пользователь при обращении к странице
        create будет отправлен на авторизацию
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_for_redirect_guest_user(self):
        """Неавторизованный пользователь при обращении к странице
        post edit будет отправлен на авторизацию
        """
        response = self.guest_client.get(
            f'/posts/{self.post.pk}/edit/',
            follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/edit/')

    def test_urls_uses_correct_template_for_authorized_person(self):
        """URL-адрес использует соответствующий шаблон для авторизованного"""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{PostURLTests.post.group.slug}/',
            'posts/profile.html': f'/profile/{PostURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.pk}/',
            'posts/post_create.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_page_for_author(self):
        """Проверка редактирования поста автором"""
        response = self.author_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
