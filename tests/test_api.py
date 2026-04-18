#!/usr/bin/python
# coding: utf8

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from ebt import Api


class TestApiInit:
    """Tests for API initialization"""
    
    def test_api_initialization(self):
        """Test that Api initializes with correct URL"""
        api = Api()
        assert api.url == "https://api.eurobilltracker.com"
        assert api.user is None


class TestApiLogin:
    """Tests for login functionality"""
    
    @patch('ebt.api.requests.post')
    def test_login_success(self, mock_post):
        """Test successful login"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'sessionid': 'test_session_id',
            'userid': '123'
        }
        mock_post.return_value = mock_response
        
        api.login("test@example.com", "password")
        
        assert api.user is not None
        assert api.user['sessionid'] == 'test_session_id'
        mock_post.assert_called_once()
    
    @patch('ebt.api.requests.post')
    def test_login_failure(self, mock_post):
        """Test login failure with non-200 status"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="Error"):
            api.login("test@example.com", "wrong_password")


class TestApiGet:
    """Tests for GET requests"""
    
    @patch('ebt.api.requests.get')
    def test_get_without_user(self, mock_get):
        """Test GET request without authenticated user"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        result = api.get("test_method", "1")
        
        assert result == {'data': 'test'}
        called_url = mock_get.call_args[0][0]
        assert 'test_method' in called_url
        assert 'v=1' in called_url
        assert 'PHPSESSID' not in called_url
    
    @patch('ebt.api.requests.get')
    def test_get_with_user(self, mock_get):
        """Test GET request with authenticated user"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        result = api.get("test_method", "1")
        
        called_url = mock_get.call_args[0][0]
        assert 'PHPSESSID=test_session_id' in called_url
    
    @patch('ebt.api.requests.get')
    def test_get_with_params(self, mock_get):
        """Test GET request with parameters"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        result = api.get("test_method", "1", {"param1": "value1", "param2": "value2"})
        
        called_url = mock_get.call_args[0][0]
        assert 'param1=value1' in called_url
        assert 'param2=value2' in called_url
    
    @patch('ebt.api.requests.get')
    def test_get_with_json_decode_error(self, mock_get):
        """Test GET request handling JSON decode error"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        mock_response._content = b'{"data": "test"}'
        mock_get.return_value = mock_response
        
        result = api.get("test_method", "1")
        
        assert result == {'data': 'test'}
    
    @patch('ebt.api.requests.get')
    def test_get_failure(self, mock_get):
        """Test GET request failure"""
        api = Api()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Error"):
            api.get("test_method", "1")


class TestApiLogout:
    """Tests for logout functionality"""
    
    @patch('ebt.api.requests.get')
    def test_logout(self, mock_get):
        """Test logout call"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_get.return_value = mock_response
        
        result = api.logout()
        
        assert result == {'status': 'success'}
        called_url = mock_get.call_args[0][0]
        assert 'logout' in called_url


class TestApiCities:
    """Tests for city-related methods"""
    
    @patch('ebt.api.requests.get')
    def test_get_cities(self, mock_get):
        """Test getting cities"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'city': 'Paris'}, {'city': 'London'}]}
        mock_get.return_value = mock_response
        
        result = api.get_cities()
        
        assert result == {'data': [{'city': 'Paris'}, {'city': 'London'}]}
        called_url = mock_get.call_args[0][0]
        assert 'mycities' in called_url


class TestApiNote:
    """Tests for note-related methods"""
    
    @patch('ebt.api.requests.get')
    def test_get_note(self, mock_get):
        """Test getting a specific note"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'note_id': '123', 'value': 5}}
        mock_get.return_value = mock_response
        
        result = api.get_note('123')
        
        assert result == {'note_id': '123', 'value': 5}
        called_url = mock_get.call_args[0][0]
        assert 'globalstats_profile_note' in called_url
        assert 'note_id=123' in called_url
    
    @patch('ebt.api.requests.get')
    def test_insert_note(self, mock_get):
        """Test inserting a new note"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_get.return_value = mock_response
        
        result = api.insert_note(
            country="France",
            city="Paris",
            zip_code="75001",
            value=5,
            short_code="FR",
            serial_number="ABC123",
            comment="Test note"
        )
        
        assert result == {'status': 'success'}
        called_url = mock_get.call_args[0][0]
        assert 'insertbills' in called_url
        assert 'country=France' in called_url
        assert 'city=Paris' in called_url


class TestApiUser:
    """Tests for user-related methods"""
    
    @patch('ebt.api.requests.get')
    def test_get_user(self, mock_get):
        """Test getting a specific user"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'user_id': '123', 'name': 'John'}}
        mock_get.return_value = mock_response
        
        result = api.get_user('123')
        
        assert result == {'user_id': '123', 'name': 'John'}
        called_url = mock_get.call_args[0][0]
        assert 'globalstats_profile_user' in called_url
        assert 'user_id=123' in called_url


class TestApiZipcodes:
    """Tests for zipcode-related methods"""
    
    @patch('ebt.api.requests.get')
    def test_get_zipcodes(self, mock_get):
        """Test getting zipcodes for a city"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': ['75001', '75002', '75003']}
        mock_get.return_value = mock_response
        
        result = api.get_zipcodes('Paris', 'France', 'Central')
        
        assert result == {'data': ['75001', '75002', '75003']}
        called_url = mock_get.call_args[0][0]
        assert 'myzipcodes' in called_url
        assert 'city=Paris' in called_url
        assert 'country=France' in called_url
        assert 'comment=Central' in called_url


class TestApiSearch:
    """Tests for search functionality"""
    
    @patch('ebt.api.requests.get')
    def test_search_basic(self, mock_get):
        """Test basic search"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'result': 'item1'}]}
        mock_get.return_value = mock_response
        
        result = api.search('test')
        
        assert result == {'data': [{'result': 'item1'}]}
        called_url = mock_get.call_args[0][0]
        assert 'search' in called_url
        assert 'find=test' in called_url
    
    @patch('ebt.api.requests.get')
    def test_search_with_type(self, mock_get):
        """Test search with type filter"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        api.search('test', typee=1)
        
        called_url = mock_get.call_args[0][0]
        assert 'what=1' in called_url
    
    @patch('ebt.api.requests.get')
    def test_search_with_limit_and_cursor(self, mock_get):
        """Test search with limit and cursor"""
        api = Api()
        api.user = {'sessionid': 'test_session_id'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        api.search('test', limit=50, cursor=1)
        
        called_url = mock_get.call_args[0][0]
        assert 'pp=50' in called_url
        assert 'c=1' in called_url
