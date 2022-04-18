from django.test import TestCase
from django.conf import settings

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста, который явно больше 15-ти символов'
        )

    def test_model_have_correct_object_names_post(self):
        """Проверяем, что у модели POST корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:settings.SYMBOL_LIMIT]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """Проверяем, что verbose_name совпадают с ожидаемыми"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """Проверяем, что help_text совпадает с ожидаемыми"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Поле для ввода текста поста',
            'group': 'Выберите соответствующую группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_have_correct_object_names_group(self):
        """Проверяем, что у модели GROUP корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
