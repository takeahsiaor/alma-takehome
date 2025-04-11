import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models import EmailNotification, Lead

logger = logging.getLogger(__name__)

class EmailNotifier:
    """In order to not cause excessive db.commits(), which may be problematic
    when setting up context manager transactions with db.begin(), this will perform
    db.adds but will leave committing to users of this client.

    From a conceptual and encapsulation point of view, it makes sense to wrap
    the EmailNotification creation logic together with the external email sending logic.
    At the same time, external APIs are I/O bound which suggests that we should await them.

    But since this is likely going to be all wrapped within a transaction, awaiting within
    a transaction may cause issues if we're waiting longer than expected.

    Ultimately, this is a nuance that I would need to do more research and testing on.
    For now I'm opting for what i consider a cleaner encapsulation assuming that awaiting
    within a transaction is potentially more dangerous. To mitigate the potential for blocking
    too long on a sync IO function, I would set a short timeout on the request out to the
    external API.
    """
    def __init__(self, db: Session):
        self.db = db

    def _create_email_notification(
        self,
        subject: str,
        body: str,
        recipient_email: str,
        lead: Optional[Lead] = None
    ) -> EmailNotification:
        notification = EmailNotification(
            subject=subject,
            body=body,
            recipient_email=recipient_email,
            lead=lead
        )
        self.db.add(notification)
        return notification

    def _send_new_lead_email_to_prospect(self, lead: Lead) -> None:
        subject = "Thanks for submitting!"
        body = "We'll be right with you"

        self._send_email(subject, body, lead.email)
        self._create_email_notification(subject, body, lead.email, lead)

    def _send_new_lead_email_to_attorney(self, lead: Lead) -> None:
        subject = "Someone has submitted!"
        body = "Get to them ASAP"

        self._send_email(subject, body, lead.assigned_to.email)
        self._create_email_notification(subject, body, lead.assigned_to.email, lead)

    def _send_email(self, subject: str, body: str, recipient_email: str) -> None:
        # Integration with external email service goes here!
        # <--------------------------->
        # Will need to wrap the integration logic in try/excepts so that if the external
        # service is down, we don't roll back any db transactions
        pass

    def send_new_lead_email_notification(self, lead: Lead) -> None:
        self._send_new_lead_email_to_prospect(lead=lead)
        if lead.assigned_to:
            self._send_new_lead_email_to_attorney(lead=lead)
        else:
            logger.warning(f'No attorney was notified for new lead {lead.id}')
