from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from django.core import signing
from django.utils import timezone

from newsletter.forms import NewsletterSubscriptionForm
from newsletter.models import NewsletterSnippet


class HeadingBlock(blocks.StructBlock):
    text = blocks.TextBlock(label="Text")
    background = blocks.ChoiceBlock(
        choices=[
            ("normal", "Normal"),
            ("multicolor", "Mehrfarbig"),
        ],
        default="normal",
        label="Hintergrund",
    )

    @classmethod
    def construct_from_lookup(cls, lookup, *args, **kwargs):
        """Keep old migrations readable after headings became structured blocks.

        Historical StreamField migrations stored headings as plain TextBlocks,
        so reconstruct that legacy block when their lookup has no children.
        New lookups include the StructBlock fields and use the superclass.
        """
        if not args and not kwargs:
            return blocks.TextBlock()
        return super().construct_from_lookup(lookup, *args, **kwargs)

    class Meta:
        icon = "form"
        label = "Überschrift"
        template = "home/blocks/heading_block.html"


class ParagraphBlock(blocks.RichTextBlock):
    class Meta:
        icon = "doc-full"
        label = "Fließtext"
        template = "home/blocks/paragraph_block.html"


class QuoteBlock(blocks.StructBlock):
    """Display one quote."""

    text = blocks.TextBlock(required=True)
    # author = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "openquote"
        label = "Ein Zitat"
        template = "home/blocks/quote_block.html"


class QuotesBlock(blocks.StreamBlock):
    """Display a series of quote blocks."""

    quote = QuoteBlock()

    class Meta:
        icon = "list-ul"
        label = "Serie von Zitaten"
        template = "home/blocks/quotes_block.html"


class ProminentLinkBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(required=True, max_length=255)
    link_url = blocks.URLBlock(required=True)

    class Meta:
        icon = "link"
        label = "Link auf externe Seite"
        template = "home/blocks/prominent_link_block.html"


class LocalLinkBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(required=True, max_length=255)
    page = blocks.PageChooserBlock(required=True)

    class Meta:
        icon = "link"
        label = "Link auf lokale Seite"
        template = "home/blocks/local_link_block.html"


class ProminentLinksBlock(blocks.StreamBlock):
    prominent_link = ProminentLinkBlock()
    local_link = LocalLinkBlock()

    class Meta:
        icon = "list-ul"
        label = "Herausgestellte Links"
        template = "home/blocks/prominent_links_block.html"


class TextCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=255)
    text = blocks.TextBlock(required=True)
    link = ProminentLinkBlock(
        required=False, template="home/blocks/textcard_link_block.html"
    )

    class Meta:
        icon = "doc-full"
        label = "Textkarte"
        template = "home/blocks/text_card_block.html"


class TextCardBlocks(blocks.StreamBlock):
    text_card = TextCardBlock()

    class Meta:
        icon = "list-ul"
        label = "Textkarten"
        template = "home/blocks/text_card_blocks.html"


class EmpfehlungBlock(blocks.StructBlock):
    image = ImageBlock(required=True)
    text = blocks.TextBlock(required=True)
    name = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "doc-full"
        label = "Empfehlung"
        template = "home/blocks/empfehlung_block.html"


class EmpfehlungenBlock(blocks.StreamBlock):
    empfehlung = EmpfehlungBlock()

    class Meta:
        icon = "list-ul"
        label = "Empfehlungen"
        template = "home/blocks/empfehlungen_block.html"


class BilderBlock(blocks.StreamBlock):
    image = ImageBlock(required=True)

    class Meta:
        icon = "image"
        label = "Bilder"
        template = "home/blocks/bilder_block.html"


class NewsletterSubscriptionBlock(blocks.StructBlock):
    newsletter = SnippetChooserBlock(NewsletterSnippet)

    class Meta:
        icon = "mail"
        label = "Newsletter-Abonnement"
        template = "home/blocks/newsletter_subscription_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["form"] = NewsletterSubscriptionForm(
            initial={"started_at": signing.dumps(timezone.now().isoformat())}
        )
        return context


class EventsBlock(blocks.StructBlock):
    # A block that displays a list of upcoming events.
    class Meta:
        icon = "date"
        label = "Zukünftige Veranstaltungen"
        template = "home/blocks/events_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from events.models import Event

        context["events"] = Event.objects.filter(
            date__gte=timezone.now()
        ).order_by("date")
        return context


class HomePage(Page):
    class Meta:
        verbose_name = "Standardseite"

    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("paragraph", ParagraphBlock()),
            ("prominent_links", ProminentLinksBlock()),
            ("quotes", QuotesBlock()),
            ("text_cards", TextCardBlocks()),
            ("empfehlungen", EmpfehlungenBlock()),
            ("bilder", BilderBlock()),
            ("newsletter", NewsletterSubscriptionBlock()),
            ("events", EventsBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
