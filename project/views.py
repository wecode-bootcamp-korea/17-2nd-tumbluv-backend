import json
import boto3

from datetime         import datetime, timedelta

from django.db        import transaction
from django.db        import IntegrityError
from django.views     import View
from django.conf      import settings
from django.http      import JsonResponse

from my_settings      import (
    SECRET_KEY, ALGORITHM,
    AWS_ID    , AWS_KEY
)

from user.models      import User
from user.utils       import login_decorator, user_decorator
from user.models      import User
from .models          import  (
    Category, Project, Like,
    Gift, Story, Community
)
     
class RegisterView(View):   
    @login_decorator
    def post(self, request):
        data    = json.loads(request.body)
        user_id = request.user.id

        try:
            with transaction.atomic():
                name          = data['name']
                thumbnail_url = data['thumbnail_url']
                summary       = data['summary']
                category      = data['category']
                story         = data['story']
                goal_amount   = data['goal_amount']
                total_amount  = data['total_amount']
                opening_date  = data['opening_date']
                closing_date  = data['closing_date']
                project_uri   = data['project_uri']
                gifts         = data['gifts']

                category_id = Category.objects.get(name=category).id

                project = Project.objects.create(
                    category_id   = category_id,
                    user_id       = user_id,
                    name          = name,
                    opening_date  = datetime.strptime(opening_date,'%Y-%m-%d'),
                    closing_date  = datetime.strptime(closing_date,'%Y-%m-%d'),
                    thumbnail_url = thumbnail_url,
                    goal_amount   = goal_amount,
                    total_amount  = total_amount,
                    summary       = summary,
                    project_uri   = project_uri
                )

                Story.objects.create(
                    content    = story,
                    project_id = project.id
                    )

                for gift in gifts: 
                    Gift.objects.create(
                        name          = gift['gift_name'],
                        price         = gift['gift_price'],
                        stock         = gift['gift_stock'],
                        project_id    = project.id,
                        quantity_sold = gift['quantity_sold']
                    )

                return JsonResponse({'message': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
            
        except IntegrityError:
            return JsonResponse({"message": "DUPLICATED_ENTRY"}, status=400)

class FileUpload(View):
    def post(self, request):
        s3_client = boto3.client(
        's3',
        aws_access_key_id     = AWS_ID,
        aws_secret_access_key = AWS_KEY
    )
        
        try:
            image       = request.FILES['filename']
            upload_time = (str(datetime.now())).replace(" ", "_")
            image_type  = (image.content_type).split("/")[1]
            
            s3_client.upload_fileobj(
                image,
                "tumbluv",
                upload_time+"."+image_type,
                ExtraArgs={
                    "ContentType": image.content_type
                }
            )

            image_url = "https://tumbluv.s3.ap-northeast-2.amazonaws.com/" + upload_time + "." + image_type
            image_url = image_url.replace(" ", "")
            
            return JsonResponse({"thumbnail_url": image_url}, status=200)
        
        except:
            return JsonResponse({'message': 'FILE_NOT_ATTACHED'}, status=400)

class ProjectDetailView(View):
    @user_decorator
    def get(self, request, project_uri):
        today = datetime.now()

        if not Project.objects.filter(project_uri=project_uri).exists():
            return JsonResponse({'message': 'PROJECT_NOT_EXIST'}, status=404)

        project = Project.objects.get(project_uri=project_uri)

        project_info = {
            'category'         : project.category.name,
            'name'             : project.name,
            'thumbnail_url'    : project.thumbnail_url,
            'creator'          : project.user.fullname,
            'achieved_rate'    : project.achieved_rate,
            'total_amount'     : project.total_amount,
            'rest_date'        : (project.closing_date - today).days,
            'total_supporters' : project.total_supporters,
            'goal_amount'      : project.goal_amount,
            'payment_date'     : project.closing_date + timedelta(days=1),
            'like'             : False if (request.user is None or not project.like_set.filter(user_id=request.user.id).exists()) else True,
            'option'           : [{
                'id'          : option.id,
                'description' : option.name,
                'money'       : option.price,
                'people'      : option.quantity_sold,
                'stock'       : option.stock,
                } for option in project.gift_set.all()],
            }

        creator_info = {
            'name'                : project.user.fullname,
            'creator_description' : project.user.user_description
            }

        tab = {
            'story'  : project.story_set.get(project_id=project.id).content,
            'communities' : [{
                'user'       : community.user.fullname,
                'comment'    : community.comment,
                'past_date'  : (today-community.updated_at).days,
                'created_at' : community.created_at,
                'recomment'  : [{
                    'user'       : recomment.user.fullname,
                    'comment'    : recomment.comment,
                    'created_at' : recomment.created_at
                    } for recomment in community.community_set.all()
                    ] if community.community_set.exists() else ''
                } for community in project.community_set.filter(parent_id=None).order_by('-created_at')
                ] if project.community_set.exists() else ''
            }

        return JsonResponse({
            'project_info': project_info,
            'creator_info': creator_info,
            'tab'         : tab
            }, status=200)