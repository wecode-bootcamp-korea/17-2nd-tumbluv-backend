import json
import unittest
import jwt
import mock
import datetime

from django.core.files import File
from unittest.mock     import patch, MagicMock
from freezegun         import freeze_time

from django.db         import transaction
from django.test       import TestCase, Client
from django.views      import View
from django.conf       import settings
from django.http       import JsonResponse

from my_settings       import (
    SECRET_KEY, ALGORITHM,
)

from user.models       import User
from user.utils        import login_decorator
from user.models       import User
from .models           import  (
    Category, Project, Like,
    Gift, Story, Community
)

class FileViewTest(TestCase):

    @patch('project.views.boto3')
    def test_file_upload_success(self, mocked_s3_client):
        self.freezer = freeze_time("2021-03-11 21:00:49.951790")
        self.freezer.start()
        
        image      = mock.MagicMock(spec=File, name='file.jpeg')
        image.name = 'file.jpg'

        class MockedResponse:
            def json(self):
                return image
        
        mocked_s3_client.upload_fileobj = MagicMock(return_value=MockedResponse())
        client                          = Client()
        data                            = {'filename':image}
        response                        = client.post("/project/file", data)
        
        self.freezer.stop()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                "thumbnail_url" : "https://tumbluv.s3.ap-northeast-2.amazonaws.com/2021-03-11_21:00:49.951790.jpeg"
            }
        ) 
    
    @patch('project.views.boto3')
    def test_file_upload_file_missing(self, mocked_s3_client):
        self.freezer = freeze_time("2021-03-11 21:00:49.951790")
        self.freezer.start()
        
        image      = mock.MagicMock(spec=None, name=None)
        image.name = None

        class MockedResponse:
            def json(self):
                return image
        
        mocked_s3_client.upload_fileobj = MagicMock(return_value=MockedResponse())
        client                          = Client()
        data                            = {'filename':image}
        response                        = client.post("/project/file", data)
        
        self.freezer.stop()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                "message" : "FILE_NOT_ATTACHED"
            }
        ) 


class ProjectRegisterTest(TestCase):
    
    def setUp(self):
        User.objects.create(
            id       = 1,
            fullname = "이단비",
            email    = "danbi@so.cute"
        )

        Category.objects.create(
            id   = 1,
            name = "카테고리"
        )

        Project.objects.create(
            id               = 1,
            name             = "단비 간식주기",
            opening_date     = "2021-03-11",
            closing_date     = "2021-03-15",
            total_supporters = None,
            created_at       = "2021-03-10",
            updated_at       = "2021-03-10",
            achieved_rate    = None,
            total_amount     = None,
            thumbnail_url    = "https://tumbluv.s3.ap-northeast-2.amazonaws.com/2021-03-10_01:02:57.219378.jpeg",
            goal_amount      = 10000000,
            summary          = "뚱비는 다이어트중",
            user_id          = 1,
            category_id      = 1,
            project_uri      = "/feed-danbi"
        )

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
    
    def test_project_register_success(self):
        user         = User.objects.get(id=1)
        access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        body         = {
            "name"         : "단비랑 산책하기",
            "summary"      : "귀여운 단비와 산책 할 기회를 드려요",
            "category"     : "카테고리",
            "story"        : "<div><p>스토리</p></div>",
            "goal_amount"  : 10000000000,
            "opening_date" : "2013-07-03",
            "closing_date" : "2021-07-03",
            "thumbnail_url": "https://tumbluv.s3.ap-northeast-2.amazonaws.com/2021-03-10_01:02:57.219378.jpeg",
            "project_uri"  : "with-danbi",
            "gifts"        : [{
                "gift_name"     : "first gift",
                "gift_price"    : 2000000,
                "gift_stock"    : 20,
                "quantity_sold" : 0
                },{
                "gift_name"     : "second gift",
                "gift_price"    : 3000000,
                "gift_stock"    : 30,
                "quantity_sold" : 0
                },{
                "gift_name"     : "third gift",
                "gift_price"    : 5000000,
                "gift_stock"    : 50,
                "quantity_sold" : 0
                }],
            "total_amount":0
        }

        client   = Client()
        response = client.post('/project/register', json.dumps(body), content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'message': 'SUCCESS'
            }
        )

    def test_project_register_fail(self):
        user         = User.objects.get(id=1)
        access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        body         = {
            "name"          : "단비랑 산책하기",
            "summary"       : "귀여운 단비와 산책 할 기회를 드려요",
            "category"      : "카테고리",
            "story"         : "<div><p>스토리</p></div>",
            "goal_amount"   : 10000000000,
            "opening_date"  : "2013-07-03",
            "closing_date"  : "2021-07-03",
            "thumbnail_url" : "https://tumbluv.s3.ap-northeast-2.amazonaws.com/2021-03-10_01:02:57.219378.jpeg",
            "project_uri"   : "with-danbi",
            "gifts"         : [{
                "gift_name"     : "first gift",
                "gift_price"    : 2000000,
                "gift_stock"    : 20,
                "quantity_sold" : 0
                },{
                "gift_name"     : "second gift",
                "gift_price"    : 3000000,
                "gift_stock"    : 30,
                "quantity_sold" : 0
                },{
                "gift_name"     : "third gift",
                "gift_price"    : 5000000,
                "gift_stock"    : 50,
                "quantity_sold" : 0
                }],
        }

        client   = Client()
        response = client.post('/project/register', json.dumps(body), content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                'message': 'KEY_ERROR'
            }
        )

    def test_project_register_token_invalid(self):
        user         = User.objects.get(id=1)
        access_token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        body         = {
            "name"          : "단비 간식주기",
            "summary"       : "귀여운 단비와 산책 할 기회를 드려요",
            "category"      : "카테고리",
            "story"         : "<div><p>스토리</p></div>",
            "goal_amount"   : 10000000000,
            "opening_date"  : "2013-07-03",
            "closing_date"  : "2021-07-03",
            "thumbnail_url" : "https://tumbluv.s3.ap-northeast-2.amazonaws.com/2021-03-10_01:02:57.219378.jpeg",
            "project_uri"   : "/feed-danbi",
            "gifts"         : [{
                "gift_name"     : "first gift",
                "gift_price"    : 2000000,
                "gift_stock"    : 20,
                "quantity_sold" : 0
                },{
                "gift_name"     : "second gift",
                "gift_price"    : 3000000,
                "gift_stock"    : 30,
                "quantity_sold" : 0
                },{
                "gift_name"     : "third gift",
                "gift_price"    : 5000000,
                "gift_stock"    : 50,
                "quantity_sold" : 0
                }],
            "total_amount":0
        }

        client   = Client()
        response = client.post('/project/register', json.dumps(body), content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                'message': 'DUPLICATED_ENTRY'
            }
        )

class TestProjectDetailView(TestCase):
    
    def setUp(self):
        self.freezer = freeze_time("2021-01-20 00:00:00")
        self.freezer.start()

        User.objects.create(
                id               = 1,
                fullname         = '사용자1',
                email            = 'email1',
                user_description = '소개1'
                )

        User.objects.create(
                id               = 2,
                fullname         = '사용자2',
                email            = 'email2',
                user_description = '소개2'
                )

        Category.objects.create(
                id   = 1,
                name = '카테고리1'
                )

        Project.objects.create(
                id                  = 1,
                user_id             = 1,
                category_id         = 1,
                name                = '프로젝트1',
                opening_date        = datetime.datetime(2021, 1, 1, 0, 0),
                closing_date        = datetime.datetime(2021, 1, 31, 0, 0),
                total_supporters    = 50,
                achieved_rate       = 0.50,
                total_amount        = 300000.00,
                thumbnail_url       = '사진1',
                goal_amount         = 3000000.00,
                summary             = '프로젝트요약1',
                project_uri         = 'uri'
                )

        Gift.objects.create(
                id                  = 1,
                project_id          = 1,
                name                = '옵션1',
                price               = 1000.00,
                quantity_sold       = 10,
                stock               = 10
                )
        
        Community.objects.create(
                id          = 1,
                user_id     = 1,
                project_id  = 1,
                parent_id   = None,
                comment     = '댓글1'
                )

        Community.objects.create(
                id          = 2,
                user_id     = 2,
                project_id  = 1,
                parent_id   = 1,
                comment     = '댓글1-1'
                )

        Story.objects.create(
                id          = 1,
                project_id  = 1,
                content     = '프로젝트 내용'
                )

        Like.objects.create(
                id          = 1,
                project_id  = 1,
                user_id     = 1
                )

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
        Project.objects.all().delete()
        Gift.objects.all().delete()
        Community.objects.all().delete()
        Story.objects.all().delete()
        self.freezer.stop()

    def test_projectdetailview_get_project_success(self):
        project_uri = 'uri'
        response   = self.client.get(f'/project/{project_uri}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'project_info': {
                        'category'         : '카테고리1',
                        'name'             : '프로젝트1',
                        'thumbnail_url'    : '사진1',
                        'creator'          : '사용자1',
                        'achieved_rate'    : '0.50',
                        'total_amount'     : '300000.00',
                        'rest_date'        : 11,
                        'total_supporters' : 50,
                        'goal_amount'      : '3000000.00',
                        'payment_date'     : datetime.datetime(2021, 2, 1, 0, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                        'like'             : False,
                        'option'           : [{
                            'id'           : 1,
                            'description'  : '옵션1',
                            'money'        : '1000.00',
                            'people'       : 10,
                            'stock'        : 10
                            }]
                        },
                    'creator_info': {
                        'name'               : '사용자1',
                        'creator_description': '소개1'
                        },
                    'tab': {
                        'story'       : '프로젝트 내용',
                        'communities' : [{
                            'user'       : '사용자1',
                            'comment'    : '댓글1',
                            'past_date'  : 0,
                            'created_at' : datetime.datetime(2021, 1, 20, 0, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                            'recomment'  : [{
                                'user'       : '사용자2',
                                'comment'    : '댓글1-1',
                                'created_at' : datetime.datetime(2021, 1, 20, 0, 0).strftime('%Y-%m-%dT%H:%M:%S')
                                }]
                            }]
                        }
                    })

    def test_projectdetailview_get_user_project_success(self):
        project_uri  = 'uri'
        access_token = jwt.encode({'id': 1}, SECRET_KEY, algorithm=ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}
        response     = self.client.get(f'/project/{project_uri}', content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'project_info': {
                        'category'         : '카테고리1',
                        'name'             : '프로젝트1',
                        'thumbnail_url'    : '사진1',
                        'creator'          : '사용자1',
                        'achieved_rate'    : '0.50',
                        'total_amount'     : '300000.00',
                        'rest_date'        : 11,
                        'total_supporters' : 50,
                        'goal_amount'      : '3000000.00',
                        'payment_date'     : datetime.datetime(2021, 2, 1, 0, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                        'like'             : True,
                        'option'           : [{
                            'id'           : 1,
                            'description'  : '옵션1',
                            'money'        : '1000.00',
                            'people'       : 10,
                            'stock'        : 10
                            }]
                        },
                    'creator_info': {
                        'name'               : '사용자1',
                        'creator_description': '소개1'
                        },
                    'tab': {
                        'story'       : '프로젝트 내용',
                        'communities' : [{
                            'user'       : '사용자1',
                            'comment'    : '댓글1',
                            'past_date'  : 0,
                            'created_at' : datetime.datetime(2021, 1, 20, 0, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                            'recomment'  : [{
                                'user'       : '사용자2',
                                'comment'    : '댓글1-1',
                                'created_at' : datetime.datetime(2021, 1, 20, 0, 0).strftime('%Y-%m-%dT%H:%M:%S')
                                }]
                            }]
                        }
                    })

    def test_projectdetailview_get_project_not_exists(self):
        project_uri = 'uri2'
        response   = self.client.get(f'/project/{project_uri}', content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                'message': 'PROJECT_NOT_EXIST'
            }

