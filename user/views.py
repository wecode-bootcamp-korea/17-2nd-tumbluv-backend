import requests
import json
import jwt

from django.http import JsonResponse
from django.views import View

from .models import User
from my_settings import (
    KAKAO_KEY, ALGORITHM, SECRET_KEY
)

class KakaoSignInView(View):

    def get(self, request):
        try:
            access_token = request.headers['Authorization']
            url          = "https://kapi.kakao.com/v2/user/me"
            header       = {
                'Authorization' : 'Bearer {}'.format(access_token)
            }
            response     = requests.get(url, headers = header).json()
                
            if 'email' not in response['kakao_account']:
                return JsonResponse({'message': 'EMAIL_REQUIRED'}, status = 405)

            user, is_user = User.objects.get_or_create(
                email         = response['kakao_account']['email'], 
                profile_image = response.get('kakao_account''profile''profile_image_url', None),
                fullname      = response['kakao_account']['profile']['nickname']
            )

            token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
            result = {
                'profile_image' : user.profile_image,
                'name'          :  user.fullname
                }
            
            return JsonResponse({'message': 'SUCCESS', 'data': result, 'token': token}, status = 200)

        except:
            return JsonResponse({'message': 'TOKEN_INVALID'}, status=401)