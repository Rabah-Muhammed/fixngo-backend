# api/tokens.py
from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        # Create a refresh token (this calls the parent class's method)
        refresh = super().for_user(user)  # Use `super()` to call the parent method
        # Add custom claims
        refresh.payload['role'] = user.role
        refresh.payload['is_superuser'] = user.is_superuser  # Add superuser claim
        return refresh
