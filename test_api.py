import pytest
from fastapi.testclient import TestClient
from datetime import time
from unittest.mock import AsyncMock, patch
import httpx

from main import app
from api import merge_overlapping_terms
from schemas import Termin, Predmet, Aktivnost


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        """Test that the health endpoint returns ok status"""
        response = client.get("/bool/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestMergeOverlappingTerms:
    def test_merge_no_overlap(self):
        """Test merging terms with no overlap"""
        terms = [
            Termin(
                termin_id=1,
                zacetek=time(8, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 1",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
            Termin(
                termin_id=2,
                zacetek=time(10, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 2",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
        ]
        result = merge_overlapping_terms(terms)
        assert len(result) == 2
        assert result[0].termin_id == 1
        assert result[1].termin_id == 2

    def test_merge_with_overlap(self):
        """Test merging terms with overlapping time slots - validates current behavior"""
        terms = [
            Termin(
                termin_id=1,
                zacetek=time(8, 0),
                dolzina=90,
                dan=1,
                lokacija="Room 1",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
            Termin(
                termin_id=2,
                zacetek=time(9, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 2",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
        ]
        # The implementation merges overlapping terms into a single term
        result = merge_overlapping_terms(terms)
        assert len(result) == 1
        assert result[0].zacetek == time(8, 0)
        assert result[0].dan == 1

    def test_merge_different_days(self):
        """Test that terms on different days are not merged"""
        terms = [
            Termin(
                termin_id=1,
                zacetek=time(8, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 1",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
            Termin(
                termin_id=2,
                zacetek=time(8, 0),
                dolzina=60,
                dan=2,
                lokacija="Room 2",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
        ]
        result = merge_overlapping_terms(terms)
        assert len(result) == 2

    def test_merge_empty_list(self):
        """Test merging empty list of terms"""
        result = merge_overlapping_terms([])
        assert result == []

    def test_merge_single_term(self):
        """Test merging single term"""
        terms = [
            Termin(
                termin_id=1,
                zacetek=time(8, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 1",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            )
        ]
        result = merge_overlapping_terms(terms)
        assert len(result) == 1
        assert result[0].termin_id == 1

    def test_merge_multiple_overlaps(self):
        """Test merging multiple overlapping terms - validates current behavior"""
        terms = [
            Termin(
                termin_id=1,
                zacetek=time(8, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 1",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
            Termin(
                termin_id=2,
                zacetek=time(8, 30),
                dolzina=60,
                dan=1,
                lokacija="Room 2",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
            Termin(
                termin_id=3,
                zacetek=time(9, 0),
                dolzina=60,
                dan=1,
                lokacija="Room 3",
                tip="lecture",
                predmet=None,
                aktivnost=None,
            ),
        ]
        # The implementation merges all overlapping terms into a single term
        result = merge_overlapping_terms(terms)
        assert len(result) == 1
        assert result[0].zacetek == time(8, 0)
        assert result[0].dan == 1


class TestBoolEndpoint:
    def test_bool_endpoint_validation(self):
        """Test the bool endpoint requires proper query parameters"""
        # Test without required parameters - the endpoint is at /bool/ not /bool/get
        response = client.get("/bool/")
        assert response.status_code == 422
        
    @patch('api.httpx.AsyncClient')
    def test_bool_endpoint_with_params(self, mock_client):
        """Test the bool endpoint with query parameters in correct format"""
        # Create a mock response object (not async)
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'termini': []}
        
        # Create async client mock
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_async_client
        mock_async_client.get.return_value = mock_response
        mock_client.return_value = mock_async_client
        
        # The GetCombined model expects user_ids as a list
        # FastAPI GET endpoints with Pydantic models expect JSON body
        response = client.request('GET', '/bool/', json={'user_ids': [1, 2]})
        # Should succeed with mocked external service
        assert response.status_code == 200
