class AccountsBackend:

    def authenticate(self, request, username=None, password=None, **kwargs):
        from accounts.models import User
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        from accounts.models import User
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
