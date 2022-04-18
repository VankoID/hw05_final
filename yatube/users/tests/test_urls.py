from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(UserURLTests.user)

    def test_urls_uses_correct_template_for_guests(self):
        """Проверка авторизации URL-адресов для гостя"""
        templates_url_names = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_logout_for_auth_person(self):
        """Проверка выхода для авторизованного пользователя"""
        response = self.auth_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_URL_uses_correct_template_for_authorization(self):
        """Cтраницы авторизации используют соответствующий шаблон для гостя"""
        template_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'
            )
        }
        for template, reverse_name in template_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_URL_uses_correct_template_for_logout(self):
        """Cтраницы выхода используют соответствующий шаблон"""
        template = 'users/logout_out.html'
        response = self.auth_client.get(reverse('users:logout'))
        self.assertTemplateUsed(response, template)
