import random
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO



def send_msg_to_mobile(mobile, otp, msg):
    try:
        print(msg)
    except Exception as e:
        print(e)
    


def send_email_token(email, email_token):
    try:
        address = [email,]
        subject = 'Your Account need to be verified'
        message = f'Click on the link to verify your email {settings.HOST_URL}/verify/{email_token}'
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
        
    
    except Exception as e:
        print(e)

def send_email_password(email, password):
    try:
        address = [email,]
        subject = 'Your Password has been reset'
        message = f'Your new password is {password}'
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
        
    
    except Exception as e:
        print(e)

def send_email_otp(email, email_otp, message):
    try:
        address = [email,]
        subject = 'Your Account need to be verified'
        print(message)
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
        
    
    except Exception as e:
        print(e)  

def generate_otp():
    #return random.randint(100000, 999999) # for production
    return 123456 # for testing purpose


def generate_pdf(data_queryset, user):
    buffer = BytesIO()

    # Set tight margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10,
        leftMargin=10,
        topMargin=10,
        bottomMargin=10,
    )

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 9  # Slightly reduced font size for better fit

    # Title
    title_string = f"Daily Case Report for Advocate : {user} for {datetime.now().date().strftime("%d-%m-%Y")}"
    title = Paragraph(title_string, styles["Title"])
    elements = [title, Spacer(1, 12)]
    # Table header
    data = [[
        "S.No", "Case No", "Last Date", "Court", "Title", "Stage of Case", "Next Date"
    ]]

    # Table data with Paragraph for text wrapping
    data.extend(
        [
            str(i),
            f"{record.case_no} / {record.case_year}",
            record.last_date.strftime("%d-%m-%Y") if record.last_date else "",
            Paragraph(record.court_name, normal_style),
            Paragraph(
                f"{record.petitioner} vs {record.respondent}", normal_style
            ),
            Paragraph(record.stage_of_case.stage_of_case, normal_style),
        ]
        for i, record in enumerate(data_queryset, start=1)
    )
    # Total width in landscape A4 is 842 points
    column_widths = [40, 80, 70, 80, 280, 200, 80]  # Total = 830, fits well

    table = Table(data, colWidths=column_widths)

    # Styling
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def send_email_password(email, password):
    try:
        address = [email,]
        subject = 'Your Password has been reset'
        message = f'Your new password is {password}'
        obj = send_mail(subject, message, settings.EMAIL_HOST_USER, address)
        print('Mail send successfull')
        
    
    except Exception as e:
        print(e)
