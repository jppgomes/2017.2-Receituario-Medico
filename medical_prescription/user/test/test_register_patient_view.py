# Standard library
import hashlib
import random
import datetime

# Django imports
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from user.models import Patient, SendInvitationProfile
from django.contrib.messages.storage.fallback import FallbackStorage

# Local django imports
from user.views import RegisterPatientView


class RegisterPatientViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email = 'teste@teste.com'
        self.salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        self.activation_key = hashlib.sha1(str(self.salt+self.email).encode('utf‌​-8')).hexdigest()
        self.key_expires = datetime.datetime.today() + datetime.timedelta(2)
        self.key_expired = datetime.datetime.today() - datetime.timedelta(2)
        self.patient = Patient(email=self.email)
        self.patient.save()
        self.patient_profile = SendInvitationProfile.objects.create(activation_key=self.activation_key,
                                                                    patient=self.patient,
                                                                    key_expires=self.key_expires)
        self.patient_profile.save()
        self.email_invalid = 'invalid@invalid.com'
        self.another_activation_key = hashlib.sha1(str(self.salt+self.email_invalid).encode('utf‌​-8')).hexdigest()
        self.name_valid = 'Teste Nome'
        self.name_invalid = 'Te'
        self.date_of_birth_valid = '10/12/1990'
        self.phone_valid = '1234567890'

        self.sex_valid = 'M'
        self.id_document_valid = '12345678910'
        self.password_valid = '1234567'
        self.password_invalid = '1'

    def test_get(self):
        request = self.factory.get('user/register_patient/(?P<activation_key>\w+)/')
        request.user = AnonymousUser()

        response = RegisterPatientView.as_view()(request, activation_key=self.activation_key)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        '''
        Test post method with a valid form.
        '''
        # Create the request
        context = {'name': self.name_valid,
                   'phone': self.phone_valid,
                   'email': self.email,
                   'password': self.password_valid,
                   'confirm_password': self.password_valid,
                   'sex': self.sex_valid,
                   'date_of_birth': self.date_of_birth_valid,
                   'id_document': self.id_document_valid}

        request = self.factory.post('/user/register_patient/(?P<activation_key>\w+)/', context)
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        request.user = AnonymousUser()

        # Get the response
        response = RegisterPatientView.as_view()(request, activation_key=self.activation_key)
        self.assertEqual(response.status_code, 302)

    def test_post_invalid(self):
        '''
        Test post method with a valid form.
        '''
        # Create the request
        context = {'name': self.name_invalid,
                   'phone': self.phone_valid,
                   'email': self.email,
                   'password': self.password_invalid,
                   'confirm_password': self.password_valid,
                   'sex': self.sex_valid,
                   'date_of_birth': self.date_of_birth_valid,
                   'id_document': self.id_document_valid}

        request = self.factory.post('/user/register_patient/(?P<activation_key>\w+)/', context)
        request.user = AnonymousUser()
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        # Get the response
        response = RegisterPatientView.as_view()(request, activation_key=self.activation_key)
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_patient_not_invited(self):
        '''
        This method tests when you try to register a not invited patient.
        '''

        # Create the request
        context = {'name': self.name_invalid,
                   'phone': self.phone_valid,
                   'email': self.email,
                   'password': self.password_invalid,
                   'confirm_password': self.password_valid,
                   'sex': self.sex_valid,
                   'date_of_birth': self.date_of_birth_valid,
                   'id_document': self.id_document_valid}

        request = self.factory.post('/user/register_patient/(?P<activation_key>\w+)/', context)
        request.user = AnonymousUser()
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        # Get the response
        response = RegisterPatientView.as_view()(request, activation_key=self.another_activation_key)
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_patient_register_time_expired(self):
        '''
        This method tests when you try to register after the expiration date of the invitation.
        '''
        patient_profile = Patient.objects.get(email=self.email)
        SendInvitationProfile.objects.filter(patient=patient_profile).update(key_expires=self.key_expired)
        # Create the request
        context = {'name': self.name_invalid,
                   'phone': self.phone_valid,
                   'email': self.email,
                   'password': self.password_invalid,
                   'confirm_password': self.password_valid,
                   'sex': self.sex_valid,
                   'date_of_birth': self.date_of_birth_valid,
                   'id_document': self.id_document_valid}

        request = self.factory.post('/user/register_patient/(?P<activation_key>\w+)/', context)
        request.user = AnonymousUser()
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        # Get the response
        response = RegisterPatientView.as_view()(request, activation_key=self.activation_key)
        self.assertEqual(response.status_code, 302)
