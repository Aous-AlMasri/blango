from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from blog.api.serializers import (
  PostSerializer, 
  UserSerializer, 
  PostDetailSerializer,
  TagSerializer,
  )
from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject
from blog.models import Post, Tag
from blango_auth.models import User

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.http import Http404

class UserDetail(generics.RetrieveAPIView):
  queryset = User.objects.all()
  lookup_field = "email"
  serializer_class = UserSerializer

  @method_decorator(cache_page(300))
  def get(self, *args, **kwargs):
    return super(UserDetail, self).get(*args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
  permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
  queryset = Post.objects.all()

  def get_queryset(self):
    user = self.request.user
    queryset = self.queryset
    now = timezone.now()

    # Base visibility rules
    if user.is_anonymous:
        queryset = queryset.filter(published_at__lte=now)  # Anonymous: only published
    elif user.is_staff:
        queryset = queryset.all()  # Staff: see all posts
    else:
        # Non-staff users: published posts + their own posts (any status)
        queryset = queryset.filter(Q(published_at__lte=now) | Q(author=user))

    # Time period filtering
    time_period_name = self.kwargs.get("period_name")
    if time_period_name:
        # Apply time window first
        if time_period_name == "new":
            queryset = queryset.filter(published_at__gte=now - timedelta(hours=1))
        elif time_period_name == "today":
            queryset = queryset.filter(published_at__date=now.date())
        elif time_period_name == "week":
            queryset = queryset.filter(published_at__gte=now - timedelta(days=7))
        else:
            raise Http404(f"Invalid time period: {time_period_name}")

        # Critical addition: For non-staff, enforce published_at <= now
        if not user.is_staff:
            queryset = queryset.filter(published_at__lte=now)

    return queryset
  """
  def get_queryset(self):
    if self.request.user.is_anonymous:
      # published only
      queryset = self.queryset.filter(published_at__lte=timezone.now())

    elif /not/ self.request.user.is_staff:
      # allow all
      queryset = self.queryset
    else:
      queryset = self.queryset.filter(
        Q(published_at__lte=timezone.now()) | Q(author=self.request.user)
      )

    time_period_name = self.kwargs.get("period_name")

    if not time_period_name:
      # no further filtering required
      return queryset

    if time_period_name == "new":
      return queryset.filter(
        published_at__gte=timezone.now() - timedelta(hours=1)
      )
    elif time_period_name == "today":
      return queryset.filter(
        published_at__date=timezone.now().date(),
      )
    elif time_period_name == "week":
      return queryset.filter(published_at__gte=timezone.now() - timedelta(days=7))
    else:
      raise Http404(
        f"Time period {time_period_name} is not valid, should be "
        f"'new', 'today' or 'week'"
      )
"""
  def get_serializer_class(self):
    if self.action in ("list", "create"):
      return PostSerializer
    return PostDetailSerializer
  
  # we cached the list here on both token and session because we want to
  # filter the queryset on all the methods (list, retrieve, ...)
  @method_decorator(cache_page(120))
  @method_decorator(vary_on_headers("Authorization", "Cookie"))
  def list(self, *args, **kwargs):
    return super(PostViewSet, self).list(*args, **kwargs)

  @method_decorator(cache_page(300))
  @method_decorator(vary_on_headers("Authorization"))
  @method_decorator(vary_on_cookie)
  @action(methods=["get"], detail=False, name="Posts by the logged in user")
  def mine(self, request):
    if request.user.is_anonymous:
      raise PermissionDenied("You must be logged in to see which Posts are yours.")
    posts = self.get_queryset().filter(author=request.user)
    serializer = PostSerializer(posts, many=True, context={"request": request})
    return Response(serializer.data)

"""
class PostList(generics.ListCreateAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
  queryset = Post.objects.all()
  serializer_class = PostDetailSerializer
"""

class TagViewSet(viewsets.ModelViewSet):
  queryset = Tag.objects.all()
  serializer_class = TagSerializer

  @action(methods=["get"], detail=True, name="Posts with the Tag")
  def posts(self, request, pk=None):
    tag = self.get_object()
    post_serializer = PostSerializer(
      tag.posts, many=True, context={"request": request}
    )
    return Response(post_serializer.data)
  
  @method_decorator(cache_page(300))
  def list(self, *args, **kwargs):
    return super(TagViewSet, self).list(*args, **kwargs)
  
  @method_decorator(cache_page(300))
  def retrieve(self, *args, **kwargs):
    return super(TagViewSet, self).retrieve(*args, **kwargs)
