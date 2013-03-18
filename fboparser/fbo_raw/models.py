from django.db import models

SOLICITATION_CHOICES = (
    ('PRESOL', 'Presolicitation'),
    ('COMBINE', 'Combined Synopsis/Solicitation'),
    ('SRCSGT', 'Sources Sought'),
    ('SSALE', 'Sale of Surplus Property'),
    ('SNOTE', 'Special Notice'),
    ('FSTD', 'Foreign Government Standard')

)

JUSTIFICATION_CHOICES = (
    (1, 'Urgency'),
    (2, 'Only One Source (Except Brand Name)'),
    (3, 'Follow-on Delivery Order Following Competitive Initial Order'),
    (4, 'Minimum Guarantee'),
    (5, 'Other Statutory Authority')
)


class GenericNode(models.model):

    sol_number = models.CharField(max_length=128, null=False)
    date = models.DateField()
    naics = models.IntegerField(max_length=6)
    description = models.TextField()
    class_code = models.CharField(max_length=20)
    subject = models.CharField(max_length=128)
    zip_code = models.CharField(max_length=10)
    setaside = models.CharField(max_length=128)
    contact = models.TextField()
    link = models.URLField()
    email = models.EmailField()
    office_address = models.CharField()
    archive_date = models.DateField()
    correction = models.BooleanField()

    class Meta:
        abstract = True

class Solicitation(GenericNode):
    response_date = models.DateField()
    pop_address = models.CharField(max_length=255)
    pop_zip = models.CharField(max_length=10)
    pop_country = models.CharField(max_length=25)
    recovery_act = models.BooleanField(default=False)
    solicitation_type = models.CharField(choices=SOLICITATION_CHOICES)

class Award(GenericNode):
    base_notice_type = models.CharField(choices=SOLICITATION_CHOICES)
    award_number = models.CharField(max_length=255)
    award_amount = models.DecimalField()
    award_date = models.DateField()
    line_number = models.IntegerField()
    awardee = models.TextField()
    
class Justification(Award):
    statutory_authority = models.CharField(max_length=255)
    modification_number = models.CharField(max_length=255)

class FairOpportunity(GenericNode):
    base_notice_type = models.CharField(choices=SOLICITATION_CHOICES)
    #Fair Opportunity/Limited Sources Justification Authority
    foja = models.IntegerField(choices=JUSTIFICATION_CHOICES)
    award_number = models.CharField(max_length=255)
    #award date of order
    award_date = models.DateField()
    #Delivery/Task Order Number
    order_number = models.CharFIeld(max_length=255)
    modification_number = models.CharField(max_length=255)

#Intent To Bundle Notices, DOD only
class ITB(GenericNode):
    base_notice_type = models.CharField(choices=SOLICITATION_CHOICES)
    award_number = models.CharField(max_length=255)
    #Delivery/Task Order Number
    order_number = models.CharFIeld(max_length=255)


