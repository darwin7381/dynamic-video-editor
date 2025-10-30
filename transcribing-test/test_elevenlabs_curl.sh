#!/bin/bash
curl -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: sk_c10b61842ead12201698676af90f1421d5f6e3cd555317ec" \
  -F "file=@multispeaker-test.MP3" \
  -F "model_id=scribe_v1" \
  -o elevenlabs_curl_result.json

echo "結果已保存到 elevenlabs_curl_result.json"
