from django.urls import path
from . import views as v
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Users'

urlpatterns = [
    path('', v.home, name='home'),
    path('signup/', v.signup_view, name='signup'),
    path('login/', v.login_view, name='login'),
    path('logout/', v.logout_view, name='logout'),
    path('forgot_pass/', v.forgot_p, name='f_p'),
    path('create_pass/', v.create_pass, name='c_p'),
    path('otp/', v.otp_new_view, name='otp'),
    path('ration_card_details/', v.ration_card_view, name="add_ration_details"),
    path('profile/', v.profile_view, name='profile'),
    path("scan_rfid" , v.scan_rfid , name="scan_rfid"),
    path("dbt/" , v.dbt_dashboard , name="dbt"),
    path("fps_shop/" , v.fps_shop , name="fps_shop"),  
    path('ration-distribution/', v.ration_distribution_static_view, name='ration_distribution'),
    path('citizen/' , v.citizen , name='citizen'),
    path('yojana1/' , v.yojana1 , name='yojana1'),
    path('yojana2/' , v.yojana2 , name='yojana2'),
    path('yojana3/' , v.yojana3 , name='yojana3'),
    # RFID-related paths
    # path('rfid-ration/', v.rfid_ration_view, name='rfid-ration'),
    # path('wait-for-rfid/', v.wait_for_rfid, name='wait_for_rfid'),  # Ensure this view exists
    # path("check-rfid/", v.check_rfid, name="check_rfid"),    
    path('give-ration/', v.give_ration, name='give_ration'),  # Use a separate function
    path("register_fps/", v.register_fps, name="register_fps"),
    path("fps_login/", v.fps_login, name="fps_login"),
    # path("fps_login/", v.fps_login, name="fps_login"),
    path("fps_logout/", v.fps_logout, name="fps_logout"),
    path("fps_dashboard/", v.fps_dashboard, name="fps_dashboard"),
    path("chatbot/", v.chatbot, name="chatbot"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
