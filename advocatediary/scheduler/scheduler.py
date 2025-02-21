from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management import call_command



def daily_db_backup():
    print('Database backed up')
    call_command('dbbackup', clean=True)


@util.close_old_connections
def delete_old_job_executions(max_age = 2): # max age in seconds
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def  start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    scheduler.add_job(daily_db_backup, 'interval', minutes=180,
                      jobstore='default',
                      id='daily_db_backup',
                      replace_existing=True)
    
    scheduler.add_job(delete_old_job_executions, 'interval', minutes=180,
                      jobstore='default',
                      id='delete_old_job_executions',
                      replace_existing=True)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
    
