import json
import jwt
import datetime
from freezegun      import freeze_time

from django.test    import TestCase, Client
from unittest.mock  import patch

from my_settings    import SECRET_KEY, ALGORITHM
from .models        import Category, Project, Gift, Community, Story, Like
from user.models    import User

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
        )
