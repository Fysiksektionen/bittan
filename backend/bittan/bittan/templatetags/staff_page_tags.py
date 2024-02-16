from django import template

register = template.Library()

@register.simple_tag
def get_total_by_ticket_type(chapter_event, ticket_type_id) -> float:
    return chapter_event.total_price_by_ticket_type(ticket_type_id)