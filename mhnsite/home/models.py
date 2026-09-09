from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageBlock


class HeadingBlock(blocks.CharBlock):
    class Meta:
        icon = "form"
        template = "home/blocks/heading_block.html"


class ParagraphBlock(blocks.RichTextBlock):
    class Meta:
        icon = "doc-full"
        template = "home/blocks/paragraph_block.html"


class QuoteBlock(blocks.StructBlock):
    """Display one quote."""

    text = blocks.TextBlock(required=True)
    # author = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "openquote"
        template = "home/blocks/quote_block.html"


class QuotesBlock(blocks.StreamBlock):
    """Display a series of quote blocks."""

    quote = QuoteBlock()

    class Meta:
        icon = "list-ul"
        template = "home/blocks/quotes_block.html"


class ProminentLinkBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(required=True, max_length=255)
    link_url = blocks.URLBlock(required=True)

    class Meta:
        icon = "link"
        template = "home/blocks/prominent_link_block.html"


class TextCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=255)
    text = blocks.TextBlock(required=True)
    link = ProminentLinkBlock(
        required=False, template="home/blocks/textcard_link_block.html"
    )

    class Meta:
        icon = "doc-full"
        template = "home/blocks/text_card_block.html"


class TextCardBlocks(blocks.StreamBlock):
    text_card = TextCardBlock()

    class Meta:
        icon = "list-ul"
        template = "home/blocks/text_card_blocks.html"


class EmpfehlungBlock(blocks.StructBlock):
    image = ImageBlock(required=True)
    text = blocks.TextBlock(required=True)
    name = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "doc-full"
        template = "home/blocks/empfehlung_block.html"


class EmpfehlungenBlock(blocks.StreamBlock):
    empfehlung = EmpfehlungBlock()

    class Meta:
        icon = "list-ul"
        template = "home/blocks/empfehlungen_block.html"


class HomePage(Page):
    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("paragraph", ParagraphBlock()),
            ("image", ImageBlock()),
            ("prominent_link", ProminentLinkBlock()),
            ("quotes", QuotesBlock()),
            ("text_cards", TextCardBlocks()),
            ("empfehlungen", EmpfehlungenBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
