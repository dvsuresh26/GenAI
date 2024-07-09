from fastapi import FastAPI
import uvicorn

app=FastAPI()
articles=[

    {"id":1,"title":"How to reset your password","content":"To reset your password..."},
    {"id":2,"title":"How to change your email address","content":"To change your email address..."},
]
@app.get("/search/")
async def search_articles(query :str):
    return [article['content'] for article in articles if query.lower() in article['title'].lower()]

@app.get("/articles/{article_id}")
async def get_article(article_id:int):
    return next((article for article in articles if article['id'] == article_id), {})

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8081)