import requests
import json
import bcrypt
import jwt
import datetime

from random                         import randint

from django.http                    import JsonResponse
from django.views                   import View
from django.utils                   import timezone
from django.core.exceptions         import ValidationError
from django.core.validators         import validate_email
from django.core.mail               import EmailMessage

from .models                        import User, Verification
from my_settings                    import (
    KAKAO_KEY, ALGORITHM, SECRET_KEY, EMAIL
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

            access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
            result = {
                'profile_image' : user.profile_image,
                'name'          : user.fullname
                }
            
            return JsonResponse({'message': 'SUCCESS', 'data': result, 'access_token': access_token}, status = 200)

        except:
            return JsonResponse({'message': 'TOKEN_INVALID'}, status=401)

class SendMailView(View):
    def post(self, request):
        data       = json.loads(request.body)
        MAIL_TITLE = '안녕하세요. tumbluv입니다.'
        try:
            email = data['email']
            code  = randint(100000, 1000000)

            validate_email(email)

            if Verification.objects.filter(email=email).exists():
                trier      = Verification.objects.get(email=email)
                trier.code = code
                trier.save()          
            else:
                trier = Verification.objects.create(email=email, code=code)

            email      = EmailMessage(MAIL_TITLE, '인증번호: ' + str(trier.code), to=[email])
            email.send()

            return JsonResponse({'message': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except ValidationError:
            return JsonResponse({'message': 'INVALID_EMAIL'}, status=400)

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

class SignUpView(View):
    def post(self, request):
        MINIMUM_FULLNAME_LENGTH = 2
        MAXIMUM_FULLNAME_LENGTH = 40
        MINIMUM_PASSWORD_LENGTH = 6
        MAXIMUM_PASSWORD_LENGTH = 20
        data                    = json.loads(request.body)
        try:
            fullname        = data['fullname']
            email           = data['email']
            password        = data['password']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'ALREADY_EXIST'}, status=400)

            if (len(fullname) < MINIMUM_FULLNAME_LENGTH) or (len(fullname) > MAXIMUM_FULLNAME_LENGTH):
                return JsonResponse({'message': 'FULLNAME_VALIDATION_ERROR'}, status=400)
                
            if (len(password) < MINIMUM_PASSWORD_LENGTH) or (len(password) > MAXIMUM_PASSWORD_LENGTH):
                return JsonResponse({'message': 'PASSWORD_VALIDATION_ERROR'}, status=400)
            
            user = User.objects.create(
                email    = email,
                fullname = fullname,
                password = hashed_password
            )

            return JsonResponse({'message': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

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
                access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'message': 'SUCCESS', 'access_token': access_token}, status=200)
            return JsonResponse({'message': 'SIGNIN_FAIL'}, status=401)

        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status=400)
