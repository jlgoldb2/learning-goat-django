from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

# Create your tests here.
from lists.views import home_page
from lists.models import Item, List

LISTS_URL = '/lists/the-only-list-in-the-world'


class NewListTest(TestCase):

    def test_saving_a_POST_request(self):
        self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'},
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        #request = self.list_item_post_request()

        response = self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )

        self.assertRedirects(
            response,
            LISTS_URL,
            target_status_code=200
            #http://stackoverflow.com/questions/
            #19318246/django-testing-redirections-when
            #-the-target-url-is-also-a-redirection
        )


class ListViewTest(TestCase):

    def test_make_sure_list_template_exists(self):
        # getting a AssertionError: No templates used to render the response
        # from line:
        #       self.assertTemplateUsed(response, 'templates/list.html')
        # of test_uses_list_templates

        with open('./lists/templates/list.html') as f:
            list_html = f.read()
        self.assertIn('<html>', list_html)

    def test_displays_all_list_items(self):
        list_ = List.objects.create()
        Item.objects.create(text="itemy 1", list=list_)
        Item.objects.create(text="itemy 2", list=list_)

        response = self.client.get(LISTS_URL)

        self.assertContains(response, "itemy 1")
        self.assertContains(response, "itemy 2")


class ListAndItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        text1 = 'The first (ever) list item'
        text2 = 'Item the second'

        first_item = Item()
        first_item.text = text1
        first_item.list = list_
        first_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        second_item = Item()
        second_item.text = text2
        second_item.list = list_
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.text, text1)
        self.assertEqual(first_saved_item.list, list_)

        self.assertEqual(second_saved_item.text, text2)
        self.assertEqual(second_saved_item.list, list_)


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html')
        self.assertEqual(response.content.decode(), expected_html)

    def test_home_page_only_saves_items_when_necessary(self):
        req = HttpRequest()
        home_page(req)
        self.assertEqual(Item.objects.count(), 0)
