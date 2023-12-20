from .models import Site_Bots, Notifications, Home_Details, category
from django.conf import settings
import jwt
from .views import employee_access, get_logged_user_data


def loadBots(request):
    context={}
    try:
        headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).all()
        bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).all()
        context['head_bots']=headbots
        context['body_bots']=bodybots
        return context
    except (KeyError,IndexError):
        return context
    except Exception as e:
        print(f':::: Error occured ::::\nfile path: {__file__}, loadUserdata() \n Error desc: {str(e)}')
    return context


def loadUserData(request):
    context={}
    try:
        token = request.COOKIES.get('token', None)
        if token!=None:
            try:
                payload = jwt.decode(token, settings.TOKEN_KEY, algorithms=settings.JWT_ALGORITHM)
                context['user']=payload
                context['user'].update({'access':payload['access'].split(';')})
                context['all_permissions']=employee_access.keys()
            except:
                pass
    except Exception as e:
        print(f':::: Error occured ::::\nfile path: {__file__}, loadUserdata() \n Error desc: {str(e)}')
    return context


def loadNotifications(request):
    context={}
    try:
        user_id=loadUserData(request)['user']['id']
        newnotifications=Notifications.objects.filter(notification_to=user_id,notification_status=1).order_by('-created_at').all()
        context['newnotifications']=newnotifications[:5]
        context['total_newnotifications']=len(newnotifications)
        return context
    except (KeyError,IndexError):
        return context
    except Exception as e:
        print(f':::: Error occured ::::\nfile path: {__file__}, loadUserdata() \n Error desc: {str(e)}')
    return context



def loadSiteData(request):
    context={}
    context['home_details']=Home_Details.objects.get()
    context['view_category']=category.objects.all()
    return context
