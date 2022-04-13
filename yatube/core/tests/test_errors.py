from http import HTTPStatus

from django.test import TestCase


class ErrorsTest(TestCase):
    def test_custom_template_404(self):
        template = 'core/404.html'
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, template)
