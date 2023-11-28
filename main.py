from sanic import Sanic
from sanic import HTTPResponse
from sanic import response
from sanic import Request
from aiohttp import ClientSession


async def search(query: str, limit: int) -> dict:
    async with ClientSession() as session:
        async with session.request(
            method="GET",
            url="https://unsplash.com/napi/search/photos",
            params={"per_page": limit, "query": query, "page": 1},
        ) as response:
            if response.ok is True:
                json = await response.json()
                results = json["results"]
                urls = []

                for result in results[: int(limit)]:
                    urls.append(result["urls"]["full"])

                return {"success": True, "urls": urls, "status": 200}

            else:
                return {
                    "success": False,
                    "error": {
                        "type": "internal_error",
                        "message": "We had an internal error when sending a request to a resource",
                        "status": 500,
                    },
                }


server = Sanic(name="duckapi-no-shitcode")


@server.route(uri="/browse")
async def browse(request: Request) -> HTTPResponse:
    if "query" not in request.get_args().keys():
        return response.json(
            body={
                "success": False,
                "error": {
                    "type": "parameter_missing",
                    "message": "Required parameter 'query' is missing",
                    "status": 400,
                },
            },
            status=400,
        )

    query = request.get_args().get("query")
    limit = request.get_args().get("limit", 1)

    if limit.isdigit() is False or (limit.isdigit() and not 1 <= int(limit) <= 150):
        return response.json(
            body={
                "success": False,
                "error": {
                    "type": "invalid_parameter",
                    "message": "Parameter 'limit' must be integer in range 1...150",
                    "status": 400,
                },
            },
            status=400,
        )

    json = await search(query=query, limit=limit)

    return response.json(body=json, status=json.get("status", 200))


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
