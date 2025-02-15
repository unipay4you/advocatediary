from v1.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

case_type = (
    (
        'Anticipatory Bail',
        'Bail Application',
        'Civil Suit',
        'Civil Appeal',
        'Civil Misc',
        'Civil Revision',
        'Arbitration',
        'Complaint',
        'Contempt',
        'Criminal Case',
        'Cr. Appeal',
        'Cr. Revision',
        'Cr. Misc',
        'DRA',
        'Execution',
        'Family Case',
        'Family Misc',
        'Final Report - FR',
        'Labour Case',
        'Labour Misc',
        'MACT Case',
        'MACT Misc',
        'Money Suit',
        'Rent Case',
        'Rent Appeal',
        'Session Case',
        'Sucession Certificate Case',
        'Misc'
    )
)

stage_of_case = (
    (
        'Report',
        'Arguments on Application',
        'Framing/Arguments of Charges',
        'Prosecution Evidence',
        'Final arguments',
        'Examination of accused u/s. 313 Cr.P.C',
        'Hearing on Admission',
        'Summons/Notice/bailable warrant',
        'Non-bailable warrant',
        'Arguments on Bail Applications',
        'Defence Evidence',
        'Orders',
        'Awaiting Order from Higher Court',
        'Compliance',
        'Appearance of accused',
        'Proclamation under Section 82-83 Cr.P.C',
        'Reply of Application',
        'Judgment',
        'Awaiting Report',
        'Stayed by Higher Court'
    )
)

def update_master():
    for item in case_type:
        Case_Type.objects.create(case_type = item)

    for item in stage_of_case:
        Case_Stage.objects.create(stage_of_case = item)
        