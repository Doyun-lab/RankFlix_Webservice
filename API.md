## login

* 기능: 사용자 로그인

* URI
   - IP:port/login

* Client --> Server
  - Format: JSON
  - Example

```python
{
   "user_id": "...",
   "passwd": "..."
}
```

* Server --> Client
  - Format: JSON
  - Example
  
```python
* Success case
{"msg":"","result":true,"session_id":"..."}

* Fail case
{"msg":"...", result":false, "session_id":none}
```

## favorite

* 기능: 선호 콘텐츠 추가 및 List-up

* URI
   - IP:port/favorite

* Client --> Server
  - Format: JSON
  - Example
  
```python
* 선호 콘텐츠 추가하는 경우
{
   "request_type": "add",
   "session_id": "...",
   "favorite": ["...", "...", ...]
}

* 선호 콘텐츠 리스트 얻는 경우
{
   "request_type": "get",
   "session_id": "..."
}
```

* Server --> Client
  - Format: JSON
  - Example
  
```python
* 선호 콘텐츠  추가 성공
{
   "session_id": "...",
   "result": true,
   "msg": ""
}

* 선호 콘텐츠  추가 실패
{
   "session_id": "...",
   "result": false,
   "msg": "..."
}

* 실패 (예: 올바르지 않은 접근)
{
   "result": false,
   "msg": "..."
}

* 선호 콘텐츠  리스트 얻는 경우
{
   "session_id": "...",
   "favorite": ["...", "...", ...]
}
```
![image](https://user-images.githubusercontent.com/70316401/119787184-ec018480-bf0b-11eb-8954-fe387019e8a4.png)

![image](https://user-images.githubusercontent.com/70316401/119786903-9d53ea80-bf0b-11eb-9bca-e8becacf838a.png)
