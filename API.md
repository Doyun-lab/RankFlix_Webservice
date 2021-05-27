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
![image](https://user-images.githubusercontent.com/70316401/119786903-9d53ea80-bf0b-11eb-9bca-e8becacf838a.png)
