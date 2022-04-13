from http import HTTPStatus

from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from yatube.settings import COUNT_OF_SHOWED_POSTS

from posts.models import Post, Group, User, Comment, Follow


class PostPagesTest(TestCase):
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
        self.author_client = Client()
        self.author_client.force_login(PostPagesTest.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': f'{self.post.group.slug}'
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': f'{self.user.username}'
            }): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.pk}'
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.pk}'
            }): 'posts/post_create.html',
        }
        for reverse_name, template, in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_context_index(self):
        """Проверка контекста домашней страницы index"""
        response = self.author_client.get(reverse('posts:index'))
        post_object = response.context.get('page_obj')[0]
        self.assertIsInstance(post_object, Post)
        post_text_0 = post_object.text
        post_author_0 = post_object.author
        post_image_0 = post_object.image
        self.assertEqual(post_text_0, PostPagesTest.post.text)
        self.assertEqual(post_author_0, PostPagesTest.post.author)
        self.assertEqual(post_image_0, PostPagesTest.post.image)

    def test_page_context_group_list_filtered(self):
        """Проверка контекста списка постов в группе"""
        response = (self.author_client.get(reverse(
            'posts:group_list', kwargs={'slug': PostPagesTest.group.slug})))
        object_group = response.context.get('page_obj')[0]
        post_object_group = object_group.group
        self.assertIsInstance(post_object_group, Group)
        post_text_0 = object_group.text
        post_author_0 = object_group.author
        post_image_0 = object_group.image
        self.assertEqual(post_text_0, PostPagesTest.post.text)
        self.assertEqual(post_author_0, PostPagesTest.post.author)
        var_group = response.context.get('group')
        self.assertEqual(var_group, PostPagesTest.group)
        self.assertEqual(post_image_0, PostPagesTest.post.image)

    def test_profile_context(self):
        """Проверка контекста списка постов пользователя"""
        response = (self.author_client.get(reverse(
            'posts:profile', kwargs={'username': PostPagesTest.user})))
        first_object_profile = response.context.get('page_obj')[0]
        self.assertEqual(first_object_profile, PostPagesTest.post)
        var_author = response.context.get('author')
        image_test = first_object_profile.image
        self.assertEqual(var_author, PostPagesTest.user)
        self.assertEqual(image_test, PostPagesTest.post.image)

    def test_post_detail_context(self):
        """Проверка контекста поста одного пользователя"""
        response = (self.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostPagesTest.post.pk})))
        first_object_post_detail = response.context.get('post').text
        image_test = response.context.get('post').image
        self.assertEqual(first_object_post_detail, PostPagesTest.post.text)
        self.assertEqual(image_test, PostPagesTest.post.image)

    def test_post_create_context(self):
        """Проверка создания поста с правильным контекстом"""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_show_correct_context_post_edit(self):
        """Проверка контекста post_edit"""
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostPagesTest.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        var_is_edit = response.context.get('is_edit')
        self.assertTrue(var_is_edit)


class PostPagesPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.COUNT_TEST_PAGES = 13
        cls.user = User.objects.create_user(username='NoName_2')
        cls.group = Group.objects.create(
            title='Тестовая группа_2',
            slug='Test_slug_2',
            description='Тестовое описание_2',
        )
        cls.posts = []
        for i in range(cls.COUNT_TEST_PAGES):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostPagesPaginatorTest.user)

    def test_first_page_contains_ten_posts(self):
        """Проверка паджинатора на десять постов"""
        list_urls = {
            reverse('posts:index'): 'posts/index',
            reverse('posts:group_list', kwargs={
                'slug': PostPagesPaginatorTest.group.slug}): 'group',
            reverse('posts:profile', kwargs={
                'username':
                PostPagesPaginatorTest.user.username
            }):
            'profile',
        }
        for tested_url in list_urls.keys():
            response = self.author_client.get(tested_url)
        self.assertEqual(len(response.context.get('page_obj').object_list),
                         COUNT_OF_SHOWED_POSTS)

    def test_second_page_contains_three_posts(self):
        """Проверка паджинатора на три поста"""
        list_urls = {
            reverse('posts:index') + '?page=2': 'posts/index',
            reverse('posts:group_list', kwargs={
                'slug': PostPagesPaginatorTest.group.slug})
            + '?page=2': 'group',
            reverse('posts:profile', kwargs={
                'username': PostPagesPaginatorTest.user.username
            })
            + '?page=2':
            'profile',
        }
        for tested_url in list_urls.keys():
            response = self.author_client.get(tested_url)
        self.assertEqual(len(response.context.get(
            'page_obj').object_list),
            self.COUNT_TEST_PAGES % COUNT_OF_SHOWED_POSTS
        )


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
            author=self.user
        ).exists()
        )
        first_comment = response.context.get('comments')[0]
        self.assertNotEqual(first_comment, form_data['text'])
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
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}))


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='User_2')
        cls.user_following = User.objects.create_user(username='User_3')
        
        cls.post = Post.objects.create(
            text='Текст поста для подписчиков',
            author=cls.user_following
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.user_follower)
        self.following_client = Client()
        self.following_client.force_login(self.user_following)

    def test_auth_can_subsribe_and_unsub(self):
        """Тест авторизованного пользователя на подписку и отписку"""
        self.follower_client.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)
        self.follower_client.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.follower_client.get(reverse('posts:profile_unfollow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """Тест записи пользователя в ленте подписчиков"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.follower_client.get('/follow/')
        follow_text = response.context.get('page_obj')[0].text
        self.assertEqual(follow_text, self.post.text)
        response = self.following_client.get('/follow/')
        self.assertNotContains(response, self.post.text)

        
