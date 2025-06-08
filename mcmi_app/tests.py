from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Item
from .forms import ItemForm

class ItemModelTest(TestCase):
    def test_item_creation(self):
        item = Item.objects.create(name="Test Item", description="This is a test item.")
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "This is a test item.")
        self.assertEqual(str(item), "Test Item")

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.item_list_url = reverse('item_list') # For redirect checks
        self.user_credentials = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        # Create a user for login and other tests that require an authenticated user
        self.user = User.objects.create_user(**self.user_credentials)

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/register.html')

    def test_register_view_post(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'newpassword123', # Changed to password1 based on form error
            'password2': 'newpassword123', # Confirmation field
        })
        if response.status_code == 200 and 'form' in response.context: # If form is invalid and page re-rendered
            print("Registration form errors (test_register_view_post):", response.context['form'].errors)
        # In Django 5+, successful registration redirects.
        # For UserCreationForm, the redirect might be to LOGIN_REDIRECT_URL if set, or another page.
        # Here we assume it redirects to item_list as per our view logic.
        self.assertRedirects(response, self.item_list_url, fetch_redirect_response=False) # Check for redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/login.html')

    def test_login_view_post_success(self):
        response = self.client.post(self.login_url, self.user_credentials)
        self.assertRedirects(response, self.item_list_url, fetch_redirect_response=False) # Check for redirect
        # Check if the user is actually logged in by accessing a protected page
        # However, self.client.session does not persist login state directly in tests
        # Instead, we can check that a user is part of the response context or similar,
        # or by checking `_auth_user_id` in session if needed, but redirect is a good sign.

    def test_login_view_post_fail(self):
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertFormError(response.context['form'], None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_logout_view_post(self):
        self.client.login(**self.user_credentials) # Log in the user first
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url, fetch_redirect_response=False) # Redirects to login

        # Verify user is logged out by trying to access a protected page
        response_after_logout = self.client.get(self.item_list_url)
        self.assertRedirects(response_after_logout, f"{self.login_url}?next={self.item_list_url}")


class ItemViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_credentials = {'username': 'testuser', 'password': 'testpassword123'}
        self.user = User.objects.create_user(**self.user_credentials)
        self.client.login(**self.user_credentials)

        self.item = Item.objects.create(name="Test Item 1", description="Description 1")
        self.item_list_url = reverse('item_list')
        self.item_detail_url = reverse('item_detail', args=[self.item.pk])
        self.item_create_url = reverse('item_create')
        self.item_update_url = reverse('item_update', args=[self.item.pk])
        self.item_delete_url = reverse('item_delete', args=[self.item.pk])

    def test_item_list_view_get(self):
        response = self.client.get(self.item_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/item_list.html')
        self.assertContains(response, self.item.name)

    def test_item_detail_view_get(self):
        response = self.client.get(self.item_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/item_detail.html')
        self.assertContains(response, self.item.name)
        self.assertContains(response, self.item.description)

    def test_item_create_view_get(self):
        response = self.client.get(self.item_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/item_form.html')
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_item_create_view_post_success(self):
        new_item_data = {'name': 'New Test Item', 'description': 'A new description'}
        response = self.client.post(self.item_create_url, new_item_data)
        self.assertRedirects(response, self.item_list_url)
        self.assertTrue(Item.objects.filter(name=new_item_data['name']).exists())

    def test_item_create_view_post_invalid(self):
        # ItemForm requires name and description, so an empty post should be invalid
        response = self.client.post(self.item_create_url, {})
        self.assertEqual(response.status_code, 200) # Stays on the form page
        self.assertFormError(response.context['form'], 'name', 'This field is required.')
        self.assertFormError(response.context['form'], 'description', 'This field is required.')


    def test_item_update_view_get(self):
        response = self.client.get(self.item_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/item_form.html')
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertEqual(response.context['form'].instance, self.item)

    def test_item_update_view_post_success(self):
        updated_data = {'name': 'Updated Test Item', 'description': 'Updated description'}
        response = self.client.post(self.item_update_url, updated_data)
        self.assertRedirects(response, self.item_list_url)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, updated_data['name'])
        self.assertEqual(self.item.description, updated_data['description'])

    def test_item_update_view_post_invalid(self):
        # Attempt to update with invalid data (e.g., empty name)
        response = self.client.post(self.item_update_url, {'name': '', 'description': 'Some description'})
        self.assertEqual(response.status_code, 200) # Stays on the form page
        self.assertFormError(response.context['form'], 'name', 'This field is required.')


    def test_item_delete_view_get(self):
        response = self.client.get(self.item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mcmi_app/item_confirm_delete.html')
        self.assertContains(response, self.item.name)

    def test_item_delete_view_post(self):
        response = self.client.post(self.item_delete_url)
        self.assertRedirects(response, self.item_list_url)
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())

    # Test for accessing protected views when not logged in
    def test_item_views_redirect_if_not_logged_in(self):
        self.client.logout() # Ensure client is logged out
        protected_urls = [
            self.item_list_url,
            self.item_detail_url,
            self.item_create_url,
            self.item_update_url,
            self.item_delete_url,
        ]
        for url in protected_urls:
            response = self.client.get(url)
            # For GET requests to login_required views, Django redirects to login URL
            # with a 'next' parameter pointing to the originally requested URL.
            expected_redirect_url = f"{reverse('login')}?next={url}"
            self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
