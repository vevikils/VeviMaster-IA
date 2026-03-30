from django.urls import path
from . import views

app_name = 'mastering'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('studio/', views.upload_audio, name='studio'),
    path('upload/', views.upload_audio, name='upload'), # Alias para compatibilidad
    path('download/<str:filename>/', views.download_master, name='download'),
    path('debug/media/', views.debug_media_files, name='debug_media'),
    path('checkout/create/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout/create-annual/', views.create_checkout_session_annual, name='create_checkout_session_annual'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('plans/', views.plans_page, name='plans'),
    path('claim-reward/', views.claim_social_reward, name='claim_reward'),
    path('analyze-pre-master/', views.analyze_pre_master, name='analyze_pre_master'),
    path('conversor/', views.converter_page, name='converter'),
    path('api/convert/', views.convert_audio_api, name='convert_audio_api'),
    path('api/post-review/', views.post_review, name='post_review'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_service, name='terms'),
    path('cookies/', views.cookie_policy, name='cookies'),
    path('studio-admin/users/', views.user_admin_list, name='user_admin_list'),
    path('studio-admin/users/toggle/<int:user_id>/', views.toggle_pro_status, name='toggle_pro_status'),
    
    # Blog URLs
    path('blog/', views.blog_index, name='blog_index'),
    path('blog/ai-mastering/', views.blog_post_ai, name='blog_post_ai'),
    path('blog/prepare-mix/', views.blog_post_prepare, name='blog_post_prepare'),
    path('blog/mix-vs-master/', views.blog_post_diff, name='blog_post_diff'),
    
    # Nuevas Rutas de "Cola Larga" (SEO Long-tail)
    path('blog/como-masterizar-base-trap-fl-studio/', views.blog_trap_fl_studio, name='blog_trap_fl_studio'),
    path('blog/mejor-configuracion-masterizar-reggaeton/', views.blog_masterizar_reggaeton, name='blog_masterizar_reggaeton'),
    path('blog/a-cuantos-lufs-masterizar-spotify-apple-music-youtube/', views.blog_lufs_spotify, name='blog_lufs_spotify'),
    path('blog/mejores-plugins-mastering-gratis-2026-alternativas-ozone/', views.blog_plugins_mastering, name='blog_plugins_mastering'),
    path('blog/como-hacer-mezcla-suene-ancha-profesional-imagen-estereo/', views.blog_imagen_estereo, name='blog_imagen_estereo'),
    path('blog/mastering-online-ia-vs-ingeniero-sonido-vale-pena/', views.blog_mastering_ia_vs_ingeniero, name='blog_mastering_ia_vs_ingeniero'),
]
