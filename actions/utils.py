from .models import SingleAction, AggregateAction
from datetime import *
from django.conf import settings
import redis

# track user function that saves single activities to Redis and then aggregate them in the main database
def create_action(user, verb, target=None):

    r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

    dt = datetime.now()
    delta = timedelta(hours=1)
    next_hour = (dt + delta).replace(microsecond=0, second=1)
    wait_seconds = (next_hour - dt).seconds

    action = SingleAction(user=user, verb=verb, target=target)
    r.lpush(f'last_actions_{action.user}', f'{dt.strftime("%m/%d/%Y, %H:%M:%S")} - {action.user} {action.verb}')
    r.expire(f'last_actions_{action.user}', wait_seconds)

    n = r.llen(f'last_actions_{action.user}')
    user_actions = AggregateAction.objects.filter(user=action.user, created=f'{dt.strftime("%m/%d/%Y")} - from {dt.strftime("%H")} to {next_hour.strftime("%H")}')
    if user_actions.exists():
        AggregateAction.objects.filter(user=action.user).update(n_actions=n)
    else:
        AggregateAction.objects.create(user=action.user,
                                       n_actions=n,
                                       created=f'{dt.strftime("%m/%d/%Y")} - from {dt.strftime("%H")} to {next_hour.strftime("%H")}')
