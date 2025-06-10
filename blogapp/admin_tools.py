import os
import subprocess
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET

COOLDOWN_SECONDS = 15 * 60
COOLDOWN_FILE = os.path.join(settings.BASE_DIR, "last_restart.txt")

def get_last_restart():
    try:
        with open(COOLDOWN_FILE, "r") as f:
            return float(f.read().strip())
    except Exception:
        return 0

def set_last_restart():
    with open(COOLDOWN_FILE, "w") as f:
        f.write(str(time.time()))

@staff_member_required
@require_POST
def restart_pythonanywhere_server(request):
    PA_USER = os.environ.get("PYTHONANYWHERE_USERNAME")
    is_pythonanywhere = 'PYTHONANYWHERE_DOMAIN' in os.environ
    now = time.time()
    last_restart = get_last_restart()
    if now - last_restart < COOLDOWN_SECONDS:
        messages.error(request, "Debes esperar antes de reiniciar el servidor nuevamente.")
        return redirect(reverse('admin:index'))
    if not is_pythonanywhere:
        messages.error(request, "Esta función solo está disponible en producción (PythonAnywhere).")
        return redirect(reverse('admin:index'))
    try:
        wsgi_path = f"/var/www/{PA_USER}_pythonanywhere_com_wsgi.py"
        subprocess.run(['touch', wsgi_path], check=True)
        set_last_restart()
        messages.success(request, "Servidor reiniciado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al reiniciar el servidor: {e}")
    return redirect(reverse('admin:index'))

@staff_member_required
@require_GET
def get_restart_cooldown(request):
    now=time.time()
    last_restart=get_last_restart()
    remaining=max(0, int(COOLDOWN_SECONDS-(now-last_restart)))
    from django.http import JsonResponse
    return JsonResponse({"remaining":remaining})