import json
import boto3

from datetime         import date, datetime, timedelta

from django.db        import transaction
from django.db        import IntegrityError
from django.views     import View
from django.db.models import Q
from django.conf      import settings
from django.http      import JsonResponse
from django.utils     import timezone

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

class ProjectView(View):
    def get(self, request):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 12))
        category = request.GET.get('category', None)
        status = request.GET.get('status', 0)
        achieve = request.GET.get('achieve', None)
        money = request.GET.get('money', 0)
        ordering = request.GET.get('sort', None)
        
        q = Q()

        if category:
            q &= Q(category=category)

        if status == 'all':
            q.add(Q(opening_date__gte=datetime.today()), q.AND)

        if status == 'onGoing':
            q.add(Q(opening_date__lte=datetime.today()), q.AND)
            q.add(Q(closing_date__gte=datetime.today()), q.AND)

        if status == 'confirm':
            q &= Q(achieved_rate__gte=100)

        if status == 'prelaunching':
            q &= Q(opening_date__gt=datetime.today())

        if achieve == 'under75':
            q &= Q(achieved_rate__lte=75)

        if achieve == 'under100':
            q.add(Q(achieved_rate__gte=75), q.AND)
            q.add(Q(achieved_rate__lte=100), q.AND)

        if achieve == '100up':
            q &= Q(achieved_rate__gte=100)

        if money == 'all':
            q &= Q(total_amount__gte=0)

        if money == 'under1m':
            q &= Q(total_amount__lte=1000000)

        if money == 'under10m':
            q.add(Q(total_amount__gt=1000000), q.AND)
            q.add(Q(total_amount__lte=10000000), q.AND)

        if money == 'under50m':
            q.add(Q(total_amount__gt=10000000), q.AND)
            q.add(Q(total_amount__lte=50000000), q.AND)

        if money == 'under100m':
            q.add(Q(total_amount__gt=50000000), q.AND)
            q.add(Q(total_amount__lte=100000000), q.AND)

        if money == '100mup':
            q &= Q(total_amount__gt=100000000)
            
        projects = Project.objects.filter(q)

        if ordering == 'popular':
            projects = projects.order_by('-achieved_rate')
        if ordering == 'publishedAt':
            projects = projects.order_by('-opening_date')
        if ordering == 'pledges':
            projects = projects.order_by('-total_supporters')
        if ordering == 'amount':
            projects = projects.order_by('-total_amount')
        if ordering == 'endedAt':
            projects = projects.order_by('closing_date')

        project_list = [{
            'thumbnail_url': project.thumbnail_url,
            'name': project.name,
            'category': project.category.name,
            'user': project.user.fullname,
            'summary': project.summary,
            'total_amount': int(project.total_amount),
            'achieved_rate': int(project.achieved_rate),
            'days_left': (project.closing_date - timezone.now()).days,
            'project_uri': project.project_uri,
            # 'islike': project.like_set.get(project=project)
            } for project in projects][offset:offset+limit]

        return JsonResponse({'count': projects.count(), 'results': project_list}, status=200)