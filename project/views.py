import json

from datetime           import datetime, timedelta

from django.http        import JsonResponse
from django.views       import View

from user.utils         import user_decorator
from .models            import Category, Project, Gift, Community, Story, Like
from user.models        import User
from message.models     import Message

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
