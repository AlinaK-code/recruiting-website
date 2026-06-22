from rest_framework.permissions import BasePermission, SAFE_METHODS


def _has_recruiter_profile(user) -> bool:
    return hasattr(user, 'recruiter_profile') and user.recruiter_profile is not None


def _has_candidate_profile(user) -> bool:
    return hasattr(user, 'candidate_profile') and user.candidate_profile is not None


class IsRecruiterOwnerOrAdmin(BasePermission):
    """Чтение — всем; создание — работодателям и админам; изменение — автору или админу."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return request.user.is_staff or _has_recruiter_profile(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_staff
            or getattr(obj, 'created_by', None) == request.user
        )


class IsCandidateOrAdmin(BasePermission):
    """Отклики и резюме — только соискателям и админам."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return request.user.is_staff or _has_candidate_profile(request.user)
        return True


class IsResumeOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return request.user.is_staff or _has_candidate_profile(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_staff
            or getattr(obj, 'user', None) == request.user
        )


class IsReviewOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_staff
            or getattr(obj, 'user', None) == request.user
        )


# Обратная совместимость
IsOwnerOrAdmin = IsRecruiterOwnerOrAdmin
