
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views, advocate_views, admin_views, staff_views, ecourt_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('base', views.base, name='base'),

    #login urls
    path('login', views.LOGIN, name='login'),
    path('', views.LOGIN, name='login'),
    path('logout_page', views.logout_page, name='logout_page'),
    path('register', views.REGISTER, name='register'),
    path('resend_otp', views.RESEND_OTP, name='resend_otp'),
    path('resend_email_link', views.resend_email_link, name='resend_email_link'),
    path('otp-verify', views.OTP_VERIFY, name='otp_verify'),
    path('verify/<email_token>', views.VERIFY, name='verify'),
    path('do_register', views.DO_REGISTER, name='do_register'),
    path('profile', views.PROFILE, name='profile'),
    path('profile-edit', views.PROFILE_EDIT, name='profile_edit'),
    path('get_district/', views.get_district, name="get_district"),
    path('get_court/', views.get_court, name="get_court"),
    path('add_new_district/', views.add_new_district, name="add_new_district"),
    path('add_new_court/', views.add_new_court, name="add_new_court"),
    path('delink-case/<id>/<returnURL>', views.DELINK_CASE, name='delink_case'),
    path('delete-client/<id>', views.DELETE_CLIENT, name='delete_client'), 
    path('update-date', views.UPDATE_DATE, name='update_date'), 
    path('casehistory/', views.CASE_HISTORY, name='casehistory'), 
    path('courttransfer/', views.COURT_TRANSFER, name='courttransfer'), 
    path('update_court', views.UPDATE_COURT, name='update_court'),
    path('case_closed/', views.CASE_CLOSED, name='case_closed'),
    path('case_closed_update', views.CASE_CLOSED_UPDATE, name='case_closed_update'),

    #url for Advocate Login area
    path('advocate/adv-index', advocate_views.adv_index, name='adv_index'),
    path('advocate/newcase', advocate_views.NEWCASE, name='newcase'),
    path('advocate/allclients', advocate_views.ALLCLIENTS, name='allclients'),
    path('advocate/case_client_associate', advocate_views.Case_Client_Associate, name='case_client_associate'),
    path('advocate/associate_client_and_add_more/', advocate_views.associate_client_and_add_more, name='associate_client_and_add_more'),
    path('advocate/offcanvas_body/', advocate_views.Offcanvas_Body, name='offcanvas_body'),
    path('advocate/client_case_viewmodal/', advocate_views.Client_Case_view_Modal, name='client_case_view_modal'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



