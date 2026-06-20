from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    # Разреш предоставляет доступ только:
    # - администраторам (is_staff=True)
    # - авторам объекта (поле created_by совпадает с request.user)
    
    # Безопасные методы (GET, HEAD, OPTIONS) доступны всем.
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        # для создания объекта нужна авторизация
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
            
        return (
            request.user.is_staff or 
            getattr(obj, 'created_by', None) == request.user
        )