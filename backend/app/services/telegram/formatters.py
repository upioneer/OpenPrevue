"""Monospaced retro ASCII message formatters for Telegram bot responses."""

from datetime import datetime


def format_bulletin(title: str, events: list[dict], metro_label: str = "NEW ORLEANS") -> str:
    """Format a list of events into a classic monospaced Prevue bulletin."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    lines = [
        "```",
        divider,
        f"| OPENPREVUE EVENT GUIDE : {metro_label[:14].ljust(14)} |",
        f"| BULLETIN: {title[:28].ljust(28)} |",
        divider,
    ]

    if not events:
        lines.append("| NO SCHEDULED LISTINGS FOUND            |")
        lines.append(divider)
        lines.append("```")
        return "\n".join(lines)

    for idx, evt in enumerate(events[:10], start=1):
        name = evt.get("title", "Untitled")[:34]
        venue = evt.get("venue_name", "Local Venue")[:32]
        cat = evt.get("category", "OTHER").upper()[:10]
        time_str = ""

        if evt.get("start_time"):
            try:
                dt = datetime.fromisoformat(str(evt["start_time"]).replace("Z", "+00:00"))
                time_str = dt.strftime("%a %I:%M %p")
            except Exception:
                time_str = str(evt["start_time"])[:15]

        price_str = ""
        p_min = evt.get("price_min")
        p_max = evt.get("price_max")
        if p_min is not None and p_max is not None:
            price_str = f"${int(p_min)}-${int(p_max)}" if p_min != p_max else f"${int(p_min)}"
        elif p_min is not None:
            price_str = f"${int(p_min)}"

        ticket_tag = "[TKT] " if evt.get("has_ticket") == 1 else ""

        lines.append(f"| {StringPad(f'{idx}. {ticket_tag}{name}', width - 4)} |")
        lines.append(f"|   VENUE : {StringPad(venue, width - 12)} |")
        lines.append(f"|   TIME  : {StringPad(time_str, width - 12)} |")
        lines.append(f"|   TYPE  : {StringPad(f'{cat} {price_str}', width - 12)} |")
        if idx < len(events[:10]):
            lines.append("| " + "." * (width - 4) + " |")

    lines.append(divider)
    lines.append(f"| SHOWING {min(len(events), 10)} OF {len(events)} EVENTS             |")
    lines.append(divider)
    lines.append("```")

    return "\n".join(lines)


def format_error_box(error_title: str, error_detail: str, usage_example: str | None = None) -> str:
    """Format an error message inside a boxed ASCII retro frame."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    lines = [
        "```",
        divider,
        f"| ERROR: {StringPad(error_title[:28], width - 11)} |",
        divider,
        f"| {StringPad(error_detail[:38], width - 4)} |",
    ]

    if usage_example:
        lines.append("| " + "-" * (width - 4) + " |")
        lines.append(f"| USAGE: {StringPad(usage_example[:30], width - 11)} |")

    lines.append(divider)
    lines.append("| Send /help to view command directory   |")
    lines.append(divider)
    lines.append("```")

    return "\n".join(lines)


def format_help_menu() -> str:
    """Format complete command guide inside retro ASCII frame."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    return "\n".join([
        "```",
        divider,
        "| OPENPREVUE BOT COMMAND DIRECTORY       |",
        divider,
        "| /today            - Events today       |",
        "| /tonight          - Events >= 5:00 PM  |",
        "| /weekend          - Fri-Sun listings   |",
        "| /search <query>   - Search artist/venue|",
        "| /pin <event_id>   - Pin to TV spotlight|",
        "| /unpin <event_id> - Unpin from display |",
        "| /watch <keyword>  - Track alert keyword|",
        "| /unwatch <keyword>- Remove alert track |",
        "| /watchlist        - View alert keywords|",
        "| /pair <code>      - Link Telegram chat |",
        "| /status           - System & sync info |",
        "| /help             - Display this menu  |",
        divider,
        "```",
    ])


def format_status_card(stats: dict) -> str:
    """Format system telemetry and sync status."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    radius_text = f"{stats.get('radius_miles', 35)} MILES"
    last_sync_text = stats.get('last_sync', 'N/A')[:16]
    weather_text = stats.get('weather', 'N/A')[:16]

    return "\n".join([
        "```",
        divider,
        "| OPENPREVUE SYSTEM TELEMETRY            |",
        divider,
        f"| STATUS      : {StringPad(stats.get('status', 'OK'), width - 18)} |",
        f"| METRO       : {StringPad(stats.get('metro_label', 'NEW ORLEANS'), width - 18)} |",
        f"| RADIUS      : {StringPad(radius_text, width - 18)} |",
        f"| ACTIVE EVTS : {StringPad(str(stats.get('active_events', 0)), width - 18)} |",
        f"| LAST SYNC   : {StringPad(last_sync_text, width - 18)} |",
        f"| TEMP        : {StringPad(weather_text, width - 18)} |",
        divider,
        "```",
    ])


def format_watchlist(keywords: list[str]) -> str:
    """Format active watchlist alert keywords."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    lines = [
        "```",
        divider,
        "| ACTIVE WATCHLIST KEYWORDS              |",
        divider,
    ]

    if not keywords:
        lines.append("| NO ACTIVE KEYWORDS REGISTERED          |")
        lines.append("| Use: /watch <band or team name>        |")
    else:
        for idx, kw in enumerate(keywords, start=1):
            lines.append(f"| {StringPad(f'{idx}. {kw}', width - 4)} |")

    lines.append(divider)
    lines.append("```")

    return "\n".join(lines)


def format_pairing_success(username: str, chat_id: int) -> str:
    """Format device pairing confirmation card."""
    width = 42
    divider = "+" + "-" * (width - 2) + "+"

    return "\n".join([
        "```",
        divider,
        "| DEVICE PAIRING SUCCESSFUL              |",
        divider,
        f"| USER        : {StringPad(username or 'Unknown', width - 18)} |",
        f"| CHAT ID     : {StringPad(str(chat_id), width - 18)} |",
        f"| STATUS      : {StringPad('AUTHENTICATED', width - 18)} |",
        divider,
        "| Remote curation & alerts enabled.      |",
        "| Send /today to query listings.         |",
        divider,
        "```",
    ])


def StringPad(text: str, length: int) -> str:
    """Pad or truncate string to fixed character length."""
    return text[:length].ljust(length)
