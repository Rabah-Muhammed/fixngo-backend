from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class JWTAuth:
    @staticmethod
    async def authenticate_websocket(scope, token):
        try:
            access_token = AccessToken(token)
            user = await JWTAuth.get_user(access_token["user_id"])
            return user
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

    @staticmethod
    async def get_user(user_id):
        return await User.objects.aget(id=user_id)
