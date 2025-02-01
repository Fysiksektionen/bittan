from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, F, Sum
from bittan.forms.forms import ChapterEventDropdownTicketCreation, ChapterEventForm, SearchForm, PaymentForm, TicketCreationForm, TicketForm
from bittan.models import ChapterEvent, Ticket, Payment
from bittan.models.payment import PaymentStatus

@login_required
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def staff_dashboard(request):
    dropdown = ChapterEventForm(request.GET or None)
    chapter_events = ChapterEvent.objects.all()
    ticket_type_infos = None
    total_values = None

    if dropdown.is_valid():
        selected_chapter_event = dropdown.cleaned_data.get("chapter_event")
        if selected_chapter_event:
            chapter_event = get_object_or_404(ChapterEvent, pk=selected_chapter_event.pk)
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
            search_res = Payment.objects.filter(swish_id=query)

        payment_forms = {payment.id: PaymentForm(instance=payment) for payment in search_res}
        ticket_forms = {ticket.id: TicketForm(instance=ticket) for payment in search_res for ticket in payment.ticket_set.all()}
    
    ce_create_ticket_dropdown = ChapterEventDropdownTicketCreation

    context = {
        "dropDownMenu": dropdown, 
        "chapter_events": chapter_events, 
        "ticket_types": ticket_type_infos, 
        "total_values": total_values,
        "searchBar": search_bar,
        "search_res": search_res,
        "payment_forms": payment_forms,
        "ticket_forms": ticket_forms,
        "createTicketDropdown": ce_create_ticket_dropdown,
    }

    return render(request, "staff_dashboard.html", context)

@require_POST
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def update_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    form = PaymentForm(request.POST, instance=payment)
    if form.is_valid():
        form.save()
    query_param = request.POST.get("query")
    return redirect(f"/staff/?query={query_param}") 

@require_POST
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    form = TicketForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
    query_param = request.POST.get("query")
    return redirect(f"/staff/?query={query_param}") 

@require_GET
def filter_ticket_type_from_chapter_event(request, chapter_event_id):
    chapter_event = ChapterEvent.objects.get(pk=chapter_event_id)
    ticket_types = chapter_event.ticket_types.all()
    ticket_types_data = [{"id": tt.pk, "title": tt.title, "price": tt.price} for tt in ticket_types]
    return JsonResponse({"ticket_types": ticket_types_data})
    

@require_POST
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def create_tickets(request):
    return JsonResponse({'success': False, 'errors': form.errors})
    
