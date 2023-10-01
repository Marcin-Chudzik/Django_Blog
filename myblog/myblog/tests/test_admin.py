"""
Test for the Django admin pages.
"""
from django.test import (
    TestCase,
    Client,
)
from django.urls import reverse
from django.contrib import admin

from ..common.utils import (
    create_user,
    create_post,
    create_comment,
)


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        self.client = Client()
        self.admin_user = create_user(superuser=True)
        self.client.force_login(self.admin_user)
        self.user = create_user()
        self.post = create_post()
        self.comment = create_comment()

    def test_admin_models_url_patterns(self):
        """
        Test all default url patterns in admin site for each registered model.

        Tested url patterns:
        - blog_<model>_changelist
        - blog_<model>_add
        - blog_<model>_history
        - blog_<model>_delete
        - blog_<model>_change
        """
        admin_models = [model for model in admin.site._registry.values()
                        if 'blog' in str(model)]

        for model in admin_models:
            for pattern in model.get_urls():
                if pattern.name is not None:
                    model_name = str(model.opts).replace('blog.', '')
                    model_instance = getattr(self, model_name)
                    pattern_params = [
                        'id' if 'id' in param else param
                        for param in pattern.pattern.converters
                    ]

                url_params = [getattr(model_instance, param)
                              for param in pattern_params]

                if len(url_params) > 0:
                    url = reverse(f"admin:{pattern.name}", args=url_params)
                else:
                    url = reverse(f"admin:{pattern.name}")

                res = self.client.get(url)

                if 'list' in pattern.name:
                    for field in model.list_display:
                        self.assertContains(
                            res, getattr(model_instance, field)
                        )

                self.assertEqual(res.status_code, 200)
