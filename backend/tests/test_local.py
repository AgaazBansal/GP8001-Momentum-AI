import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import httpx
from groq import AuthenticationError
from fastapi.testclient import TestClient
from backend import main

class LocalTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.key_patch = patch.object(main, 'groq_client', None)
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)
        self.demo_patch = patch.object(main.settings, 'demo_mode', True)
        self.demo_patch.start()
        self.addCleanup(self.demo_patch.stop)

    def test_no_keys_startup_transcript_chat_and_optional_export(self):
        self.assertEqual(self.client.get('/').json()['mode'], 'demo')
        transcript = 'Priya: I will prepare slides by Friday.\nSam: The demo is Monday.'
        minutes = self.client.post('/process-transcript', json={'transcript': transcript})
        self.assertEqual(minutes.status_code, 200)
        self.assertEqual(minutes.json()['transcript'], transcript)
        self.assertEqual(minutes.json()['action_items'], [])
        chat = self.client.post('/chat', json={'transcript': transcript, 'question': 'When are the slides due?'})
        self.assertIn('Friday', chat.json()['answer'])
        payload = minutes.json(); payload.pop('transcript')
        with patch.object(main, 'notion', None):
            self.assertEqual(self.client.post('/export-to-notion', json=payload).status_code, 503)
        self.assertEqual(self.client.post('/process-meeting', files={'file': ('sample.wav', b'not real audio', 'audio/wav')}).status_code, 503)

    def test_input_validation(self):
        self.assertEqual(self.client.post('/process-transcript', json={'transcript': '   '}).status_code, 400)
        self.assertEqual(self.client.post('/process-transcript', json={'transcript': 'x' * 60001}).status_code, 422)
        self.assertEqual(self.client.post('/process-meeting', files={'file': ('empty.wav', b'', 'audio/wav')}).status_code, 400)
        self.assertEqual(self.client.post('/process-meeting', files={'file': ('bad.txt', b'hello', 'text/plain')}).status_code, 400)
        self.assertEqual(self.client.post('/process-meeting', files={'file': ('big.wav', b'x' * (main.MAX_FILE_SIZE + 1), 'audio/wav')}).status_code, 413)

    def test_cloud_audio_and_json_normalization_with_mock_provider(self):
        groq = Mock()
        groq.audio.transcriptions.create.return_value.text = 'Priya will prepare slides by Friday.'
        groq.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({
            'overall_sentiment': 'Neutral', 'topics': ['Launch'],
            'discussion_points': [{'topic': 'Launch', 'summary': 'Slides due Friday.'}],
            'action_items': [{'task': 'Prepare slides', 'owner': 'Priya', 'deadline': 'Friday'}]
        })))])
        with patch.object(main, 'groq_client', groq):
            result = self.client.post('/process-meeting', files={'file': ('sample.wav', b'audio', 'audio/wav')})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['action_items'][0]['owner'], ['Priya'])
        self.assertEqual(groq.chat.completions.create.call_args.kwargs['model'], main.settings.summary_model)
        self.assertEqual(groq.chat.completions.create.call_args.kwargs['response_format'], {'type': 'json_object'})

    def test_bad_key_reports_fix(self):
        groq = Mock()
        response = httpx.Response(401, request=httpx.Request('POST', 'https://api.groq.com'))
        groq.chat.completions.create.side_effect = AuthenticationError('Invalid key', response=response, body={})
        with patch.object(main, 'groq_client', groq):
            result = self.client.post('/process-transcript', json={'transcript': 'Meeting notes.'})
        self.assertEqual(result.status_code, 502)
        self.assertIn('Replace GROQ_API_KEY', result.json()['detail'])

    def test_disabled_demo_does_not_silently_fake_output(self):
        with patch.object(main.settings, 'demo_mode', False):
            result = self.client.post('/process-transcript', json={'transcript': 'Meeting notes.'})
        self.assertEqual(result.status_code, 503)

if __name__ == '__main__':
    unittest.main()
