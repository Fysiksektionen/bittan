from bittan import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Count, F, Sum
from django.db.utils import IntegrityError

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status


from uuid import uuid4
import logging
import random

from bittan.forms.forms import ChapterEventDropdownTicketCreation, ChapterEventForm, SearchForm, PaymentForm, TicketForm
from bittan.models import ChapterEvent, Ticket, Payment
from bittan.models.payment import PaymentStatus
from bittan.mail import mail_payment, send_bulk_mail
from bittan.mail import MailError

PREFIX = "/"
PREFIX += settings.get_bittan_backend_url_path_prefix()

@login_required
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def staff_dashboard(request):
    """
    Renders the staff dashboard with the appropriate information and functionality to administer basic staff tasks. 
    """
    dropdown = ChapterEventForm(request.GET or None)
    chapter_events = ChapterEvent.objects.all()
    ticket_type_infos = None
    total_values = None

    # Default id is -1. This corresponds to all chapter events. 
    selected_chapter_event_id = -1

    if dropdown.is_valid():
        selected_chapter_event = dropdown.cleaned_data.get("chapter_event")
        if selected_chapter_event:
            chapter_event = get_object_or_404(ChapterEvent, pk=selected_chapter_event.pk)
            selected_chapter_event_id = selected_chapter_event.pk
            ticket_type_infos = chapter_event.ticket_set.filter(
                payment__status = PaymentStatus.PAID, 
                chapter_event = selected_chapter_event
            ).values("ticket_type", "ticket_type__title").annotate(
                ticket_count=Count("id"),
                total_price=F("ticket_count") * F("ticket_type__price")
            )        
        else:
            ticket_type_infos = Ticket.objects.filter(
                payment__status = PaymentStatus.PAID, 
            ).values("ticket_type", "ticket_type__title").annotate(
                ticket_count=Count("id"),
                total_price=F("ticket_count") * F("ticket_type__price")
            )
        total_values = ticket_type_infos.aggregate(
                total_ticket_count=Sum("ticket_count"),
                all_ticket_price=Sum("total_price")
            )

    search_bar = SearchForm(request.GET or None)
    search_res = None
    payment_forms = None
    ticket_forms = None
    if search_bar.is_valid():
        query = search_bar.cleaned_data["query"]
        search_res = Payment.objects.filter(email=query)
        if search_res.count() == 0:
            search_res = Payment.objects.filter(swish_id=query.upper())

        payment_forms = {payment.id: PaymentForm(instance=payment) for payment in search_res}
        ticket_forms = {ticket.id: TicketForm(instance=ticket, prefix=f"ticket_{ticket.id}") for payment in search_res for ticket in payment.ticket_set.all()}
    
    ce_create_ticket_dropdown = ChapterEventDropdownTicketCreation


    context = {
        "dropDownMenu": dropdown, 
        "chapter_events": chapter_events, 
        "chosen_chapter_event": selected_chapter_event_id,
        "ticket_types": ticket_type_infos, 
        "total_values": total_values,
        "searchBar": search_bar,
        "search_res": search_res,
        "payment_forms": payment_forms,
        "ticket_forms": ticket_forms,
        "createTicketDropdown": ce_create_ticket_dropdown,
        "url_prefix": PREFIX 
    }

    return render(request, "staff_dashboard.html", context)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["email", "status"]

@api_view(["POST"])
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def update_payment(request, payment_id):
    """
    Takes form input from the staffpage and updates a payment. 
    """
    payment = get_object_or_404(Payment, id=payment_id)
    serializer = PaymentSerializer(payment, data=request.data)
    if serializer.is_valid():
        serializer.save()
        query_param = request.POST.get("query")
        return redirect(f"{PREFIX}staff/?query={query_param}") 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(["GET"])
def filter_ticket_type_from_chapter_event(request, chapter_event_id) -> Response:
    """
    Gets all the allowed ticket types from a chapter event by the chapter event's id. 
    """
    try:
        chapter_event = ChapterEvent.objects.get(pk=chapter_event_id)
        ticket_types = chapter_event.ticket_types.all()
        ticket_types_data = [{"id": tt.pk, "title": tt.title, "price": tt.price} for tt in ticket_types]
        return Response({"ticket_types": ticket_types_data}, status=status.HTTP_200_OK)
    except ChapterEvent.DoesNotExist:
        return Response({"error": "Chapter event not found"}, status=status.HTTP_404_NOT_FOUND)


@require_POST
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def update_tickets(request, payment_id):
    """
    Takes form input from the staff page and updates tickets associated with a payment accordingly. 
    """
    payment = get_object_or_404(Payment, id=payment_id)
    tickets = payment.ticket_set.all()
    forms = []
    errors = False
    chapter_event_changes = {}

    for ticket in tickets:
        old_chapter_event_pk = ticket.chapter_event.pk
        form = TicketForm(request.POST, instance=ticket, prefix=f"ticket_{ticket.id}")
        forms.append(form)


        if form.is_valid():
            new_chapter_event = form.cleaned_data.get("chapter_event")
            old_chapter_event = ChapterEvent.objects.get(pk=old_chapter_event_pk)

            if new_chapter_event != old_chapter_event:
                chapter_event_changes[new_chapter_event] = chapter_event_changes.get(new_chapter_event, 0) + 1
                chapter_event_changes[old_chapter_event] = chapter_event_changes.get(old_chapter_event, 0) - 1
        else:
            errors = True

    if not errors:
        for chapter_event, change in chapter_event_changes.items():
            if change > chapter_event.total_seats - chapter_event.alive_ticket_count:
                errors = True
                for form in forms:
                    if form.cleaned_data.get("chapter_event") == chapter_event:
                        form.add_error('chapter_event', "Exceeds maximum ticket count for this chapter event")

    if not errors:
        for form in forms:
            form.save()

        for ticket in tickets:
            delete_checkbox = request.POST.get(f"delete_ticket_{ticket.id}")
            if delete_checkbox:
                ticket.delete()

    return redirect(f"{PREFIX}staff/?query={payment.swish_id}") 

    

class TicketCreationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    chapter_event = serializers.PrimaryKeyRelatedField(queryset=ChapterEvent.objects.all())
    ticket_types = serializers.DictField(child=serializers.IntegerField())
    ignore_seat_limit = serializers.BooleanField()
    send_receipt = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chapter_event = self.initial_data.get('chapter_event')
        if chapter_event:
            chapter_event_instance = ChapterEvent.objects.get(id=chapter_event)
            ticket_types = chapter_event_instance.ticket_types.all()
            for ticket_type in ticket_types:
                self.fields[f'ticket_type_{ticket_type.id}'] = serializers.IntegerField(required=False, min_value=0)

    def validate(self, data):
        chapter_event = data['chapter_event']
        ticket_types = chapter_event.ticket_types.all()
        total_ticket_count = sum(data.get(f"ticket_type_{ticket_type.id}", 0) for ticket_type in ticket_types)
        ignore_seat_limit = data.get("ignore_seat_limit", False)

        if not ignore_seat_limit and total_ticket_count > chapter_event.total_seats - chapter_event.alive_ticket_count:
            raise serializers.ValidationError("Not enough tickets left")

        return data

@api_view(["POST"])
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def create_tickets(request) -> Response:
    """
    Takes ticket information from the 
    """
    serializer = TicketCreationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    chapter_event = serializer.validated_data['chapter_event']
    ticket_types = chapter_event.ticket_types.all()
    email = serializer.validated_data['email']
    ticket_counts = {f"ticket_type_{ticket_type.id}": serializer.validated_data.get(f"ticket_type_{ticket_type.id}", 0) for ticket_type in ticket_types}
    ignore_seat_limit = serializer.validated_data["ignore_seat_limit"]
    send_receipt = serializer.validated_data["send_receipt"]

    payment = Payment.objects.create(
        expires_at=timezone.now() + chapter_event.reservation_duration,
        swish_id=str(uuid4()).replace('-', '').upper(),
        status=PaymentStatus.PAID,
        email=email,
        payment_started=True,
        time_paid=timezone.now()
    )

    for ticket_type in ticket_types:
        quantity = ticket_counts.get(f"ticket_type_{ticket_type.id}", 0)
        for _ in range(quantity):
            for _ in range(1000):
                try:
                    Ticket.objects.create(
                        external_id=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)),
                        time_created=timezone.now(),
                        payment=payment,
                        ticket_type=ticket_type,
                        chapter_event=chapter_event
                    )
                except IntegrityError:
                    continue
                break
            else:
                payment.status = PaymentStatus.FAILED_OUT_OF_IDS
                logging.critical("Failed to generate a ticket external id. This should never happen. This happened when admin attempted to create a ticket.")
                return Response("Failed to create tickets.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        mail_payment(payment, send_receipt=send_receipt)
    except MailError as e:
        logging.warning(f"Error {e} when attempting to send mail for staff created tickets.")
        payment.status = PaymentStatus.FAILED_ADMIN
        payment.save()
        return Response("Something went wrong when sending the email.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(payment.swish_id, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def resend_email(request) -> Response:
    """
    Takes payment info from the staffpage and resends the standard payment mail to the mail address associated with the payment. 
    """
    payment_id = request.data["paymentId"]
    payment: Payment =  Payment.objects.get(pk=payment_id)

    try:
        mail_payment(payment)
        payment.sent_email = True
        payment.save()
    except MailError as e:
        logging.warning(f"Error {e} when attempting to resend mail from staff interface. ")
        payment.status = PaymentStatus.FAILED_ADMIN
        payment.save()
        return Response({'success': False, 'errors': "Something went wrong when sending the email. "})
    
    return Response({'success': True})

@api_view(["POST"])
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def send_mass_email(request) -> Response:
    chapter_event_id = request.data["chapter_event_id"]
    mail_subject = request.data["email_subject"]
    if mail_subject == "":
        return Response({"success": False, "errors": "Mail subject is empty. "})
    mail_content = request.data["email_content"]
    if mail_content == "":
        return Response({"success": False, "errors": "Mail content is empty. "})
    
    # Chapter event id of -1 is all chapter events in this case. 
    if chapter_event_id == -1:
        mail_addresses = Payment.objects.filter(
            status=PaymentStatus.PAID
        ).values_list("email", flat=True)
    else:
        chapter_event: ChapterEvent = ChapterEvent.objects.get(pk=chapter_event_id)
        mail_addresses = Payment.objects.filter(
            ticket__chapter_event=chapter_event,
            status=PaymentStatus.PAID
        ).values_list("email", flat=True)
    
    try:
        send_bulk_mail(list(mail_addresses), mail_subject, mail_content)
    except MailError as e:
        logging.warning(f"Error {e} when attempting to send mass mail from staff interface. ")
        return Response({'success': False, 'errors': "Something went wrong when sending the mass email. "})


    return Response({"success": True})

