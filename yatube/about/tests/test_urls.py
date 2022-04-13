from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_URL_page_existance(self):
        """Статические страницы существуют для гостя"""
        template_names_exist = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }
        for address, status in template_names_exist.items():
            with self.subTest(address=address):
                response = self.guest.get(address)
                self.assertEqual(response.status_code, status)

    def test_URL_uses_correct_template(self):
        """Статические страницы используют соответствующий шаблон для гостя"""
        template_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in template_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest.get(reverse_name)
                self.assertTemplateUsed(response, template)
