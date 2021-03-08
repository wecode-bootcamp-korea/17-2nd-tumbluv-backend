import json
import jwt
import time
import datetime
import bcrypt

from django.http    import JsonResponse
from django.views   import View
from django.test    import TestCase, Client
from unittest.mock  import patch, MagicMock

from .models        import User, Verification
from .views         import KakaoSignInView
from my_settings    import ALGORITHM, SECRET_KEY

class KakaoSignInTest(TestCase):
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

class TestSignInView(TestCase):
    
    def setUp(self):
        User.objects.create(
            email    = 'test1234@test.com',
            password = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode()
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_signinview_success(self):
        client = Client()
        user   = {
                'id'       : 1,
                'email'    : 'test1234@test.com',
                'password' : '123456'
            }
        header   = {'Authorization': 'access_token'}
        response = client.post('/user/signin', json.dumps(user), content_type='application/json', **header)
        user_id  = User.objects.get(email='test1234@test.com').id

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message': 'SUCCESS',
                'access_token': jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm=ALGORITHM)
            }
        )

    def test_signinview_invalid_user(self):
        client = Client()
        user   = {
                'email'    : 'test5678@test.com',
                'password' : '123456'
            }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                'message': 'INVALID_USER'
            }
        )

    def test_signinview_invalid_password(self):
        client = Client()
        user = {
                'email'    : 'test1234@test.com',
                'password' : '234567'
            }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                'message': 'SIGNIN_FAIL'
            }
        )

    def test_signinview_invalid_key(self):
        client = Client()
        user = {
                'user_email' : 'test1234@test.com',
                'password'   : '123456'
            }
        response = client.post('/user/signin', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'INVALID_KEY'
            }
        )
