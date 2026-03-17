
# webhook 
PS C:\Users\user\Documents\GitHub\gamyeon-AI> uv run python callback_receiver.py

# question - test 
```
{
  "intvId": 123,
  "files": [
    {
      "fileType": "RESUME",
      "fileKey": "sample/resume.pdf"
    }
  ],
  "callback": "http://127.0.0.1:9000/internal/v1/questions/callback"
}

```

```
{
  "resume_url": "sample/resume.pdf",
  "portfolio_url": null,
  "self_introduction_url": null,
  "job_role": "백엔드 개발자"
}

{
  "resume_url": "https://gamyeon-s3-bucket.s3.ap-northeast-2.amazonaws.com/resume.pdf",
  "portfolio_url": null,
  "self_introduction_url": null,
  "job_role": "백엔드 개발자"
}
```
# feedback - test
```
{
  "intv_question_id": 101,
  "question_content": "본인의 강점에 대해 설명해주세요.",
  "corrected_transcript": "제 강점은 문제 해결 능력입니다. 프로젝트 진행 시 협업을 통해 효율적인 결과를 만들어냅니다.",
  "degraded": false,
  "reliability_score": 95,
  "gaze_score": 88,
  "time_score": 92,
  "answer_duration_ms": 45000,
  "keyword_candidates": [
    {
      "term": "문제 해결",
      "count": 1,
      "category": "역량"
    },
    {
      "term": "협업",
      "count": 1,
      "category": "태도"
    }
  ]
}
```