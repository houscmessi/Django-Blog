
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Tag

class SmokeTests(TestCase):
    def test_home_page(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_tag_page(self):
        u = User.objects.create_user(username='u1', password='p')
        p = Post.objects.create(title='Hello', body_md='**world**', author=u, status='published')
        t,_ = Tag.objects.get_or_create(name='Django')
        p.tags.add(t)
        r = self.client.get('/tag/django/')
        self.assertContains(r, 'Hello')
