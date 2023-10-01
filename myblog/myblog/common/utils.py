"""
Util functionalities.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from myblog.blog.models import (
    Post,
    Comment,
)

from taggit.models import Tag


def create_user(superuser: bool = False, *args, **kwargs) -> User:
    """Create and return a user."""
    last_user = get_user_model().objects.last()
    new_user_id = 1 if not last_user else last_user.id + 1
    email = f'test{new_user_id}@example.com'

    user = get_user_model().objects.create(
        email=kwargs.pop('email', email),
        username=kwargs.pop('username', email),
        password=kwargs.pop('password', 'sample123'),
        *args,
        **kwargs,
    )
    if superuser:
        """Promote to superuser."""
        user.is_staff = True
        user.is_superuser = True
        user.save()

    return user


def create_post(title: str = 'Test title', body: str = 'Test body',
                **extra_fields) -> Post:
    """Create and return a post."""
    post = Post.objects.create(
        title=title,
        body=body,
        **extra_fields,
    )

    return post


def create_comment(name: str = 'Test name', email: str = 'test@example.com',
                   body: str = 'Test body') -> Comment:
    """Create and return a comment."""
    comment = Comment.objects.create(
        name=name,
        email=email,
        body=body,
    )

    return comment


def create_tag(name: str = 'Test tag') -> Tag:
    """Create and return a tag."""
    return Tag.objects.create(name=name)
