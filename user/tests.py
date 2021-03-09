import json
import jwt
import time
import datetime

from django.http   import JsonResponse
from django.views  import View
from django.test   import TestCase, Client
from unittest.mock import patch, MagicMock

from .models     import User, Verification
from .views      import KakaoSignInView
from my_settings import ALGORITHM, SECRET_KEY

class KakaoSignInTest(TestCase):

    def tearDown(self):
        User.objects.all().delete()

    @patch('user.views.requests')
    def test_kakao_login_success(self, mocked_request):

        class KakaoResponse:
            def json(self):
                return {
                    "kakao_account": {
                        "email"   : "danbi@so.cute",
                        "profile" : {
                            "nickname" : "단비"
                        }
                    }

                }
            
        client             = Client()
        mocked_request.get = MagicMock(return_value=KakaoResponse())
        header             = {'HTTP_Authorization': 'access_token'}
        response           = client.get('/user/signin/kakao', content_type='application/json', **header)
        user_id            = User.objects.get(email = 'danbi@so.cute').id
       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'message'       : 'SUCCESS', 
                'data': {
                    'profile_image' : None,
                    'name'          : "단비"
                },
                'token': jwt.encode({'id':user_id}, SECRET_KEY, algorithm=ALGORITHM)
            }
        )

    @patch('user.views.requests')
    def test_kakao_login_failed_invalid_token(self, mocked_request):

        class KakaoResponse:
            def json(self):
                return {
                    "code": -401,
                    "msg": "this access token does not exist"
                }

        client             = Client()
        mocked_request.get = MagicMock(return_value=KakaoResponse())
        header             = {'HTTP_Authorization': '12345' }
        response           = client.get('/user/signin/kakao', content_type='application/json', **header)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message': 'TOKEN_INVALID'})

class TestValidateCodeView(TestCase):

    def setUp(self):
        Verification.objects.create(
            email = 'test1234@test.com',
            code  = '123456'
        )
    
    def tearDown(self):
        Verification.objects.all().delete()
    
    def test_validatecodeview_valid_code(self):
        client = Client()
        verification = {
                'email': 'test1234@test.com',
                'code' : '123456'
                }
        response = client.post('/user/signup/email-validation', json.dumps(verification), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message': 'EMAIL_VALIDATE_SUCCESS'
                }
        )

    def test_validatecodeview_need_code(self):
        client = Client()
        verification = {
                'email'  : 'test1234@test.com',
                'number' : '123456'
                }
        response = client.post('/user/signup/email-validation', json.dumps(verification), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'NEED_CODE'
                }
        )

    def test_validatecodeview_invalid_code(self):
        client = Client()
        verification = {
                'email': 'test1234@test.com',
                'code' : '234567'
                }
        response = client.post('/user/signup/email-validation', json.dumps(verification), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'INVALID_CODE'
                }
        )

    def test_validatecodeview_time_out(self):
        client = Client()
        verification = {
                'email': 'test1234@test.com',
                'code' : '123456'
                }
        time.sleep(65)
        response = client.post('/user/signup/email-validation', json.dumps(verification), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'TIME_OUT'
                }
        )

    def test_validatecodeview_time_in(self):
        client = Client()
        verification = {
                'email': 'test1234@test.com',
                'code' : '123456'
                }
        time.sleep(40)
        response = client.post('/user/signup/email-validation', json.dumps(verification), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message': 'EMAIL_VALIDATE_SUCCESS'
                }
        )
