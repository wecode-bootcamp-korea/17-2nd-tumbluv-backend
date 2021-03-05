import json
import jwt

from django.http   import JsonResponse
from django.views  import View
from django.test   import TestCase, Client
from unittest.mock import patch, MagicMock

from .models     import User
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