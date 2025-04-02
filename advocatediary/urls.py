
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .import api_views, appviews, advocate_views, staff_views, ecourt_views
from advocatediary.scheduler import scheduler

from rest_framework_simplejwt import views as jwt_views



urlpatterns = [
   
    path('admin/', admin.site.urls),

    path('base', appviews.base, name='base'),

    #login urls
    path('login', appviews.LOGIN, name='login'),
    path('', appviews.LOGIN, name='login'),
    path('logout_page', appviews.logout_page, name='logout_page'),
    path('register', appviews.REGISTER, name='register'),
    path('resend_otp', appviews.RESEND_OTP, name='resend_otp'),
    path('resend_email_link', appviews.resend_email_link, name='resend_email_link'),
    path('otp-verify', appviews.OTP_VERIFY, name='otp_verify'),
    path('verify/<email_token>', appviews.VERIFY, name='verify'),
    path('do_register', appviews.DO_REGISTER, name='do_register'),
    path('profile', appviews.PROFILE, name='profile'),
    path('profile-edit', appviews.PROFILE_EDIT, name='profile_edit'),
    path('get_district/', appviews.get_district, name="get_district"),
    path('get_court/', appviews.get_court, name="get_court"),
    path('add_new_district/', appviews.add_new_district, name="add_new_district"),
    path('add_new_court/', appviews.add_new_court, name="add_new_court"),
    path('delink-case/<id>/<returnURL>', appviews.DELINK_CASE, name='delink_case'),
    path('delete-client/<id>', appviews.DELETE_CLIENT, name='delete_client'), 
    path('update-date', appviews.UPDATE_DATE, name='update_date'), 
    path('casehistory/', appviews.CASE_HISTORY, name='casehistory'), 
    path('courttransfer/', appviews.COURT_TRANSFER, name='courttransfer'), 
    path('update_court', appviews.UPDATE_COURT, name='update_court'),
    path('case_closed/', appviews.CASE_CLOSED, name='case_closed'),
    path('case_closed_update', appviews.CASE_CLOSED_UPDATE, name='case_closed_update'),
    path('edit_client/', appviews.EDIT_CLIENT, name='edit_client'),
    path('edit_client_update', appviews.EDIT_CLIENT_UPDATE, name='edit_client_update'),

    #url for Advocate Login area
    path('advocate/adv-index', advocate_views.adv_index, name='adv_index'),
    path('advocate/newcase', advocate_views.NEWCASE, name='newcase'),
    path('advocate/case-edit/<id>', advocate_views.CASEEDIT, name='case_edit'),
    path('advocate/allclients', advocate_views.ALLCLIENTS, name='allclients'),
    path('advocate/case_client_associate/<id>', advocate_views.Case_Client_Associate, name='case_client_associate'),
    path('advocate/associate_client_and_add_more/', advocate_views.associate_client_and_add_more, name='associate_client_and_add_more'),
    path('advocate/offcanvas_body/', advocate_views.Offcanvas_Body, name='offcanvas_body'),
    path('advocate/client_case_viewmodal/', advocate_views.Client_Case_view_Modal, name='client_case_view_modal'),


    #url for API
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', api_views.RegisterUser.as_view()),
    path('api/otp-verify/', api_views.verifyOTP.as_view()),
    path('api/otp-resend/', api_views.resendOTP.as_view()),
    path('api/email-resend/', api_views.resendEmail.as_view()),
    path('api/changeemail/', api_views.ChangeEmail.as_view()),
    path('api/login/', api_views.Login.as_view()),
    path('api/getdistrict/', api_views.getDistrict.as_view()),
    path('api/user/', api_views.CaseView.as_view()),
    path('api/user/update/', api_views.UpdateUser.as_view()),
    path('api/case/stage/', api_views.StageOfCase.as_view()),
    path('api/case/history/', api_views.CaseHistoryView.as_view()),
    path('api/case/filter/', api_views.CaseViewFiltered.as_view()),

    path('api/case/dateupdate/', api_views.DateUpdateCase.as_view()),

    
    
    
    
    
    path('api/test', api_views.Case_API.as_view()),
    path('api/court', api_views.Court),
    

    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


scheduler.start()



