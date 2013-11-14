from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel


class DocdataOrder(models.Model):
    """
    Tracking of the order which is sent to docdata.
    """
    # Simplified internal status codes.
    # Lowercased on purpose to avoid mixing the statuses together.
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_PAID = 'paid'
    STATUS_CHARGED_BACK = 'changed_back'
    STATUS_CANCELLED = 'cancelled'
    STATUS_PENDING = 'pending'
    STATUS_REFUNDED = 'refunded'
    STATUS_UNKNOWN = 'unknown'

    STATUS_CHOICES = (
        (STATUS_PAID, _("Paid")),
        (STATUS_IN_PROGRESS, _("In Progress")),
        (STATUS_CHARGED_BACK, _("Charged back")),
        (STATUS_CANCELLED, _("Cancelled")),
        (STATUS_PENDING, _("Pending")),
        (STATUS_REFUNDED, _("Refunded")),
        (STATUS_UNKNOWN, _("Unknown")),
    )

    merchant_order_id = models.CharField(_("Order ID"), max_length=100, default='')
    order_key = models.CharField(_("Docdata ID"), max_length=200, default='', unique=True)

    status = models.CharField(_("Status"), max_length=50, choices=STATUS_CHOICES, default=STATUS_NEW)
    language = models.CharField(_("Language"), max_length=5, blank=True, default='en')

    # Track
    total_gross_amount = models.DecimalField(_("Total gross amount"), max_digits=15, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=10)
    country = models.CharField(_("Country_code"), max_length=2, null=True, blank=True)

    # Internal info.
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        ordering = ('-created', '-updated')
        verbose_name = _("Docdata Order")
        verbose_name_plural = _("Docdata Orders")

    def __unicode__(self):
        return self.order_key

    @property
    def latest_payment(self):
        try:
            return self.payments.order_by('-merchant_order_id').all()[0]
        except IndexError:
            return None


class DocdataPayment(PolymorphicModel):
    """
    A reported Docdata payment.

    Some payment types have additional fields, which are stored as subclass.
    """
    docdata_order = models.ForeignKey(DocdataOrder, related_name='payments')
    payment_id = models.CharField(_("Payment id"), max_length=100, default='', blank=True, primary_key=True)

    # Note: We're not using choices here so that we can write unknown statuses if they are presented by Docdata.
    status = models.CharField(_("status"), max_length=30, default='NEW')

    # The payment method id from Docdata (e.g. IDEAL, MASTERCARD, etc)
    payment_method = models.CharField(max_length=60, default='', blank=True)

    # Internal info.
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    def __unicode__(self):
        return self.payment_id

    class Meta:
        ordering = ('-created', '-updated')
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class DocdataDirectDebitPayment(DocdataPayment):
    """
    Web direct debit direct payment.
    """
    holder_name = models.CharField(max_length=35)  # max_length from Docdata
    holder_city = models.CharField(max_length=35)  # max_length from Docdata
    holder_country_code = models.CharField(_("Country_code"), max_length=2, null=True, blank=True)

    # Note: there is django-iban for validated versions of these fields.
    # Not needed here.
    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=11)

    class Meta:
        ordering = ('-created', '-updated')
        verbose_name = _("Direct Debit Payment")
        verbose_name_plural = _("Derect Debit Payments")
