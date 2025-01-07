# API References

## Notion API

### Official Documentation
- Main Documentation: https://developers.notion.com/docs
- API Reference: https://developers.notion.com/reference/intro
- Authentication: https://developers.notion.com/docs/authorization
- Rate Limits: https://developers.notion.com/reference/request-limits

### Important Endpoints
- Database Query: https://developers.notion.com/reference/post-database-query
- Create Page: https://developers.notion.com/reference/post-page
- Update Page: https://developers.notion.com/reference/patch-page

### Rate Limits
- 3 requests per second (averaged over 1 minute)
- 90 requests per minute per integration
- 1000 blocks per page

## Telegram Bot API

### Official Documentation
- Main Documentation: https://core.telegram.org/bots/api
- WebHooks: https://core.telegram.org/bots/webhooks
- Long Polling: https://core.telegram.org/bots/api#getupdates

### Important Methods
- sendMessage: https://core.telegram.org/bots/api#sendmessage
- editMessageText: https://core.telegram.org/bots/api#editmessagetext
- answerCallbackQuery: https://core.telegram.org/bots/api#answercallbackquery

### Rate Limits
- 30 messages per second to different chats
- 1 message per second to same chat
- 20 messages per minute to same chat for same content

## Python Libraries

### python-telegram-bot
- Documentation: https://docs.python-telegram-bot.org/
- GitHub: https://github.com/python-telegram-bot/python-telegram-bot
- Version: 20.7 (Latest stable)

### notion-client
- Documentation: https://ramnes.github.io/notion-sdk-py/
- GitHub: https://github.com/ramnes/notion-sdk-py
- Version: 2.2.1 (Latest stable)

## Error Codes

### Notion API Error Codes
- 400: Invalid request
- 401: Invalid authentication
- 403: Forbidden (insufficient permissions)
- 404: Resource not found
- 429: Rate limited

### Telegram API Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 429: Too Many Requests