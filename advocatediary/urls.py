
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .import api_views, appviews, advocate_views, staff_views, ecourt_views
from jcikotastar import views as JKS_views
from advocatediary.scheduler import scheduler

from rest_framework_simplejwt import views as jwt_views
from advocatediary import masteradmin_views

from paysprint import views as PS_views
from actbook import views as actbook_views



urlpatterns = [
   
    path('admin/', admin.site.urls),

    path('base', appviews.base, name='base'),

    #download urls for Apps
    path('legaldiary/download/', api_views.downloadapp.as_view(), name='download'),

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
    path('advocate/act/add/', advocate_views.act_add_view, name='newact'),
    path('advocate/act/add/chapter/', advocate_views.act_add_chapter, name='newchapter'),
    path('advocate/act/add/section/', advocate_views.act_add_section, name='newsection'),
    path('advocate/act/add/section/bulk/', advocate_views.act_add_section_bulk, name='newbulksection'),
    path('advocate/act/add/section/bulk2/', advocate_views.act_add_section_bulk2, name='newbulksection2'),


    #url for API
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', api_views.RegisterUser.as_view()),
    path('api/otp-verify/', api_views.verifyOTP.as_view()),
    path('api/otp-resend/', api_views.resendOTP.as_view()),
    path('api/email-resend/', api_views.resendEmail.as_view()),
    path('api/changeemail/', api_views.ChangeEmail.as_view()),
    path('api/login/', api_views.Login.as_view()),
    path('api/forgotpwd/', api_views.ForgatPassword.as_view()),
    path('api/otp-verify-changepwd/', api_views.verifyOTPChangepwd.as_view()),
    path('api/change-password/', api_views.ChangePassword.as_view()),
    
    
    
    
    path('api/user/', api_views.CaseView.as_view()),
    path('api/user/update/', api_views.UpdateUser.as_view()),
    
    path('api/case/history/', api_views.CaseHistoryView.as_view()),
    path('api/case/filter/', api_views.CaseViewFiltered.as_view()),
    path('api/case/add/', api_views.CaseAdd.as_view()),
    path('api/case/edit/', api_views.CaseEdit.as_view()),
    path('api/case/close/', api_views.CaseClosedView.as_view()),
    path('api/case/detail/', api_views.CaseViewDetailByID.as_view()),
    path('api/case/calenderdetail/', api_views.CaseViewDetailCalander.as_view()),

    path('api/case/dateupdate/', api_views.DateUpdateCase.as_view()),
    path('api/getcourt/update/', api_views.CourtUpdateView.as_view()),
    path('api/version/', api_views.getVersionView.as_view()),

    path('api/getcasetype/', api_views.getCaseType.as_view()),
    path('api/case/stage/', api_views.StageOfCase.as_view()),
    path('api/getcourttype/', api_views.getCourtType.as_view()),
    path('api/getdistrict/', api_views.getDistrict.as_view()),
    path('api/getcourt/', api_views.getCourt.as_view()),

    path('api/getall/', api_views.AddCaseApisViews.as_view()),

    
    
    
    path('api/pdf/', api_views.DataPDFView.as_view(), name='data-pdf'),
   

    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('api/models-changed/', api_views.PerModelChangeStatusView.as_view()),
    




#jcikotastar urls
    path('jks/api/auth/login/', JKS_views.LoginView.as_view(), name='token_obtain_pair'),     #
    path('jks/api/auth/verify-otp/', JKS_views.verifyOTP.as_view(), name='token_obtain_pair'),  #
    path('jks/api/auth/resend-otp/', JKS_views.resendOTP.as_view(), name='token_obtain_pair'),  #
    path('jks/api/auth/reset-password/', JKS_views.ChangePassword.as_view(), name='token_obtain_pair'),     #
    path('jks/api/auth/user/', JKS_views.UserView.as_view(), name='token_obtain_pair'), #
    path('jks/api/auth/forgat-password/', JKS_views.ForgatPassword.as_view(), name='token_obtain_pair'),    #
    path('jks/api/auth/verify-forgat-password-otp/', JKS_views.verifyForgatePasswordOTP.as_view(), name='token_obtain_pair'), #


    path('jks/api/admin/addmember/', JKS_views.AddNewMembter.as_view()), #
    path('jks/api/admin/dashboard/', JKS_views.AdminDashboardView.as_view()),   #
    path('jks/api/admin/members/change-status/', JKS_views.MembterChangeStatusView.as_view()), #
    path('jks/api/admin/members/update/', JKS_views.UpdateMembterProfileViewFromAdmin.as_view()),
    path('jks/api/admin/members/list/', JKS_views.AdminMemberListView.as_view()), #
    path('jks/api/admin/members/update-post/', JKS_views.MembterUpdatePostView.as_view()),  #
    path('jks/api/admin/members/make-admin/', JKS_views.MakeAdminView.as_view()), #

    path('jks/api/admin/programs/', JKS_views.AdminProgramView.as_view()),  #
    path('jks/api/admin/members/programs/add/', JKS_views.ProgramAddView.as_view()),  #
    path('jks/api/admin/members/programs/update/', JKS_views.ProgramEditView.as_view()),  #

    path('jks/api/user/profile/', JKS_views.UserProfileView.as_view()), #
    path('jks/api/user/update-profile/', JKS_views.UpdateProfile.as_view()),    #
    path('jks/api/user/greeting-cards/', JKS_views.GreetingCardsView.as_view()),
    path('jks/api/user/greeting-cards/add/', JKS_views.AddGreetingCardsView.as_view()),


    path('jks/api/programs/', JKS_views.MembersProgramView.as_view()),
    

    path('jks/api/program-images/', JKS_views.ProgramImagesView.as_view()), #
    path('jks/api/program-images/program-id/', JKS_views.ProgramImagesByProgramIDView.as_view()),
    path('jks/api/program-images/upload/', JKS_views.ImageUploadView.as_view()),    #






#urls for supperadmin
    path('api/superadmin/dashboard/', masteradmin_views.SuperAdminDashboardView.as_view()),
    path('api/superadmin/verify-otp/', masteradmin_views.SuperAdminVerifyOTPView.as_view()), 
    path('api/superadmin/verify-email/', masteradmin_views.SuperAdminVerifyEmailView.as_view()), 
    path('api/superadmin/toggle-status/', masteradmin_views.SuperAdminToggleStatusView.as_view()),
    path('api/superadmin/reset-password/', masteradmin_views.SuperAdminResetPasswordView.as_view()), 
    path('api/superadmin/courts/', masteradmin_views.SuperAdminCourtView.as_view()),
    path('api/superadmin/courts/add/', masteradmin_views.SuperAdminCourtAddView.as_view()), 



    #urls for actbook
    path('api/actbook/add/', actbook_views.Add_ActBookView.as_view(), name='actbookadd'),
    path('api/actbook/', actbook_views.ActBookView.as_view(), name='actbook'),
    path('api/actbook/chapter/', actbook_views.ActBookChapterView.as_view(), name='chapter'),
    path('api/actbook/section/', actbook_views.ActBookSectionView.as_view(), name='section'),
    path('api/actbook/similar-section/', actbook_views.SimilarSectionView.as_view(), name='similarsection'),
    path('api/actbook/similar-section/add/', actbook_views.SimilarSectionAddView.as_view(), name='SimilarSectionAddView'),






#urls for Paysprint
    path('paysprint/api/test/', PS_views.TestView.as_view(), name='bbps_login'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


scheduler.start()



