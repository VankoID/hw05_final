from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse

from ..models import Post, User


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index_page(self):
        """Тест кеша главной страницы"""
        form_data = {
            'text': 'Текст поста для кеша'
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response_before_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.all().delete()
        response_after_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response_before_delete.content, response_after_delete.content
        )
        cache.clear()
        response_after_clear_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_before_delete.content, response_after_clear_cache.content
        )
