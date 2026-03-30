import os
import shutil
import uuid
import subprocess
import json
import logging
import math
from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from .utils import analyze_audio_metrics, analyze_spectrum, convert_to_wav
from .models import UserSettings, Review
from .analytics_utils import get_google_analytics_stats
from django.contrib.auth import get_user_model
User = get_user_model()

import stripe
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    """Create a Stripe Checkout Session for the Pro plan."""
    try:
        success_url = request.build_absolute_uri(reverse('mastering:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.build_absolute_uri(reverse('mastering:payment_cancel'))
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': settings.STRIPE_PRICE_ID_PRO,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=request.user.email,
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

    return redirect(checkout_session.url, code=303)

@login_required
def create_checkout_session_annual(request):
    """Create a Stripe Checkout Session for the Annual Pro plan."""
    try:
        success_url = request.build_absolute_uri(reverse('mastering:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.build_absolute_uri(reverse('mastering:payment_cancel'))
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID_ANNUAL,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=request.user.email,
        )
    except Exception as e:
        logger.error(f"Error creating annual checkout session: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

    return redirect(checkout_session.url, code=303)


@login_required
def payment_success(request):
    """Payment success page. Checks session to activate Pro status immediately."""
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                customer_email = session.customer_details.email
                # Activar Pro para el usuario actual o el del email
                target_user = request.user if request.user.is_authenticated else User.objects.get(email=customer_email)
                user_settings, _ = UserSettings.objects.get_or_create(user=target_user)
                if not user_settings.is_pro:
                    user_settings.is_pro = True
                    user_settings.save()
                    messages.success(request, "¡Tu suscripción Pro ha sido activada! Disfruta de masterizaciones ilimitadas.")
        except Exception as e:
            logger.error(f"Error verifies success session: {e}")
            
    return render(request, 'mastering/payment_success.html')

def payment_cancel(request):
    """Payment cancel page."""
    return render(request, 'mastering/payment_cancel.html')

@csrf_exempt
def stripe_webhook(request):
    """
    Webhook para manejar eventos de suscripción de Stripe.
    Mantiene sincronizado el estado 'is_pro' del usuario.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
        if customer_email:
            try:
                user = User.objects.get(email=customer_email)
                user_settings, _ = UserSettings.objects.get_or_create(user=user)
                user_settings.is_pro = True
                user_settings.save()
                logger.info(f"Pro status activated for {customer_email} via webhook.")
            except User.DoesNotExist:
                logger.error(f"User with email {customer_email} not found during webhook.")

    elif event['type'] == 'customer.subscription.deleted':
        # Suscripción cancelada o terminada
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        # Buscamos al usuario por el email de Stripe
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.get('email')
        if customer_email:
            try:
                user = User.objects.get(email=customer_email)
                user_settings, _ = UserSettings.objects.get_or_create(user=user)
                user_settings.is_pro = False
                user_settings.save()
                logger.info(f"Pro status deactivated for {customer_email} (subscription deleted).")
            except User.DoesNotExist:
                pass

    elif event['type'] == 'invoice.payment_failed':
        # Pago fallido
        invoice = event['data']['object']
        customer_email = invoice.get('customer_email')
        if customer_email:
            try:
                user = User.objects.get(email=customer_email)
                user_settings, _ = UserSettings.objects.get_or_create(user=user)
                user_settings.is_pro = False
                user_settings.save()
                logger.info(f"Pro status deactivated for {customer_email} (payment failed).")
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)


@csrf_exempt
def landing_page(request):
    """Muestra la página de inicio con reseñas reales."""
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:6]
    return render(request, 'mastering/landing.html', {'reviews': reviews})

@login_required
@csrf_exempt
def post_review(request):
    """Permite a usuarios registrados postear una reseña si han masterizado al menos 1 tema."""
    if request.method == 'POST':
        content = request.POST.get('content')
        rating = int(request.POST.get('rating', 5))
        
        try:
            settings = UserSettings.objects.get(user=request.user)
            if settings.mastered_tracks_total < 1:
                return JsonResponse({'error': 'Debes masterizar al menos una canción antes de dejar una reseña.'}, status=403)
            
            Review.objects.create(
                user=request.user,
                content=content,
                rating=rating
            )
            return JsonResponse({'success': '¡Gracias por tu reseña!'})
        except UserSettings.DoesNotExist:
            return JsonResponse({'error': 'No se encontraron ajustes de usuario.'}, status=404)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def blog_index(request):
    """Blog index page."""
    return render(request, 'mastering/blog/index.html')

def blog_post_ai(request):
    """Blog post: What is AI Mastering."""
    return render(request, 'mastering/blog/what_is_ai_mastering.html')

def blog_post_prepare(request):
    """Blog post: Prepare mix."""
    return render(request, 'mastering/blog/prepare_mix.html')

def blog_post_diff(request):
    """Blog post: Mix vs Master."""
    return render(request, 'mastering/blog/mix_vs_master.html')

def blog_trap_fl_studio(request):
    """Blog post: Trap FL Studio SEO Long-tail."""
    return render(request, 'mastering/blog/trap_fl_studio.html')

def blog_masterizar_reggaeton(request):
    """Blog post: Reggaeton settings SEO Long-tail."""
    return render(request, 'mastering/blog/masterizar_reggaeton.html')

def blog_lufs_spotify(request):
    """Blog post: LUFS for Spotify 2026."""
    return render(request, 'mastering/blog/lufs_spotify.html')

def blog_plugins_mastering(request):
    """Blog post: Free Mastering Plugins Alternatives to Ozone."""
    return render(request, 'mastering/blog/plugins_mastering.html')

def blog_imagen_estereo(request):
    """Blog post: How to make mix sound wider (Stereo Image)."""
    return render(request, 'mastering/blog/imagen_estereo.html')

def blog_mastering_ia_vs_ingeniero(request):
    """Blog post: AI Mastering vs Human Sound Engineer."""
    return render(request, 'mastering/blog/ia_vs_ingeniero.html')
def about_page(request):
    """About us page."""
    return render(request, 'mastering/about.html')

def contact_page(request):
    """Contact page."""
    return render(request, 'mastering/contact.html')

def privacy_policy(request):
    """Privacy Policy page."""
    return render(request, 'mastering/privacy_policy.html')

def terms_of_service(request):
    """Terms of Service page."""
    return render(request, 'mastering/terms_of_service.html')

def cookie_policy(request):
    """Cookie Policy page."""
    return render(request, 'mastering/cookie_policy.html')

@login_required
def plans_page(request):
    """View for pricing plans."""
    return render(request, 'mastering/plans.html')

@login_required
def claim_social_reward(request):
    """Claim +3 extra masterings."""
    if request.method == 'POST':
        try:
            from .models import UserSettings
            user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
            if not user_settings.social_reward_claimed:
                user_settings.social_reward_claimed = True
                user_settings.extra_credits = 3
                user_settings.save()
                messages.success(request, "¡Recompensa reclamada! Tienes 3 masterizaciones extra.")
            else:
                messages.warning(request, "Ya has reclamado esta recompensa.")
        except Exception as e:
            logger.error(f"Error claiming reward: {e}")
    return redirect('mastering:plans')
    
@login_required
def converter_page(request):
    """Muestra la página del conversor de audio."""
    return render(request, 'mastering/converter.html')

@login_required
@csrf_exempt
def convert_audio_api(request):
    """API para convertir archivos entre MP3 y WAV."""
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        target_format = request.POST.get('format', 'wav').lower()
        
        # Soportamos múltiples formatos
        if target_format not in ['wav', 'mp3', 'flac', 'mpeg']:
            return JsonResponse({'error': 'Formato no soportado'}, status=400)
            
        ext = audio_file.name.lower().split('.')[-1]
        temp_input = os.path.join(settings.MEDIA_ROOT, f'conv_in_{uuid.uuid4()}.{ext}')
        temp_output = os.path.join(settings.MEDIA_ROOT, f'conv_out_{uuid.uuid4()}.{target_format}')
        
        try:
            with open(temp_input, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # Conversion logic universal
            if target_format == ext and ext != 'mp3' and ext != 'wav':
                # Si es el mismo y no es comun, simplemente copiarlo
                shutil.copy(temp_input, temp_output)
            elif target_format == 'wav':
                convert_to_wav(temp_input, temp_output)
            elif target_format == 'mp3':
                cmd = ['ffmpeg', '-y', '-i', temp_input, '-codec:a', 'libmp3lame', '-qscale:a', '2', temp_output]
                subprocess.run(cmd, capture_output=True, check=True)
            elif target_format == 'flac':
                cmd = ['ffmpeg', '-y', '-i', temp_input, '-c:a', 'flac', temp_output]
                subprocess.run(cmd, capture_output=True, check=True)
            elif target_format == 'mpeg':
                # Force mpeg format output
                cmd = ['ffmpeg', '-y', '-i', temp_input, '-f', 'mpeg', '-c:a', 'libmp3lame', temp_output]
                subprocess.run(cmd, capture_output=True, check=True)

            # Return the file
            with open(temp_output, 'rb') as f:
                response = HttpResponse(f.read(), content_type=f'audio/{target_format}')
                response['Content-Disposition'] = f'attachment; filename="converted_{audio_file.name.rsplit(".", 1)[0]}.{target_format}"'
                
                # Cleanup
                os.remove(temp_input)
                os.remove(temp_output)
                
                return response
        except Exception as e:
            logger.error(f"Error in conversion API: {e}")
            if os.path.exists(temp_input): os.remove(temp_input)
            if os.path.exists(temp_output): os.remove(temp_output)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def analyze_pre_master(request):
    """
    Analiza un archivo de audio antes de masterizar para mostrar estadísticas al usuario.
    """
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        ext = audio_file.name.lower().split('.')[-1]
        if ext not in ['wav', 'mp3']:
            return JsonResponse({'error': 'Solo se aceptan archivos WAV o MP3.'}, status=400)

        # Ensure MEDIA_ROOT exists
        if not os.path.exists(settings.MEDIA_ROOT):
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            except Exception as e:
                logger.error(f"Cannot create MEDIA_ROOT: {settings.MEDIA_ROOT} - {e}")
                return JsonResponse({'error': f'Error de permisos en el servidor: {str(e)}'}, status=500)

        # Save temporarily
        temp_filename = f'pre_analyze_{uuid.uuid4()}.{ext}'
        temp_path = os.path.join(settings.MEDIA_ROOT, temp_filename)
        
        try:
            with open(temp_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # If MP3, convert to WAV for analysis
            analysis_path = temp_path
            if ext == 'mp3':
                try:
                    wav_temp_path = temp_path.replace('.mp3', '.wav')
                    convert_to_wav(temp_path, wav_temp_path)
                    analysis_path = wav_temp_path
                except Exception as e:
                    logger.error(f"Conversion error: {e}")
                    if os.path.exists(temp_path): os.remove(temp_path)
                    return JsonResponse({'error': 'Error al convertir MP3 para análisis.'}, status=500)
                
            # Analyze
            metrics = analyze_audio_metrics(analysis_path)
            
            # Clean up
            if os.path.exists(temp_path): os.remove(temp_path)
            if ext == 'mp3' and os.path.exists(analysis_path): os.remove(analysis_path)
            
            return JsonResponse(metrics)
        except Exception as e:
            logger.error(f"Error in pre-master analysis: {e}")
            if os.path.exists(temp_path): os.remove(temp_path)
            return JsonResponse({'error': f'Error técnico: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Petición inválida'}, status=400)

@login_required
@csrf_exempt
def upload_audio(request):
    """Handle audio upload with plan limits."""
    # Check limits
    try:
        from .models import UserSettings
        from django.utils import timezone
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        
        # Admin account gets unlimited credits
        is_admin = request.user.email in ['vevikils556@gmail.com', 'vevimasteria@gmail.com'] or request.user.is_superuser
        
        # Reset count if new month (basic implementation)
        if user_settings.last_reset_date.month != timezone.now().month:
             user_settings.monthly_masterings_count = 0
             user_settings.last_reset_date = timezone.now()
             user_settings.save()

        # Skip limit check for admin
        if not is_admin and not user_settings.is_pro:
            limit = 1 + user_settings.extra_credits
            if user_settings.monthly_masterings_count >= limit:
                return redirect('mastering:plans')
                
    except Exception as e:
        logger.warning(f"Limit check skipped due to DB error (migration needed?): {e}")

    """Handle audio upload, run PhaseLimiter and return metrics before/after."""
    if request.method == 'POST' and request.FILES.get('audio'):
        
        # Increment count on successful upload attempt (skip for admin)
        try:
            if 'user_settings' in locals() and 'is_admin' in locals():
                if not is_admin and not user_settings.is_pro:
                    user_settings.monthly_masterings_count += 1
                user_settings.mastered_tracks_total += 1
                user_settings.save()
        except:
            pass

        audio_file = request.FILES['audio']
        ext = audio_file.name.lower().split('.')[-1]
        if ext not in ['wav', 'mp3']:
            return HttpResponse('Solo se aceptan archivos WAV o MP3.', status=400)

        # Helper to get parameters with defaults
        def get_param(name, default, cast):
            val = request.POST.get(name)
            try:
                return cast(val) if val is not None else default
            except Exception:
                return default

        # Handle Presets
        preset = request.POST.get('preset', 'normal')
        preset_values = {
            'normal': {'loudness': -14, 'dynamics': 2.5, 'sharpness': 2.2, 'space': -3},
            'rock': {'loudness': -11, 'dynamics': 3.5, 'sharpness': 3.0, 'space': -2},
            'trap': {'loudness': -9, 'dynamics': 1.8, 'sharpness': 4.5, 'space': -1},
            'drill': {'loudness': -8.5, 'dynamics': 1.5, 'sharpness': 5.0, 'space': -1},
            'reggaeton': {'loudness': -10, 'dynamics': 2.2, 'sharpness': 3.5, 'space': -1.5},
            'rap': {'loudness': -10.5, 'dynamics': 2.5, 'sharpness': 2.8, 'space': -2},
            'pop': {'loudness': -12, 'dynamics': 3.0, 'sharpness': 3.2, 'space': -1},
            'hyperpop': {'loudness': -8, 'dynamics': 1.2, 'sharpness': 6.5, 'space': 0},
        }
        
        selected_preset = preset_values.get(preset, preset_values['normal'])
        
        # Override loudness only if it was at default -14? 
        # Actually user sliders should take precedence if they moved them.
        # But since we don't have a way to know if they moved them easily here without JS support,
        # we only use preset if explicitly selected and sliders are roughly at default.
        # For now, let's keep it simple: sliders ARE the truth, but we use preset to define 'reference' context.

        # Global mastering parameters – PhaseLimiter uses 'reference' (target LUFS) and 'reference_mode'
        global_params = {
            'reference': get_param('loudness', selected_preset['loudness'], float),
            'reference_mode': 'loudness',
            'loudness_range': get_param('loudness_range', 6, float),
            'peak': get_param('peak', 0.98, float),
            'rms': get_param('rms', -10, float),
            'dynamics': get_param('dynamics', selected_preset['dynamics'], float),
            'sharpness': get_param('sharpness', selected_preset['sharpness'], float),
            'space': get_param('space', selected_preset['space'], float),
            'drr': get_param('drr', 12, float),
            'sample_rate': get_param('sample_rate', 44100, int),
            'channels': get_param('channels', 2, int),
        }

        # Band parameters (4 bands)
        bands = []
        for i in range(4):
            band = {
                'low_freq': get_param(f'band_{i}_low_freq', 20, float),
                'high_freq': get_param(f'band_{i}_high_freq', 20000, float),
                'loudness': get_param(f'band_{i}_loudness', -18, float),
                'loudness_range': get_param(f'band_{i}_loudness_range', 6, float),
                'mid_mean': get_param(f'band_{i}_mid_mean', -15, float),
                'mid_to_side_loudness': get_param(f'band_{i}_mid_to_side_loudness', -10, float),
                'mid_to_side_loudness_range': get_param(f'band_{i}_mid_to_side_loudness_range', 10, float),
                'side_mean': get_param(f'band_{i}_side_mean', -20, float),
            }
            bands.append(band)

        # Build configuration JSON (PhaseLimiter expects specific keys)
        config = {
            **global_params,
            'bands': bands,
            # PhaseLimiter specific flag – will be filled with the path below
            'mastering5_mastering_reference_file': None,
            'mastering5_mastering_level': 0.5,
            'mastering5_optimization_algorithm': 'de_prmm',
            'mastering5_optimization_max_eval_count': 40000,
        }
        # Save JSON and set the reference file path
        config_path = os.path.join(settings.MEDIA_ROOT, f'{uuid.uuid4()}_mastering_config.json')
        config['mastering5_mastering_reference_file'] = config_path
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Mastering configuration saved to {config_path}")

        # Save uploaded file temporarily
        input_filename = f'{uuid.uuid4()}.{ext}'
        input_path = os.path.join(settings.MEDIA_ROOT, input_filename)
        with open(input_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # If MP3, convert to WAV before processing
        processing_input_path = input_path
        if ext == 'mp3':
            wav_input_path = input_path.replace('.mp3', '.wav')
            convert_to_wav(input_path, wav_input_path)
            processing_input_path = wav_input_path
            # Optional: remove original mp3 to save space
            # os.remove(input_path)
            input_path = processing_input_path


        # Analyze before mastering
        metrics_before = analyze_audio_metrics(input_path)
        spectrum_before = analyze_spectrum(input_path)


        # Prepare PhaseLimiter execution
        base_name = os.path.splitext(audio_file.name)[0]
        output_filename = f'{base_name}_vevi_master_ia.wav'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        BASE_DIR = settings.BASE_DIR
        bin_dir = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin')
        exe_path = os.path.join(bin_dir, 'phase_limiter')

        # Ensure executable permission on Linux
        if os.name != 'nt':
            try:
                import stat
                st = os.stat(exe_path)
                os.chmod(exe_path, st.st_mode | stat.S_IEXEC)
            except Exception:
                pass

        env = os.environ.copy()
        env['PATH'] = bin_dir + os.pathsep + env['PATH']
        # Use /tmp for the initial output to avoid 'Invalid cross-device link' in Docker
        temp_output_filename = f'temp_master_{uuid.uuid4()}.wav'
        temp_output_path = os.path.join('/tmp', temp_output_filename)

        cmd = [
            exe_path,
            f'-input={input_path}',
            f'-output={temp_output_path}',
            f'-mastering5_mastering_reference_file={config_path}',
            f'-reference={global_params["reference"]}',
            f'-reference_mode={global_params["reference_mode"]}',
            f'-mastering5_mastering_level=5.0',
        ]
        # Run PhaseLimiter with detailed logging
        logger.info("MASTERING ENGINE VERSION: 3.0 (PRO PEAK FIX)")
        logger.info(f"Executing PhaseLimiter command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=BASE_DIR, env=env)
        logger.info(f"PhaseLimiter STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"PhaseLimiter STDERR:\n{result.stderr}")
        if result.returncode != 0:
            return HttpResponse(f'Error en PhaseLimiter:<br><pre>{result.stderr}</pre>', status=500)
        if os.path.exists(temp_output_path):
            # Paso intermedio: Aplicar EQ correctivo post-mastering
            # Reducir brillo: -1.5dB entre 2000Hz y 8000Hz
            # Usaremos un filtro equalizador paramétrico centrado en 4000Hz con un ancho (Q) aproximado de 1.0
            
            non_eq_path = os.path.join(settings.MEDIA_ROOT, f'pre_eq_{uuid.uuid4()}.wav')
            shutil.move(temp_output_path, non_eq_path)
            
            # Professional Mastering Chain: Density (Compand) -> Precision Volume (Loudnorm) -> Final Wall (Limiter)
            # This combination ensures we hit exactly -12 LUFS while pushing peaks to the ceiling.
            target_lufs = global_params['reference']
            peak_linear = global_params['peak'] # ej 0.98 (~ -0.17dB)
            
            # Metadata for precision
            measured_i = metrics_before.get('lufs', -24.0)
            measured_tp = metrics_before.get('peak', -1.0)
            measured_lra = metrics_before.get('lra', 12.0)
            measured_thresh = metrics_before.get('threshold', -34.0)
            
            # MASTERING V4.3 (PRO POWER CHAIN): 
            # 1. EQ Correctivo
            # 2. Compand Agresivo (Densidad)
            # 3. Loudnorm (Fijar volumen a -12 LUFS)
            # 4. Alimiter con Push masivo (Garantiza picos en la cima)
            af_filters = [
                f'equalizer=f=4000:width_type=o:width=1.5:g=-1.5',
                f'compand=0.01|0.01:0.02|0.02:-90/-90/-70/-60/-20/-9/-5/-1/0/0:4:0:-90:0.02',
                f'loudnorm=I={target_lufs}:TP=-0.5:LRA=12', 
                f'alimiter=level_in=10.0:level_out=1.0:limit={peak_linear}:attack=1.5:release=100:type=inst'
            ]
            
            cmd_eq = [
                'ffmpeg',
                '-y',
                '-i', non_eq_path,
                '-af', ','.join(af_filters),
                output_path
            ]
            
            logger.info(f"EXECUTING V3 POWER CHAIN: {' '.join(cmd_eq)}")
            
            logger.info(f"Applying corrective EQ: {' '.join(cmd_eq)}")
            result_eq = subprocess.run(cmd_eq, capture_output=True, text=True)
            
            if result_eq.returncode != 0:
                logger.error(f"EQ Failed: {result_eq.stderr}")
                # Fallback to non-EQ version if ffmpeg fails
                shutil.move(non_eq_path, output_path)
            else:
                # Clean up intermediate file
                try:
                    os.remove(non_eq_path)
                except:
                    pass
        else:
            return HttpResponse('Error: PhaseLimiter no generó el archivo de salida esperado.', status=500)

        # Analyze after mastering
        metrics_after = analyze_audio_metrics(output_path)
        spectrum_after = analyze_spectrum(output_path)

        context = {
            'metrics_before': metrics_before,
            'metrics_after': metrics_after,
            'spectrum_before_json': json.dumps(spectrum_before),
            'spectrum_after_json': json.dumps(spectrum_after),
            'output_filename': output_filename,
            'input_filename': input_filename,  # Pass the saved input filename for playback
            'original_filename': audio_file.name,
            'engine_used': 'PhaseLimiter',
            'MEDIA_URL': settings.MEDIA_URL,  # Explicitly pass MEDIA_URL
        }
        return render(request, 'mastering/results.html', context)
    # GET request – render upload form
    return render(request, 'mastering/upload.html')

@login_required
def download_master(request, filename):
    """Vista para descargar el archivo masterizado."""
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("El archivo no existe.")

def debug_media_files(request):
    """Debug view to list all files in media directory."""
    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL
    
    html = f"<h1>Media Files Debug</h1>"
    html += f"<p><strong>MEDIA_ROOT:</strong> {media_root}</p>"
    html += f"<p><strong>MEDIA_URL:</strong> {media_url}</p>"
    html += f"<p><strong>Directory exists:</strong> {os.path.exists(media_root)}</p>"
    
    if os.path.exists(media_root):
        files = os.listdir(media_root)
        html += f"<p><strong>Files count:</strong> {len(files)}</p>"
        html += "<ul>"
        for f in files:
            file_path = os.path.join(media_root, f)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            html += f"<li>{f} ({size} bytes) - <a href='{media_url}{f}' target='_blank'>Open</a></li>"
        html += "</ul>"
    else:
        html += "<p style='color:red;'>MEDIA_ROOT directory does not exist!</p>"
    
    return HttpResponse(html)

@login_required
def toggle_pro_status(request, user_id):
    """Activa o desactiva el estado PRO de un usuario manualmente."""
    if not request.user.is_superuser:
        return HttpResponse("Acceso denegado.", status=403)
    
    from .models import UserSettings
    try:
        settings = UserSettings.objects.get(user_id=user_id)
        settings.is_pro = not settings.is_pro
        settings.save()
        messages.success(request, f"Estado Pro de {settings.user.email} actualizado a {'ACTIVO' if settings.is_pro else 'DESACTIVADO'}")
    except UserSettings.DoesNotExist:
        messages.error(request, "Ajustes de usuario no encontrados.")
    
    return redirect('mastering:user_admin_list')

@login_required
def user_admin_list(request):
    """Muestra la lista de todos los usuarios y estadísticas reales de Google."""
    if not request.user.is_superuser:
        return HttpResponse("Acceso denegado.", status=403)
    
    from .models import UserSettings
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Obtener todas las configuraciones de usuario
    all_settings = UserSettings.objects.all().select_related('user').order_by('-user__date_joined')
    
    # Contar cuántos son PRO
    pro_count = all_settings.filter(is_pro=True).count()
    user_count = all_settings.count()
    
    # Get Google Analytics stats
    ga_stats = get_google_analytics_stats()
    
    return render(request, 'mastering/admin_users.html', {
        'all_settings': all_settings,
        'pro_count': pro_count,
        'user_count': user_count,
        'ga_visits': ga_stats.get('visits', 'N/A'),
        'ga_avg_position': ga_stats.get('avg_position', 'N/A')
    })

