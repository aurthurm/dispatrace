from django.db.models.signals import post_save
from django.shortcuts import render, get_object_or_404

from fuel.models import Fuel
from notify.signals import notify

def send_notifications(instance, sender, **kwargs):
    fuel = instance
    if kwargs['created']:
        print(fuel.approver)
        if fuel.approver is not None:
            notify.send(
                fuel.requester, 
                recipient=fuel.approver, 
                actor=fuel.requester,
                verb='has requested fuel',
                target=fuel, 
                nf_type='fuel_request_sent'
            )
        if fuel.assessor is not None:
            notify.send(
                fuel.requester, 
                recipient=fuel.assessor, 
                actor=fuel.requester,
                verb='has requested fuel',
                target=fuel, 
                nf_type='fuel_request_sent'
            )

post_save.connect(send_notifications, sender=Fuel)

