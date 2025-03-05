from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class JWTAuth:
    @staticmethod
    async def authenticate_websocket(scope, token):
        try:
            access_token = AccessToken(token)
            user = await JWTAuth.get_user(access_token["user_id"])
            return user
        except TokenError:
            raise AuthenticationFailed("Invalid or expired token")
        except Exception:
            raise AuthenticationFailed("Authentication error")

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")