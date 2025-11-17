from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing_by_id
from users.decorators import manager_required
from users.models import Profile


def index(request):
    """Главная страница с расширенной статистикой"""
    if request.user.is_authenticated:
        # Основная статистика
        total_mailings = Mailing.objects.filter(owner=request.user).count()
        active_mailings = Mailing.objects.filter(
            owner=request.user,
            status=Mailing.STATUS_STARTED
        ).count()
        unique_clients = Client.objects.filter(owner=request.user).count()

        # Статистика по попыткам
        user_mailings = Mailing.objects.filter(owner=request.user)
        total_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings).count()
        successful_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings,
            status=MailingAttempt.STATUS_SUCCESS
        ).count()
        failed_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings,
            status=MailingAttempt.STATUS_FAILED
        ).count()

        # Проценты успеха
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        failure_rate = (failed_attempts / total_attempts * 100) if total_attempts > 0 else 0

        # Статусы рассылок
        created_mailings = Mailing.objects.filter(
            owner=request.user,
            status=Mailing.STATUS_CREATED
        ).count()
        completed_mailings = Mailing.objects.filter(
            owner=request.user,
            status=Mailing.STATUS_COMPLETED
        ).count()

        # Последние рассылки
        recent_mailings = Mailing.objects.filter(owner=request.user).order_by('-created_at')[:5]

    else:
        total_mailings = 0
        active_mailings = 0
        unique_clients = 0
        total_attempts = 0
        successful_attempts = 0
        failed_attempts = 0
        success_rate = 0
        failure_rate = 0
        created_mailings = 0
        completed_mailings = 0
        recent_mailings = []

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'failed_attempts': failed_attempts,
        'success_rate': success_rate,
        'failure_rate': failure_rate,
        'created_mailings': created_mailings,
        'completed_mailings': completed_mailings,
        'recent_mailings': recent_mailings,
    }
    return render(request, 'mailing/index.html', context)


@login_required
def client_list(request):
    """Список клиентов - пользователь видит только своих, менеджер всех"""
    if hasattr(request.user, 'profile') and request.user.profile.is_manager:
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(owner=request.user)
    return render(request, 'mailing/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    """Создание клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.save()
            messages.success(request, 'Клиент успешно создан!')
            return redirect('mailing:client_list')
    else:
        form = ClientForm()
    return render(request, 'mailing/client_form.html', {'form': form})


@login_required
def client_update(request, pk):
    """Редактирование клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент успешно обновлен!')
            return redirect('mailing:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'mailing/client_form.html', {'form': form})


@login_required
def client_delete(request, pk):
    """Удаление клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Клиент успешно удален!')
        return redirect('mailing:client_list')
    return render(request, 'mailing/client_confirm_delete.html', {'client': client})


@login_required
def mailing_list(request):
    """Список рассылок - пользователь видит только своих, менеджер всех"""
    if hasattr(request.user, 'profile') and request.user.profile.is_manager:
        mailings = Mailing.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=request.user)
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


@login_required
def mailing_create(request):
    """Создание рассылки"""
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(user=request.user)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def message_list(request):
    """Список сообщений"""
    messages = Message.objects.filter(owner=request.user)
    return render(request, 'mailing/message_list.html', {'messages': messages})


@login_required
def message_create(request):
    """Создание сообщения"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            messages.success(request, 'Сообщение успешно создано!')
            return redirect('mailing:message_list')
    else:
        form = MessageForm()
    return render(request, 'mailing/message_form.html', {'form': form})


@login_required
def message_update(request, pk):
    """Редактирование сообщения"""
    message_obj = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено!')
            return redirect('mailing:message_list')
    else:
        form = MessageForm(instance=message_obj)
    return render(request, 'mailing/message_form.html', {'form': form})


@login_required
def message_delete(request, pk):
    """Удаление сообщения"""
    message_obj = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        message_obj.delete()
        messages.success(request, 'Сообщение успешно удалено!')
        return redirect('mailing:message_list')
    return render(request, 'mailing/message_confirm_delete.html', {'message': message_obj})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена!')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(instance=mailing, user=request.user)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена!')
        return redirect('mailing:mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


@login_required
def mailing_send_now(request, pk):
    """Отправка рассылки по требованию через интерфейс"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    if request.method == 'POST':
        try:
            successful, failed = send_mailing_by_id(pk)
            messages.success(
                request,
                f'Рассылка отправлена! Успешно: {successful}, Неудачно: {failed}'
            )
        except Exception as e:
            messages.error(request, f'Ошибка отправки: {str(e)}')

        return redirect('mailing:mailing_list')

    return render(request, 'mailing/mailing_send_confirm.html', {'mailing': mailing})


@manager_required
def user_list(request):
    """Список пользователей - только для менеджеров"""
    users = User.objects.all().select_related('profile')
    return render(request, 'users/user_list.html', {'users': users})


@manager_required
def toggle_user_block(request, user_id):
    """Блокировка/разблокировка пользователя - только для менеджеров"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.profile.blocked = not user.profile.blocked
        user.profile.save()
        action = "заблокирован" if user.profile.blocked else "разблокирован"
        messages.success(request, f'Пользователь {user.username} {action}')
    else:
        messages.error(request, 'Нельзя заблокировать себя')
    return redirect('users:user_list')


@manager_required
def toggle_mailing_status(request, mailing_id):
    """Включение/отключение рассылки - только для менеджеров"""
    mailing = get_object_or_404(Mailing, id=mailing_id)
    if mailing.status == Mailing.STATUS_STARTED:
        mailing.status = Mailing.STATUS_COMPLETED
        action = "отключена"
    else:
        mailing.status = Mailing.STATUS_STARTED
        action = "включена"
    mailing.save()
    messages.success(request, f'Рассылка "{mailing.message.subject}" {action}')
    return redirect('mailing:mailing_list')