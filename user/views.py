import requests
import json
import jwt
import bcrypt

from django.http    import JsonResponse
from django.views   import View
from django.utils   import timezone

from .models        import User, Verification
from my_settings    import KAKAO_KEY, ALGORITHM, SECRET_KEY

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

class ValidateCodeView(View):
    def post(self, request):
        TIME_LIMIT = 60

        data = json.loads(request.body)
        try:
            code  = data['code']
            email = data['email']
            trier = Verification.objects.get(email=email)

            if (timezone.now() - trier.created_at).seconds >= TIME_LIMIT:
                trier.delete()
                return JsonResponse({'message': 'TIME_OUT'}, status=400)

            if code != trier.code:
                return JsonResponse({'message': 'INVALID_CODE'}, status=400)
            trier.delete()
            return JsonResponse({'message': 'EMAIL_VALIDATE_SUCCESS'}, status=200)
                
        except KeyError:
            return JsonResponse({'message': 'NEED_CODE'}, status=400)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            email    = data['email']
            password = data['password']

            if not User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'INVALID_USER'}, status=401)

            user = User.objects.get(email=email)

            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'message': 'SUCCESS', 'access_token': access_token}, status=200)
            return JsonResponse({'message': 'SIGNIN_FAIL'}, status=401)

        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status=400)
