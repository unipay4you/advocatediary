from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management import call_command
from rest_framework.permissions import AllowAny
from django.http import FileResponse
from v1.models import *
from api.utils import *
from django.core.mail import EmailMessage

def daily_db_backup():
    print('Database backed up')
    call_command('dbbackup', clean=True)


@util.close_old_connections
def delete_old_job_executions(max_age = 604_800): # max age in seconds
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def generate_daily_pdf():
    try:
        today = datetime.now().date()
        print('generating daily pdf for date:', today)
        user_obj = CustomUser.objects.filter(is_active=True).order_by('id')
        if not user_obj.exists():
            print('No active users found for today')

        results = []    
        for user in user_obj:
            try:
                result = _extracted_from_generate_daily_pdf_6(user, today)
                results.append(f"{user.user_name}: Success")
            except Exception as e:
                results.append(f"{user.user_name}: Failed with error {str(e)}")

        print('Results:', results)        
        return 'PDF generation completed for all users.'
    except Exception as e:
        return f'Error: {str(e)}'


# TODO Rename this here and in `generate_daily_pdf`
def _extracted_from_generate_daily_pdf_6(user, today):
    print('Generating daily PDF for user:', user.user_name , 'phone number:', user.phone_number, 'Date :', today)
    if not user.is_active:
        print('User is not active:', user.user_name)
        
    
    user_name = user.user_name
    data_records = Case_Master.objects.filter(advocate__phone_number= user.phone_number, next_date = today)
    if not data_records.exists():
        print('No data records found for user:', user.user_name)
        
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10, leftMargin=10,
        topMargin=10, bottomMargin=10,
    )
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 9

    title_string = f"Daily Case Report for Advocate : {user_name} for {datetime.now().date().strftime('%d-%m-%Y')}"
    title = Paragraph(title_string, styles["Title"])
    elements = [title, Spacer(1, 12)]
    
    data = [[
        "S.No", "Case No", "Last Date", "Court", "Title", "Stage of Case", "Next Date"
    ]]
    
    
    data.extend(
        [
            str(i),
            f"{record.case_no} / {record.case_year}",
            (
                record.last_date.strftime("%d-%m-%Y")
                if record.last_date
                else ""
            ),
            Paragraph(record.court_name, normal_style),
            Paragraph(
                f"{record.petitioner} vs {record.respondent}", normal_style
            ),
            Paragraph(record.stage_of_case.stage_of_case, normal_style),
            (
                record.next_date.strftime("%d-%m-%Y")
                if record.next_date
                else ""
            ),
        ]
        for i, record in enumerate(data_records, start=1)
    )

    table = Table(data, colWidths=[40, 80, 70, 80, 280, 200, 80])
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
    buffer_name = f"daily_case_report_{user_name}.pdf"
    # OPTIONAL: Send email with PDF

    email = EmailMessage(
        'Daily Case Report',
        'Attached is your daily case report.',
        to=[user.email],
    )
    print('Sending email to:', user.email)
    # Attach the PDF file
    email.attach('daily_case_report.pdf', buffer.read(), 'application/pdf')
    email.send()
    print('Email sent successfully')
    print('PDF generated and emailed successfully.')
    

def  start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    scheduler.add_job(daily_db_backup, 'interval', hours=1,
                      jobstore='default',
                      id='daily_db_backup',
                      replace_existing=True)
    
    scheduler.add_job(delete_old_job_executions, 'interval', hours=23,
                      jobstore='default',
                      id='delete_old_job_executions',
                      replace_existing=True)
    
    
    scheduler.add_job(generate_daily_pdf, 'interval', minutes=2,
                      jobstore='default',
                      id='generate_daily_pdf',
                      replace_existing=True)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

