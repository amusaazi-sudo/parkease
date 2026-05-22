from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if user.is_superuser:
                return True
            user_groups = set(user.groups.values_list('name', flat=True))
            return bool(set(group_names).intersection(user_groups))
        return False
    return user_passes_test(in_groups, login_url='core:login')
