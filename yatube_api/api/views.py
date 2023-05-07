from django.shortcuts import get_object_or_404
from posts.models import Comment, Group, Post
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Пользователь может изменять и удалять только свои объекты."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    """CRUD для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def perform_create(self, serializer) -> None:
        """Автоматически присваивает текущего пользователя как автора поста."""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр списка групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD для комментариев."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def perform_create(self, serializer) -> None:
        """
        Автоматически присваивает текущего пользователя как автора комментария
        и связывает его с постом.
        """
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self) -> list[Comment]:
        """Возвращает список комментариев, относящихся к конкретному посту."""
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, pk=post_id)
        return post.comments.all()
