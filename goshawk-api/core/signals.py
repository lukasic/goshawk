from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django_redis import get_redis_connection

from core.models import Record

import uuid
import json

@receiver(post_save, sender=Record)
def notify_subscribers(sender, instance, **kwargs):
    print("notifying subscribers...")
    data = {
        'type': None,
        'exchange': instance.reporter.collection.acronym,
        'routing_key': instance.list.name,
        'record': {
            'pk': instance.pk,
            'value': instance.value,
            'policy': instance.policy,
            'expires_at': instance.expires_at,
            'active': instance.active
        }
    }

    if kwargs['created']:
        data['type'] = 'goshawk.record.created'
    else:
        data['type'] = 'goshawk.record.updated'

    msgid = str(uuid.uuid4())

    rclient = get_redis_connection('notifier')
    rclient.set(msgid, json.dumps(data))
    rclient.rpush("queue", msgid)

