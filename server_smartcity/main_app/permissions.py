from rest_framework import permissions


class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:

            # draft hanya pemilik yang boleh lihat
            if obj.status == 'DRAFT':
                return obj.reporter == request.user

            return True

        # PUT, PATCH, DELETE
        return (
            obj.reporter == request.user
            and obj.status == 'DRAFT'
        )